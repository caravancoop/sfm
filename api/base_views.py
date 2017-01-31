from datetime import datetime
import json
import itertools

from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView
from django.db import connection

from sfm_pc.utils import get_org_hierarchy_by_id, REVERSE_CONFIDENCE
from sfm_pc.base_views import CacheMixin

OPERATOR_LOOKUP = {
    'lte': '<=',
    'gte': '>=',
    'eq': '=',
    'in': 'IN',
}


class ValidationError(Exception):
    def __init__(self, message):
        self.message = message


def dateValidator(value):
    try:
        datetime.strptime(value, '%Y-%m-%d')
    except ValueError:
        raise ValidationError('Incorrect date format. Should be YYYY-MM-DD.')


def integerValidator(value):
    try:
        int(value)
    except ValueError:
        raise ValidationError('{} is not an integer'.format(value))


class JSONResponseMixin(object):
    def render_to_json_response(self, context, **response_kwargs):
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        try:
            del context['view']
        except (KeyError, TypeError):
            pass
        # Make sure things are JSON serializable
        return context

class NotImplementedView(JSONResponseMixin, TemplateView):
    def dispatch(self, request, *args, **kwargs):
        response = HttpResponse({'status': 'ok', 'message': 'Endpoint not implemented yet'},
                                content_type='application/json')
        response.status_code = 204
        return response


class JSONAPIView(JSONResponseMixin, TemplateView, CacheMixin):
    safe = True
    page_count = 20
    having_fields = {}
    filter_fields = {}
    order_by_fields = {}
    required_params = []
    optional_params = []

    def dispatch(self, request, *args, **kwargs):
        errors = []
        self.wheres = []
        self.having = []
        self.order_bys = []

        filter_fields = list(getattr(self, 'filter_fields', {}).keys())
        having_fields = list(getattr(self, 'having_fields', {}).keys())
        order_by_fields = list(getattr(self, 'order_by_fields', {}).keys())
        required_params = getattr(self, 'required_params', [])
        optional_params = getattr(self, 'optional_params', [])

        valid_params = required_params + filter_fields + order_by_fields + optional_params + having_fields

        incoming_params = list(self.request.GET.keys())

        missing = set(required_params) - set(incoming_params)

        if missing:
            if len(missing) > 1:
                errors.append("{} are required fields".format(', '.join(missing)))
            else:
                errors.append('{} is a required field'.format(list(missing)[0]))

        for query_param in self.request.GET.keys():
            try:
                field, operator = query_param.split('__')
            except ValueError:
                field = query_param
                operator = 'eq'

            if field not in valid_params:
                errors.append("'{}' is not a valid query parameter".format(query_param))

            elif not self.checkOperator(field, operator):
                errors.append("Invalid operator for '{1}'".format(operator, field))

            elif field in filter_fields:

                value = self.request.GET[query_param]

                validator = self.filter_fields[field]['validator']

                if validator:
                    try:
                        validator(value)
                        self.wheres.append((field, operator, value,))
                    except ValidationError as e:
                        errors.append("Value for '{0}' is not valid: {1}".format(field, e.message))
                else:
                    self.wheres.append((field, operator, value,))

            elif field in having_fields:

                value = self.request.GET[query_param]

                validator = self.having_fields[field]['validator']

                if validator:
                    try:
                        validator(value)
                        self.having.append((field, operator, value,))
                    except ValidationError as e:
                        errors.append("Value for '{0}' is not valid: {1}".format(field, e.message))
                else:
                    self.having.append((field, operator, value,))

            elif field == 'o':
                value = self.request.GET['o']
                if value not in order_by_fields:
                    errors.append("Cannot order by '{}'".format(value))
                else:
                    sort_order = 'ASC'

                    if value.startswith('-'):
                        sort_order = 'DESC'
                        value = value.strip('-')

                    self.order_bys.append((value, sort_order,))

            elif field == 'p':
                value = self.request.GET['p']
                try:
                    int(value)
                except ValueError:
                    errors.append("'{}' is not a valid page number")

            elif field == 'bbox':
                bbox = self.request.GET['bbox']
                coords = bbox.split(',')

                if len(coords) != 4:
                    errors.append('"bbox" should be a comma separated list of four floats')

                for point in coords:

                    try:
                        float(point)
                    except ValueError:
                        errors.append('"{}" is not a valid value for a bbox'.format(point))

        if errors:
            response = HttpResponse(json.dumps({'errors': errors}),
                                    content_type='application/json')
            response.status_code = 400
        else:
            response = super().dispatch(request, *args, **kwargs)

        return response

    def checkOperator(self, field, operator):
        if field in self.filter_fields:
            if operator not in self.filter_fields[field]['operators']:
                return False
        elif field in self.having_fields:
            if operator not in self.having_fields[field]['operators']:
                return False
        elif operator != 'eq':
            return False

        return True

    def render_to_response(self, context, **response_kwargs):
        response_kwargs.update({'safe': self.safe})
        return self.render_to_json_response(context, **response_kwargs)

    def makeFeature(self, geometry, properties):

        try:
            del properties['location']
        except KeyError:
            pass

        try:
            del properties['geometry']
        except KeyError:
            pass

        try:
            bbox = properties['bbox']
            del properties['bbox']
        except KeyError:
            bbox = None

        feature = {
            'type': 'Feature',
            'id': properties['id'],
            'properties': properties,
            'geometry': geometry,
        }

        if bbox:
            feature['bbox'] = bbox

        return feature

    def splitSources(self, obj):
        prepared_obj = {}

        for k, v in obj.items():

            try:
                first, last = k.rsplit('_', 1)
            except ValueError:
                prepared_obj[k] = v
                continue

            if last not in ['sources', 'value', 'confidence']:
                prepared_obj[k] = v

            else:

                if last == 'sources':
                    sources = []
                    source_ids = []
                    for source in v:
                        if source and source['id'] not in source_ids:
                            sources.append(source)
                            source_ids.append(source['id'])
                    v = sources

                elif last == 'confidence':
                    if v:
                        v = REVERSE_CONFIDENCE[int(v)].title()

                try:
                    prepared_obj[first][last] = v
                except KeyError:
                    prepared_obj[first] = {last: v}

        return prepared_obj

    def makeEntityEvents(self,
                         entity_id,
                         entity_type='organization',
                         bbox=None,
                         when=None):

        q_args = [entity_id]
        nearby_q_args = []

        events_query = '''
            SELECT DISTINCT ON (MAX(o.id::VARCHAR))
              v.id,
              MAX(v.start_date) AS start_date,
              MAX(v.end_date) AS end_date,
              MAX(v.location_description) AS location,
              MAX(v.admin_level_1) AS admin_level_1,
              MAX(v.admin_level_2) AS admin_level_2,
              MAX(v.osmname) AS osm_name,
              MAX(v.osm_id) AS osm_id,
              MAX(v.division_id) AS division_id,
              MAX(v.description) AS description,
              MAX(p.name) AS perpetrator_name,
              array_agg(DISTINCT TRIM(v.perpetrator_classification))
                FILTER (WHERE TRIM(v.perpetrator_classification) IS NOT NULL) AS perpetrator_classification,
              array_agg(DISTINCT TRIM(v.violation_type))
                FILTER (WHERE TRIM(v.violation_type) IS NOT NULL) AS classifications,
              json_agg(row_to_json(o.*)) AS perpetrator_organization,
              ST_ASGeoJSON(MAX(v.location))::json AS location
            FROM violation AS v
            LEFT JOIN person AS p
              ON v.perpetrator_id = p.id
        '''
        if entity_type == 'organization':
            events_query = '''
                {}
                LEFT JOIN organization AS o
                  ON v.perpetrator_organization_id = o.id
            '''.format(events_query)
        elif entity_type == 'person':
            events_query = '''
                {}
                LEFT JOIN person AS o
                  ON v.perpetrator_id = o.id
            '''.format(events_query)

        wheres = '''
            WHERE o.id = %s
        '''

        if when:
            wheres = '''
                {} 
                AND v.start_date::date <= %s 
                AND v.end_date::date >= %s
            '''.format(wheres)
            q_args.extend([when, when])

        if bbox:
            wheres = '''
                {} AND ST_Within(v.location, ST_MakeEnvelope(%s, %s, %s, %s, 4326))
            '''.format(wheres)
            q_args.extend(bbox.split(','))

        nearby_events_query = '''
            {}
            JOIN violation AS center
              ON ST_Intersects(ST_Buffer_Meters(center.location, 35000), v.location)
            WHERE v.id != center.id
        '''.format(events_query)

        if when:
            nearby_events_query = '''
                {} AND center.start_date::date <= %s 
                   AND center.end_date >= %s
            '''.format(nearby_events_query)
            nearby_q_args.extend([when, when])

        nearby_events_query = '{} GROUP BY v.id'.format(nearby_events_query)

        events_query = '''
            {0} {1} GROUP BY v.id
        '''.format(events_query, wheres)

        cursor = connection.cursor()
        cursor.execute(events_query, q_args)
        columns = [c[0] for c in cursor.description]

        events = []
        for event in cursor:
            event = self.makeEvent(dict(zip(columns, event)), simple=True)
            feature = self.makeFeature(event['location'], event)
            events.append(feature)

        del q_args[0]
        
        cursor.execute(nearby_events_query, nearby_q_args)
        columns = [c[0] for c in cursor.description]

        event_ids = [e['id'] for e in events]
        nearby_events = []
        for event in cursor:
            if event[0] not in event_ids:
                event = self.makeEvent(dict(zip(columns, event)), simple=True)
                feature = self.makeFeature(event['location'], event)
                nearby_events.append(feature)

        return events, nearby_events

    def makeOrganizationMembers(self, organization_id):

        members = '''
            SELECT
              p.id,
              MAX(p.name) AS name,
              MAX(m.rank) AS rank,
              MAX(m.role) AS role,
              MAX(m.title) AS title,
              array_agg(DISTINCT TRIM(p.alias))
                FILTER (WHERE TRIM(p.alias) IS NOT NULL) AS other_names,
              COUNT(DISTINCT v.id) AS events_count,
              MAX(m.first_cited::DATE) AS first_cited,
              MAX(m.last_cited::DATE) AS last_cited,
              json_agg(row_to_json(ss.*)) AS sources,
              MAX(mp.confidence) AS confidence
            FROM person AS p
            JOIN membershipperson AS m
              ON p.id = m.member_id
            JOIN membershipperson_membershippersonmember AS mp
              ON m.id = mp.object_ref_id
            LEFT JOIN violation AS v
              ON m.member_id = v.perpetrator_id
            LEFT JOIN membershipperson_membershippersonmember_sources AS mps
              ON m.id = mps.membershippersonmember_id
            LEFT JOIN source_source AS ss
              ON mps.source_id = ss.id
            WHERE m.organization_id = %s
            GROUP BY p.id
        '''

        cursor = connection.cursor()
        cursor.execute(members, [organization_id])

        members = []

        for row in cursor:

            member = {
                'id': row[0],
                'name': row[1],
                'rank': row[2],
                'role': row[3],
                'title': row[4],
                'other_names': row[5],
                'events_count': row[6],
                'first_cited': row[7],
                'last_cited': row[8],
                'sources': [],
                'confidence': row[10]
            }

            source_ids = []

            for source in row[9]:
                if source['id'] not in source_ids:
                    member['sources'].append(source)
                    source_ids.append(source['id'])

            members.append(member)

        return members

    def makeOrganizationRelationships(self, properties):

        hierarchy = get_org_hierarchy_by_id(properties['id'])

        properties['root_name'] = None
        properties['root_id'] = None

        if hierarchy:
            top = hierarchy[-1]
            properties['root_name'] = top['name']
            properties['root_id'] = top['id']

        return properties

    def makeOrganizationCommanders(self, properties):
        commanders = '''
            SELECT * FROM (
              SELECT DISTINCT ON (id)
                *
              FROM (
                SELECT
                  o.id AS organization_id,
                  MAX(p.id::VARCHAR) AS id,
                  MAX(p.name) AS name,
                  m.first_cited AS first_cited,
                  m.last_cited AS last_cited,
                  COUNT(DISTINCT v.id) AS events_count
                FROM organization AS o
                JOIN membershipperson AS m
                  ON o.id = m.organization_id
                JOIN person AS p
                  ON m.member_id = p.id
                LEFT JOIN violation AS v
                  ON p.id = v.perpetrator_id
                WHERE o.id = %s
                  AND m.role = 'Commander'
                GROUP BY o.id, m.first_cited, m.last_cited
                ORDER BY o.id,
                         m.last_cited DESC,
                         m.first_cited DESC
              ) AS s
            ) AS s ORDER BY last_cited DESC, first_cited DESC
        '''

        cursor = connection.cursor()
        cursor.execute(commanders, [properties['id']])
        columns = [c[0] for c in cursor.description]

        row = cursor.fetchone()

        if row:
            properties['commander_present'] = dict(zip(columns, row))
            properties['commanders_former'] = [dict(zip(columns, r)) for r in cursor]
        else:
            properties['commander_present'] = {}
            properties['commanders_former'] = []

        return properties
    
    def makePresentCommander(self, properties):
        when = self.request.GET.get('at', datetime.now().date().isoformat())
        
        commander = '''
            SELECT * FROM (
              SELECT DISTINCT ON (id)
                *
              FROM (
                SELECT
                  o.id AS organization_id,
                  MAX(p.id::VARCHAR) AS id,
                  MAX(p.name) AS name,
                  m.first_cited AS first_cited,
                  m.last_cited AS last_cited,
                  COUNT(DISTINCT v.id) AS events_count
                FROM organization AS o
                JOIN membershipperson AS m
                  ON o.id = m.organization_id
                JOIN person AS p
                  ON m.member_id = p.id
                LEFT JOIN violation AS v
                  ON p.id = v.perpetrator_id
                WHERE o.id = %s
                  AND m.role = 'Commander'
                  AND m.first_cited <= %s
                  AND COALESCE(m.last_cited::date, NOW()::date)  >= %s
                GROUP BY o.id, m.first_cited, m.last_cited
                ORDER BY o.id,
                         m.last_cited DESC,
                         m.first_cited DESC
              ) AS s
            ) AS s 
            ORDER BY last_cited DESC, first_cited DESC
            LIMIT 1
        '''

        cursor = connection.cursor()
        cursor.execute(commander, [properties['id'], when, when])
        columns = [c[0] for c in cursor.description]
        
        row = cursor.fetchone()
        
        properties['current_commander'] = {}

        if row:
            properties['current_commander'] = dict(zip(columns, row))

        return properties

    def makeOrganizationGeographies(self, 
                                    properties, 
                                    all_geography=False,
                                    tolerance=0.001):

        site_present = '''
            SELECT DISTINCT ON (e.id)
              g.id,
              g.name,
              g.admin_level_1 AS admin_level_1_osm_name,
              g.osmname AS osm_name,
              e.start_date AS date_first_cited,
              e.end_date AS date_last_cited,
              ST_AsGeoJSON(g.coordinates)::json AS location
            FROM organization AS o
            JOIN emplacement AS e
              ON o.id = e.organization_id
            JOIN geosite AS g
              ON e.site_id = g.id
            WHERE o.id = %s
            ORDER BY e.id,
                     e.end_date::date DESC,
                     e.start_date::date DESC
        '''

        cursor = connection.cursor()
        cursor.execute(site_present, [properties['id']])
        columns = [c[0] for c in cursor.description]

        if all_geography:
            properties['sites'] = [self.makeFeature(r[-1], dict(zip(columns, r))) for r in cursor]
        else:
            row = cursor.fetchone()
            if row:
                properties['site_current'] = dict(zip(columns, row))
            else:
                properties['site_current'] = {}

        area_present = '''
            SELECT DISTINCT ON (ass.id)
              o.id,
              a.name,
              a.osmname AS osm_name,
              a.osmid,
              ass.start_date AS first_cited,
              ass.end_date AS last_cited,
              ST_AsGeoJSON(ST_Simplify(a.geometry, %s))::json AS geometry
            FROM organization AS o
            JOIN association AS ass
              ON o.id = ass.organization_id
            JOIN area AS a
              ON ass.area_id = a.id
            WHERE o.id = %s
            ORDER BY ass.id,
                     ass.end_date::date DESC,
                     ass.start_date::date DESC
        '''

        cursor = connection.cursor()
        cursor.execute(area_present, [tolerance, properties['id']])
        columns = [c[0] for c in cursor.description]

        if all_geography:
            properties['areas'] = [self.makeFeature(r[-1], dict(zip(columns, r))) for r in cursor]
        else:
            row = cursor.fetchone()
            if row:
                properties['area_current'] = dict(zip(columns, row))
            else:
                properties['area_current'] = {}

        return properties

    def makeOrganization(self,
                         properties,
                         relationships=True,
                         all_commanders=True,
                         present_commander=False,
                         simple=False,
                         all_geography=False,
                         memberships=False,
                         tolerance=0.001):

        if relationships:
            properties = self.makeOrganizationRelationships(properties)

        if all_commanders:
            properties = self.makeOrganizationCommanders(properties)
        
        if present_commander:
            properties = self.makePresentCommander(properties)

        if not simple:
            properties = self.makeOrganizationGeographies(properties,
                                                          all_geography=all_geography,
                                                          tolerance=tolerance)

        if memberships and properties.get('memberships'):

            orgs = []

            for org in properties['memberships']:

                member_orgs = '''
                    SELECT DISTINCT ON (mo.member_id_value)
                      o.id,
                      MAX(o.name) AS name,
                      array_agg(DISTINCT TRIM(o.alias))
                        FILTER (WHERE TRIM(o.alias) IS NOT NULL) AS other_names,
                      array_agg(DISTINCT TRIM(o.classification))
                        FILTER (WHERE TRIM(o.classification) IS NOT NULL) AS classifications,
                      MAX(mo.member_id_sources::VARCHAR)::json AS sources
                    FROM organization AS o
                    JOIN membershiporganization_sources AS mo
                      ON o.id = mo.organization_id_value
                    WHERE o.id = %s
                    GROUP BY o.id, mo.member_id_value
                '''

                cursor = connection.cursor()
                cursor.execute(member_orgs, [org])

                columns = [c[0] for c in cursor.description]

                for org_id, group in itertools.groupby(cursor, lambda x: x[0]):
                    grouping = [dict(zip(columns, r)) for r in group]

                    o = {
                        'id': org_id,
                        'name': grouping[0]['name'],
                        'other_names': grouping[0]['other_names'],
                        'classifications': grouping[0]['classifications'],
                        'sources': []
                    }

                    source_ids = []

                    for row in grouping:

                        for source in row['sources']:

                            if source['id'] not in source_ids:
                                o['sources'].append(source)
                                source_ids.append(source['id'])

                    orgs.append(o)

            properties['memberships'] = orgs

        return properties

    def makePerson(self, properties):

        properties['membership_present'] = None
        properties['membership_former'] = None

        membership_present = '''
            SELECT
              row_to_json(o.*) AS organization,
              role,
              rank,
              title,
              g.site_present
            FROM membershipperson AS mp
            JOIN (
              SELECT DISTINCT ON (id)
                id,
                name
              FROM organization
            ) AS o
              ON mp.organization_id = o.id
            JOIN (
              SELECT DISTINCT ON (o.id)
                o.id AS organization_id,
                json_build_object('type', 'Feature',
                                  'id', g.id,
                                  'properties', json_build_object('location', g.name,
                                                                  'osm_name', g.osmname,
                                                                  'admin_level_1_osm_name', g.admin_level_1),
                                  'geometry', ST_AsGeoJSON(g.coordinates)::json) AS site_present
              FROM organization AS o
              LEFT JOIN emplacement AS e
                ON o.id = e.organization_id
              LEFT JOIN geosite AS g
                ON e.site_id = g.id
              ORDER BY o.id, e.end_date DESC, e.start_date DESC
            ) AS g
              ON o.id = g.organization_id
            LEFT JOIN emplacement AS e
              ON mp.organization_id = e.organization_id
            WHERE mp.member_id = %s
              AND (e.end_date IS NULL OR
                   e.end_date::date > NOW()::date)
              AND (mp.last_cited IS NULL OR
                   mp.last_cited::date > NOW()::date)
        '''

        membership_former = '''
            SELECT
              row_to_json(o.*) AS organization,
              role,
              rank,
              title
            FROM membershipperson AS mp
            JOIN (
              SELECT DISTINCT ON (id)
                id,
                name
              FROM organization
            ) AS o
              ON mp.organization_id = o.id
            LEFT JOIN emplacement AS e
              ON mp.organization_id = e.organization_id
            WHERE mp.member_id = %s
              AND e.end_date::date < NOW()::date
        '''

        cursor = connection.cursor()
        cursor.execute(membership_present, [properties['id']])
        columns = [c[0] for c in cursor.description]

        row = cursor.fetchone()

        if row:
            properties['membership_present'] = dict(zip(columns, row))

        cursor = connection.cursor()
        cursor.execute(membership_former, [properties['id']])
        columns = [c[0] for c in cursor.description]

        row = cursor.fetchone()

        if row:
            properties['membership_former'] = dict(zip(columns, row))

        return properties

    def makeEvent(self, properties, simple=False):

        perp_org_ids = []
        perp_orgs = []
        for org in properties['perpetrator_organization']:
            if org and org['id'] not in perp_org_ids:
                structured_org = self.makeOrganization(org,
                                                       relationships=False,
                                                       simple=simple)

                perp_orgs.append(structured_org)
                perp_org_ids.append(org['id'])

        properties['perpetrator_organization'] = perp_orgs

        site_ids = []
        sites = []
        if properties.get('sites_nearby'):
            for site in properties['sites_nearby']:
                if site['id'] not in site_ids:
                    sites.append(site)
                    site_ids.append(site['id'])

            properties['sites_nearby'] = sites
        
        if properties.get('sources'):
            properties['sources'] = properties['sources'][0]

        return properties

    def makeWhereClauses(self):
        where_clauses = []

        for field, operator, value in self.wheres:
            operator = OPERATOR_LOOKUP[operator]

            if self.filter_fields.get(field):
                db_field = self.filter_fields[field]['field']

                clause = '{0} {1} %s'.format(db_field, operator)

                if operator == 'IN':
                    value = tuple(v for v in value.split(','))
                    clause = 'TRIM({0}) {1} %s'.format(db_field, operator)

                where_clauses.append((clause, value,))

        return where_clauses

    def makeHavingClauses(self):
        having_clauses = []

        for field, operator, value in self.having:
            operator = OPERATOR_LOOKUP[operator]

            db_field = self.having_fields[field]['field']
            aggregate_function = self.having_fields[field]['function']

            clause = '{function}({field}) {operator} %s'.format(function=aggregate_function,
                                                                field=db_field,
                                                                operator=operator)
            having_clauses.append((clause, value,))

        return having_clauses

    def makeOrderBy(self):
        order_bys = []

        for field, sort_order in self.order_bys:
            db_field = self.order_by_fields[field]['field']
            order_bys.append('{0} {1}'.format(db_field, sort_order))

        return order_bys

    def appendWhereClauses(self, query):
        where_clauses = self.makeWhereClauses()

        these_args = []
        for clause, value in where_clauses:
            query = '{0} AND {1}'.format(query, clause)
            these_args.append(value)

        return query, these_args

    def getFacets(self,
                  query,
                  grouper):

        q_args = []
        group_by = 'GROUP BY TRIM({0}), uuid'.format(grouper)

        having_clauses, q_args = self.appendHavingClauses('')

        facets_counts = '''
            SELECT
              SUM(facet_count)::int AS facet_count,
              facet,
              uuid
            FROM (
              {0}
              {1}
              {2}
            ) AS s
            GROUP BY facet, uuid
        '''.format(query, group_by, having_clauses)

        return facets_counts, q_args

    def retrieveFacetsCounts(self, base_query, query_args):

        for facet in self.facet_fields:

            facets_counts = '''
                SELECT
                  TRIM({0}) AS facet,
                  COUNT(DISTINCT uuid) AS facet_count,
                  uuid
                {1}
                AND {0} IS NOT NULL
            '''.format(facet, base_query)

            facets_counts, this_facet_args = self.appendWhereClauses(facets_counts)
            this_facet_args = query_args + this_facet_args

            facets_counts, more_args = self.getFacets(facets_counts, facet)
            this_facet_args = this_facet_args + more_args

            cursor = connection.cursor()
            cursor.execute(facets_counts, this_facet_args)

            facets_counts = [r for r in cursor]

            count = int(len({f[2] for f in facets_counts}))

            facets_counts = sorted(facets_counts, key=lambda x: x[1])
            aggregated_facets_counts = []

            for f, group in itertools.groupby(facets_counts, key=lambda x: x[1]):
                aggregated_facets_counts.append([f, len(list(group))])

            this_facet_args = []

            yield facet, count, aggregated_facets_counts

    def orderPaginate(self, query):
        order_by = self.makeOrderBy()

        if order_by:
            order_by = ', '.join(order_by)
            query = '{0} ORDER BY {1}'.format(query, order_by)

        query = '''
            SELECT * FROM ({0}) AS s LIMIT {1}
        '''.format(query, self.page_count)

        if self.request.GET.get('p'):
            page = self.request.GET.get('p')

            if int(page) >= 1:
                offset = (int(page) - 1) * self.page_count
                query = '{0} OFFSET {1}'.format(query, offset)

        return query

    def appendHavingClauses(self, query):
        having_clauses = self.makeHavingClauses()

        these_args = []
        if having_clauses:

            query_fmt = '{0} HAVING ({1})'
            clauses = []

            for clause, value in having_clauses:
                clauses.append(clause)
                these_args.append(value)

            query = query_fmt.format(query, ' AND '.join(clauses))

        return query, these_args
