import re
import importlib
from collections import namedtuple
import itertools
import json

from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.db import connection

CONFIDENCE_MAP = {
    'low': 1,
    'medium': 2,
    'high': 3,
}

REVERSE_CONFIDENCE = {v:k for k,v in CONFIDENCE_MAP.items()}

class RequireLoginMiddleware(object):

    """
    Middleware component that wraps the login_required decorator around
    matching URL patterns. To use, add the class to MIDDLEWARE_CLASSES and
    define LOGIN_REQUIRED_URLS and LOGIN_REQUIRED_URLS_EXCEPTIONS in your
    settings.py. For example:
    ------
    LOGIN_REQUIRED_URLS = (
        r'/topsecret/(.*)$',
    )
    LOGIN_REQUIRED_URLS_EXCEPTIONS = (
        r'/topsecret/login(.*)$',
        r'/topsecret/logout(.*)$',
    )
    ------
    LOGIN_REQUIRED_URLS is where you define URL patterns; each pattern must
    be a valid regex.

    LOGIN_REQUIRED_URLS_EXCEPTIONS is, conversely, where you explicitly
    define any exceptions (like login and logout URLs).
    """

    def __init__(self):
        self.required = tuple(re.compile(url)
                              for url in settings.LOGIN_REQUIRED_URLS)
        self.exceptions = tuple(re.compile(url)
                                for url in settings.LOGIN_REQUIRED_URLS_EXCEPTIONS)

    def process_view(self, request, view_func, view_args, view_kwargs):
        # No need to process URLs if user already logged in
        if request.user.is_authenticated():
            return None

        # An exception match should immediately return None
        for url in self.exceptions:
            if url.match(request.path):
                return None

        # Requests matching a restricted URL pattern are returned
        # wrapped with the login_required decorator
        for url in self.required:
            if url.match(request.path):
                return login_required(view_func)(request, *view_args, **view_kwargs)

        # Explicitly return None for all non-matching requests
        return None

def class_for_name(class_name, module_name="person.models"):
    if class_name == "Membershipperson":
        class_name = "MembershipPerson"

    if class_name not in settings.ALLOWED_CLASS_FOR_NAME:
        raise Exception("Unallowed class for name")
    module = importlib.import_module(module_name)
    class_ = getattr(module, class_name)
    return class_

def get_osm_by_id(osm_id):
    
    osm_feature = None
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM osm_data WHERE id = %s', [osm_id])
    
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
        
        trimmed = {
            'id': org_id,
            'name': orgs[0].name,
            'other_names': list({o.alias.strip() for o in orgs if o.alias}),
            'classifications': list({o.classification.strip() for o in orgs if o.classification}),
            'division_id': orgs[0].division_id,
            'date_first_cited': orgs[0].start_date,
            'date_last_cited': orgs[0].end_date,
            # 'parent_id': orgs[0].parent_id
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

def get_org_hierarchy_by_id(org_id, when=None, sources=False):
    hierarchy = ''' 
        WITH RECURSIVE children AS (
          SELECT 
            o.*,
            NULL::VARCHAR AS child_id, 
            NULL::VARCHAR AS child_name, 
            NULL::DATE AS start_date,
            NULL::DATE AS end_date,
            NULL::BOOL AS open_ended,
            NULL::VARCHAR AS source,
            NULL::VARCHAR AS confidence
          FROM organization As o 
          WHERE id = %s 
          UNION 
          SELECT 
            o.*,
            h.child_id::VARCHAR AS child_id, 
            children.name AS child_name, 
            h.start_date::date,
            h.end_date::date,
            h.open_ended,
            row_to_json(ss.*)::VARCHAR AS source,
            ccc.confidence
          FROM organization AS o 
          JOIN composition AS h 
            ON o.id = h.parent_id 
          JOIN composition_compositionparent AS ccc
            ON h.id = ccc.object_ref_id
          LEFT JOIN composition_compositionparent_sources AS cccs
            ON ccc.id = cccs.compositionparent_id
          LEFT JOIN source_source AS ss
            ON cccs.source_id = ss.id
          JOIN children 
            ON children.id = h.child_id
        ) SELECT * FROM children WHERE id != %s
    '''
    
    q_args = [org_id, org_id]
    if when:
        hierarchy = '''
            {} 
            AND start_date <= %s 
            AND (end_date >= %s OR open_ended = TRUE)
        '''.format(hierarchy)
        q_args.extend([when, when])
    
    hierarchy = '{} ORDER BY id'.format(hierarchy)

    hierarchy = generate_hierarchy(hierarchy, q_args, 'child_id', sources=sources)
    
    return hierarchy

def get_child_orgs_by_id(org_id, when=None, sources=False):
    hierarchy = ''' 
        WITH RECURSIVE parents AS (
          SELECT 
            o.*,
            NULL::VARCHAR AS parent_id, 
            NULL::VARCHAR AS parent_name,
            NULL::DATE AS start_date,
            NULL::DATE AS end_date,
            NULL::BOOL AS open_ended,
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
            h.open_ended,
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
            ON cccs.source_id = ss.id
          JOIN parents 
            ON parents.id = h.parent_id
        ) SELECT * FROM parents WHERE id != %s
    '''
    
    q_args = [org_id, org_id]
    if when:
        hierarchy = '''
            {} 
            AND start_date <= %s 
            AND (end_date >= %s OR open_ended = TRUE)
        '''.format(hierarchy)
        q_args.extend([when, when])
    
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
                objects[index] = _("Object sources")
            else:
                objects[index] = name
        index += 1

    return objects

def import_class(cl):
    d = cl.rfind('.')
    classname = cl[d+1:len(cl)]
    m = __import__(cl[0:d], globals(), locals(), [classname])
    return getattr(m, classname)
