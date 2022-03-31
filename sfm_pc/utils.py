import re
import importlib
from collections import namedtuple
import itertools
import json
from io import StringIO, BytesIO
import zipfile
import csv

import pysolr

from reversion.models import Version

from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.urls import reverse


CONFIDENCE_MAP = {
    'low': 1,
    'medium': 2,
    'high': 3,
}

REVERSE_CONFIDENCE = {v:k for k,v in CONFIDENCE_MAP.items()}


class Autofill(object):
    '''
    Helper class for getting attributes that we already know about entities
    based on autocomplete queries.
    '''
    def __init__(self, objects=[], simple_attrs=[], complex_attrs=[],
                 list_attrs=[], set_attrs={}):

        # Model objects that we want to query
        self.objects = objects

        # Simple (non-complex) fields
        self.simple_attrs = simple_attrs

        # Complex single-select fields
        self.complex_attrs = complex_attrs

        # Complex multiselect fields
        self.list_attrs = list_attrs

        # Querysets from foreign key relationships
        # (Requires both the attr name, and the foreign key name,
        # like: {'membershippersonmember_set', 'organization'})
        self.set_attrs = set_attrs

    @property
    def attrs(self):

        collected_attrs = []

        for obj in self.objects:

            obj_data = {
                'text': str(obj.name),
                'id': obj.id
            }

            # Add optional attributes, with confidence values, to the results
            for attr in self.simple_attrs:

                try:
                    val = getattr(obj, attr).get_value()
                except AttributeError:
                    val = None

                if val:
                    if attr.endswith('date'):
                        display_value = repr(val.value)
                    else:
                        display_value = str(val.value)
                    attr_confidence = val.confidence
                else:
                    display_value = ''
                    attr_confidence = '1'

                obj_data[attr] = display_value
                obj_data[attr + '_confidence'] = attr_confidence

            # Differentiate id/text for complex attributes
            for attr in self.complex_attrs:

                try:
                    val = getattr(obj, attr).get_value()
                except AttributeError:
                    val = None

                if val:
                    val_id = val.id
                    val_text = str(val.value)
                    attr_confidence = val.confidence
                else:
                    val_id, val_text = '', ''
                    attr_confidence = '1'

                obj_data[attr] = {}
                obj_data[attr]['id'] = val_id
                obj_data[attr]['text'] = val_text
                obj_data[attr + '_confidence'] = attr_confidence

            # Add optional attributes that are lists
            for attr in self.list_attrs:

                try:
                    lst = getattr(obj, attr).get_list()
                except AttributeError:
                    lst = []

                lst_no_nulls = [inst.get_value() for inst in lst if inst.get_value()]

                if any(lst_no_nulls):
                    lst_confidence = lst_no_nulls[0].confidence
                else:
                    lst_confidence = '1'

                cleaned_lst = []
                for inst in lst_no_nulls:
                    if attr != 'classification':
                        cleaned_lst.append({
                            'id': inst.id,
                            'text': str(inst.value)
                        })
                    else:
                        # For classificaitons, we want to get the Classification
                        # model, not the OrganizationClassification model
                        cleaned_lst.append({
                            'id': inst.value.id,
                            'text': str(inst.value)
                        })

                obj_data[attr] = cleaned_lst
                obj_data[attr + '_confidence'] = lst_confidence

            # Add objects corresponding to foreign keys
            for attr, fkey in self.set_attrs.items():

                try:
                    lst = getattr(obj, attr).all()
                except AttributeError:
                    lst = []

                lst_refs = [getattr(inst.object_ref, fkey) for inst in lst
                            if getattr(inst.object_ref, fkey, None)]

                lst_values = [inst.get_value().value for inst in lst_refs if inst.get_value()]

                # We need to traverse the relationship again due to the particular
                # membership relationships on complex fields
                lst_values = [inst.get_value() for inst in lst_values if inst.get_value()]

                if any(lst_values):
                    lst_confidence = lst_values[0].confidence
                else:
                    lst_confidence = '1'

                cleaned_lst = []
                for inst in lst_values:
                    cleaned_lst.append({
                        'id': inst.id,
                        'text': str(inst.value)
                    })

                obj_data[attr] = cleaned_lst
                obj_data[attr + '_confidence'] = lst_confidence

            collected_attrs.append(obj_data)

        return collected_attrs

class Downloader(object):
    '''
    Helper class for producing CSV-compatible rows of entities and attributes.

    Initialize with an entity type. Returns a ZIP archive as an HttpResponse
    object.
    '''
    def __init__(self, etype):

        try:
            assert etype in ['Person', 'Organization', 'Violation']
        except AssertionError:
            raise AttributeError('Downloader objects must be initialized with' +
                                 ' one of three entity types: "Person", "Violation",' +
                                 ' or "Organization".')

        self.etype = etype

        if self.etype == 'Person':

            self.table_attrs = ['name', 'alias', 'firstciteddate', 'lastciteddate',
                                'membership', 'rank', 'role', 'title']

        elif self.etype == 'Organization':

            self.table_attrs = ['name', 'alias', 'classification', 'parent',
                                'membership', 'site_name', 'firstciteddate',
                                'lastciteddate']

        else:

            self.table_attrs = ['all']

        self.base_fmt = '%s_{table}' % self.etype.lower()
        self.tables = (self.base_fmt.format(table=attr) for attr in self.table_attrs)

        self.query_fmt = '''
            SELECT * FROM {table}
            WHERE {etype}_id = %s
        '''

        self.col_query_fmt = '''
            SELECT * FROM {table}
            LIMIT 0
        '''

    def get_zip(self, ids):

        zipout = BytesIO()

        with zipfile.ZipFile(zipout, 'w') as zf:

            for table in self.tables:

                tablename = table + '_export'

                with connection.cursor() as col_cursor:
                    col_query = self.col_query_fmt.format(table=tablename)
                    col_cursor.execute(col_query)

                    columns = [c[0] for c in col_cursor.description]

                csvfile = StringIO()
                writer = csv.DictWriter(csvfile, fieldnames=columns)
                writer.writeheader()

                row_fmt = {colname: '' for colname in columns}

                for entity_id in ids:

                    query = self.query_fmt.format(etype=self.etype.lower(),
                                                  table=tablename)
                    q_args = [entity_id]

                    with connection.cursor() as cursor:
                        cursor.execute(query, q_args)

                        results_tuple = namedtuple(table, columns)
                        results = [results_tuple(*r) for r in cursor]

                    for res in results:
                        row = {}

                        for colname in columns:
                            row[colname] = getattr(res, colname, '')

                        writer.writerow(row)

                csvfile.seek(0)
                zf.writestr('{0}.csv'.format(table), csvfile.getvalue())

            # Get sources
            src_query = '''
                SELECT * FROM source_source
            '''

            with connection.cursor() as src_cursor:
                src_cursor.execute(src_query)

                src_cols = [c[0] for c in src_cursor.description]
                src_tuple = namedtuple('sources', src_cols)
                src_results = [src_tuple(*r) for r in src_cursor]

            csvfile = StringIO()
            writer = csv.DictWriter(csvfile, fieldnames=src_cols)
            writer.writeheader()

            for res in src_results:
                row = {}

                for colname in src_cols:
                    row[colname] = getattr(res, colname, '')

                writer.writerow(row)

            csvfile.seek(0)
            zf.writestr('sources.csv', csvfile.getvalue())

        zipout.seek(0)
        return zipout


class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)
    def added(self):
        return self.set_current - self.intersect
    def removed(self):
        return self.set_past - self.intersect
    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])
    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])


class VersionsMixin(object):
    '''
    Model mixin to get version diff for a given model instance
    '''

    def _getDiff(self, differ):

        skip_fields = ['date_updated', 'id']

        def makeIt(change_type):

            for field in getattr(differ, change_type)():

                if field not in skip_fields:

                    if change_type == 'changed':
                        yield {
                            'field_name': field,
                            'to': differ.current_dict[field],
                            'from': differ.past_dict[field],
                        }
                    elif change_type == 'added':
                        yield {
                            'field_name': field,
                            'to': differ.current_dict[field],
                            'from': None
                        }
                    elif change_type == 'removed':
                        yield {
                            'field_name': field,
                            'to': None,
                            'from': differ.past_dict[field]
                        }

        additions = [a for a in makeIt('added')]
        changes = [c for c in makeIt('changed')]
        removals = [r for r in makeIt('removed')]

        return additions, changes, removals

    def getRevisions(self, versions):
        from source.models import Source, AccessPoint

        revisions = []

        for version in versions:

            complete_revision = {
                'id': version.revision.id
            }

            revision_meta = {
                'modification_date': version.revision.date_created,
                'comment': version.revision.comment,
                'user': version.revision.user,
            }

            complex_list_models = [c.field_model._meta.model_name for c in getattr(self, 'complex_lists', [])]

            for object_property in version.revision.version_set.all():

                if object_property.object != self or isinstance(self, Source):

                    serialized_data = json.loads(object_property.serialized_data)[0]

                    # a bit of a hack in order to get sources and access points
                    # to work
                    field_names = []
                    if 'value' in serialized_data['fields']:
                        field_names.append((serialized_data['fields']['value'],
                                            serialized_data['model'].split('.')[1]))
                    else:
                        for field in serialized_data['fields']:
                            field_names.append((serialized_data['fields'][field], field))

                    for value, field_name in field_names:
                        if field_name in complex_list_models:
                            try:
                                complete_revision[field_name].add(value)
                            except KeyError:
                                complete_revision[field_name] = {value}

                        else:
                            complete_revision[field_name] = value

            revisions.append((complete_revision, version.revision))

        return revisions

    def getDifferences(self, revisions):
        differences = []

        for index, (version, revision) in enumerate(revisions):
            if (index - 1) > 0:
                try:
                    previous, previous_revision = revisions[index - 1]
                except (IndexError, AssertionError):
                    continue
            else:
                continue

            differ = DictDiffer(previous, version)

            fields_added, fields_changed, fields_removed = self._getDiff(differ)

            diff = {
                'modification_date': previous_revision.date_created,
                'comment': previous_revision.comment,
                'user': previous_revision.user,
                'from_id': version['id'],
                'to_id': previous_revision.id,
                'fields_added': fields_added,
                'fields_changed': fields_changed,
                'fields_removed': fields_removed,
                'model': self._meta.object_name,
            }

            differences.append(diff)

        return differences

    def getVersions(self, versions=None):

        if not versions:
            versions = Version.objects.get_for_object(self)

        revisions = self.getRevisions(versions)

        return self.getDifferences(revisions)


def execute_sql(file_path):
    '''
    Execute arbitrary SQL code from a file location.
    '''
    with open(file_path) as f:
        statements = f.read().split(';')

        with connection.cursor() as c:
            for statement in statements:
                if statement.strip():
                    c.execute(statement.strip())

def class_for_name(class_name, module_name="person.models"):
    # Check for irregular class names (names where we cannot infer the class
    # name by capitalizing the first letter of class_name)
    irregular_names = (
        ('Membershipperson', 'MembershipPerson'),
        ('Membershiporganization', 'MembershipOrganization'),
        ('Personextra', 'PersonExtra'),
        ('Personbiography', 'PersonBiography')
    )
    for name, formatted_name in irregular_names:
        if class_name == name:
            class_name = formatted_name
            break

    if class_name not in settings.ALLOWED_CLASS_FOR_NAME:
        raise Exception("Unallowed class for name")
    module = importlib.import_module(module_name)
    class_ = getattr(module, class_name)
    return class_

def get_osm_by_id(osm_id):

    osm_feature = None
    cursor = connection.cursor()

    query = '''
        SELECT
          ST_X(ST_Centroid(geometry)),
          ST_Y(ST_Centroid(geometry)),
          *
        FROM osm_data
        WHERE id = {osm_id}
    '''.format(osm_id=osm_id)

    cursor.execute(query)

    columns = [c[0] for c in cursor.description]
    results_tuple = namedtuple('OSMFeature', columns)

    row = cursor.fetchone()

    if row:
        osm_feature = results_tuple(*row)

    return osm_feature

def get_hierarchy_by_id(osm_id):
    hierarchy = '''
        SELECT parents.*
        FROM osm_data AS parents
        JOIN (
          SELECT
            UNNEST(hierarchy) AS h_id,
            localname,
            tags,
            admin_level,
            name,
            geometry
          FROM osm_data
          WHERE id = %s
        ) AS child
          ON parents.id = child.h_id::integer
    '''

    cursor = connection.cursor()
    cursor.execute(hierarchy, [osm_id])

    columns = [c[0] for c in cursor.description]
    results_tuple = namedtuple('OSMFeature', columns)

    hierarchy = [results_tuple(*r) for r in cursor]

    return hierarchy

def generate_hierarchy(query, q_args, rel_field, sources=False):

    cursor = connection.cursor()
    cursor.execute(query, q_args)

    columns = [c[0] for c in cursor.description]
    results_tuple = namedtuple('Organization', columns)

    hierarchy = [(idx, results_tuple(*r)) for idx, r in enumerate(cursor)]

    trimmed_hierarchy = []

    for org_id, orgs in itertools.groupby(hierarchy, key=lambda x: x[1].id):
        group = list(orgs)

        lowest_index = min(g[0] for g in group)
        orgs = [o[1] for o in group]

        start_date = None
        if orgs[0].start_date:
            start_date = orgs[0].start_date

        end_date = None
        if orgs[0].end_date:
            end_date = orgs[0].end_date

        # Create a label, which we display on the charts for person and unit "parents."
        label = '<b>' + orgs[0].name + '</b>' + '\n\n' + _('Unknown commander')
        if orgs[0].commander:
            label = '<b>' + orgs[0].name + '</b>' + '\n\n' + orgs[0].commander

        trimmed = {
            'id': org_id,
            'label': str(label),
            'detail_id': str(orgs[0].org_org_id),
            'name': orgs[0].name,
            'other_names': list({o.alias.strip() for o in orgs if o.alias}),
            'classifications': list({o.classification.strip() for o in orgs if o.classification}),
            'division_id': orgs[0].division_id,
            'date_first_cited': start_date,
            'date_last_cited': end_date,
            'commander': orgs[0].commander,
        }

        trimmed[rel_field] = getattr(orgs[0], rel_field)

        if sources:
            trimmed['sources'] = []

            source_ids = []
            for o in orgs:
                org_source = json.loads(o.source)

                if org_source['id'] not in source_ids:

                    trimmed['sources'].append(org_source)
                    source_ids.append(org_source['id'])

            trimmed['confidence'] = REVERSE_CONFIDENCE[int(orgs[0].confidence)].title()

        trimmed_hierarchy.append((lowest_index, trimmed))

    hierarchy = [i[1] for i in sorted(trimmed_hierarchy, key=lambda x: x[0])]

    return hierarchy

# this makes an edge list that shows the parent relationships (see child_id)

solr = pysolr.Solr(settings.SOLR_URL)


def get_org_hierarchy_by_id(org_id,
                            when=None,
                            sources=False,
                            direction='up',
                            authenticated=False):
    '''
    org_id: uuid for the organization
    when: date for limiting the search
    '''

    base_url = settings.SOLR_URL

    if direction == 'up':
        from_ = 'child'
        to = 'parent'
    elif direction == 'down':
        from_ = 'parent'
        to = 'child'

    filter_query = '{!graph from=composition_%s_id_s_fct to=composition_%s_id_s_fct returnRoot=true}composition_%s_id_s_fct:%s' % (from_, to, from_, org_id)

    if when:
        filter_query += ' AND {!field f=composition_daterange_dr op=contains}%s' % when

    if not authenticated:
        filter_query += ' AND published_b:T'

    results = solr.search('*:*', fq=filter_query)

    if when:
        for result in results:
            for key in [from_, to]:
                org = result['composition_{}_id_s_fct'.format(key)]
                args =  (org, when)
                query = 'commander_org_id_s_fct:%s AND {!field f=commander_assignment_range_dr op=contains}%s' % args

                if not authenticated:
                    query += ' AND published_b:T'

                commanders = solr.search(query)

                # We need to deduplicate commanders and then throw out the open ended date ranges.

                result['commanders-{}'.format(key)] = []

                for commander in commanders:
                    label_fmt = '{name} ({start} - {end})'
                    assignment_range = commander['commander_assignment_range_dr']
                    start, end = assignment_range.replace('[', '').replace(']', '').split(' TO ')

                    if start == '*':
                        start = '?'
                    if end == '*':
                        end = '?'

                    label = label_fmt.format(name=commander['commander_person_name_s'],
                                            start=start,
                                            end=end)

                    commander['label'] = label
                    result['commanders-{}'.format(key)].append(commander)

    return results

def get_child_orgs_by_id(org_id, when=None, sources=False):
    hierarchy = '''
        WITH RECURSIVE parents AS (
          SELECT
            o.*,
            NULL::VARCHAR AS parent_id,
            NULL::VARCHAR AS parent_name,
            NULL::DATE AS start_date,
            NULL::DATE AS end_date,
            NULL::VARCHAR AS comp_open_ended,
            NULL::VARCHAR AS source,
            NULL::VARCHAR AS confidence
          FROM organization As o
          WHERE id = %s
          UNION
          SELECT
            o.*,
            h.parent_id::VARCHAR AS parent_id,
            parents.name AS parent_name,
            h.start_date::date,
            h.end_date::date,
            h.open_ended AS comp_open_ended,
            row_to_json(ss.*)::VARCHAR AS source,
            ccc.confidence
          FROM organization AS o
          JOIN composition AS h
            ON o.id = h.child_id
          JOIN composition_compositionchild AS ccc
            ON h.id = ccc.object_ref_id
          LEFT JOIN composition_compositionchild_sources AS cccs
            ON ccc.id = cccs.compositionchild_id
          LEFT JOIN source_source AS ss
            ON cccs.source_id = ss.uuid
          JOIN parents
            ON parents.id = h.parent_id
        ) SELECT * FROM parents WHERE id != %s
    '''

    q_args = [org_id, org_id]
    if when:
        hierarchy = '''
            {}
            AND CASE
              WHEN (start_date IS NOT NULL AND
                    end_date IS NOT NULL AND
                    comp_open_ended IN ('N', 'E'))
              THEN (%s::date BETWEEN start_date::date AND end_date::date)
              WHEN (start_date IS NOT NULL AND
                    end_date IS NOT NULL AND
                    comp_open_ended = 'Y')
              THEN (%s::date BETWEEN start_date::date AND NOW()::date)
              WHEN (start_date IS NOT NULL AND
                    end_date IS NULL AND
                    comp_open_ended IN ('N', 'E'))
              THEN (start_date::date = %s::date)
              WHEN (start_date IS NOT NULL AND
                    end_date IS NULL AND
                    comp_open_ended = 'Y')
              THEN (%s::date BETWEEN start_date::date AND NOW()::date)
              WHEN (start_date IS NULL AND
                    end_date IS NOT NULL AND
                    comp_open_ended IN ('N', 'E'))
              THEN (end_date::date = %s)
              WHEN (start_date IS NULL AND
                    end_date IS NOT NULL AND
                    comp_open_ended = 'Y')
              THEN TRUE
            END
        '''.format(hierarchy)
        q_args.extend([when] * 5)


    hierarchy = '{} ORDER BY id'.format(hierarchy)

    hierarchy = generate_hierarchy(hierarchy, q_args, 'parent_id', sources=sources)

    return hierarchy


def deleted_in_str(objects):
    index = 0
    for obj in objects:
        if isinstance(obj, list):
            objects[index] = deleted_in_str(obj)

        else:
            if hasattr(obj, 'field_name'):
                name = obj.field_name + ": " + str(obj)
            else:
                name = type(obj).__name__ + ": " + str(obj)
            if '_sources' in name:
                objects[index] = "Object sources"
            else:
                objects[index] = name
        index += 1

    return objects


def import_class(cl):
    d = cl.rfind('.')
    classname = cl[d+1:len(cl)]
    m = __import__(cl[0:d], globals(), locals(), [classname])
    return getattr(m, classname)


def format_facets(facet_dict):
    '''
    pysolr formats facets in a weird way. This helper function converts their
    list-like data structure into a dict that we can iterate more easily.

    Basic idea: convert counts from a list to a dict containing a list of tuples
    and a flag for whether any facets were found, e.g.:

    ['foo', 1, 'bar', 2] --> {'any': True, 'counts': [('foo', 1), ('bar': 2)]}
    '''
    facet_types = ['facet_queries', 'facet_fields', 'facet_ranges',
                   'facet_heatmaps', 'facet_intervals']

    out = {}

    for ftype, facets in facet_dict.items():
        updated_facets = {}
        for facet, items in facets.items():
            if isinstance(items, dict):
                # Ranges have a slightly different format
                item_list = items['counts']
            else:
                item_list = items

            counts = []
            for i, el in enumerate(item_list):
                # The attribute name always comes first; use them as keys
                if i % 2 == 0:
                    count = item_list[i+1]
                    counts.append((el, count))
                else:
                    # We already bunched this one, so skip it
                    continue

            updated_facets[facet] = {}
            updated_facets[facet]['counts'] = counts

            # Check to see if there are any facets in this category
            any_facets = sum(count[1] for count in counts) > 0
            updated_facets[facet]['any'] = any_facets
        out[ftype] = updated_facets

    return out


def get_command_edges(org_id, when=None, parents=True):

    edges = []
    if parents:
        hierarchy_list = get_org_hierarchy_by_id(org_id, when=when)
        from_key, to_key = 'id', 'child_id'
    else:
        hierarchy_list = get_child_orgs_by_id(org_id, when=when)
        from_key, to_key = 'parent_id', 'id'

    # Iterate over the hierarchy_list, and create nodes
    for org in hierarchy_list:
        edges.append({'from': str(org[from_key]), 'to': org[to_key]})

    return edges


def get_command_nodes(org_id, when=None):
    hierarchy_list = get_org_hierarchy_by_id(org_id, when=when)
    # Iterate over the hierarchy_list, and convert/modify hierarchy object, as needed.
    nodes = []
    for org in hierarchy_list:
        trimmed = {
            'id': str(org['id']),
            'label': org['label'],
            'detail_id': org['detail_id']
        }
        nodes.append(trimmed)

    return nodes


def get_source_context(field_name, access_point, uncommitted=True):
    context = {
        'field_name': field_name,
        'uncommitted': uncommitted,
        'id': access_point.uuid,
        'publication': access_point.source.publication,
        'publication_country': access_point.source.publication_country,
        'title': access_point.source.title,
        'date_added': None,
        'published_on': str(access_point.source.published_date),
        'access_point': str(access_point),
        'source_url': access_point.source.source_url,
        'source_detail_url': reverse('view-source', kwargs={'pk': access_point.source.uuid}),
        'archive_url': access_point.archive_url,
        'source_id': access_point.source.uuid,
        'page_number': access_point.trigger,
        'accessed_on': None,
    }

    if access_point.source.date_added:
        context['date_added'] = access_point.source.date_added.strftime('%Y-%m-%d')

    if access_point.accessed_on:
        context['accessed_on'] = access_point.accessed_on.strftime('%Y-%m-%dT%H:%M:%S')

    return context
