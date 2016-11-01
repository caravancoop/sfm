import re
import importlib
from collections import namedtuple

from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.db import connection

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

def get_geoname_by_id(geoname_id):
    
    geoname = None
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM geonames WHERE geonameid = %s', [geoname_id])
    
    columns = [c[0] for c in cursor.description]
    results_tuple = namedtuple('Geoname', columns)

    row = cursor.fetchone()

    if row:
        geoname = results_tuple(*row)
        
    return geoname

def get_hierarchy_by_id(geoname_id):
    hierarchy = ''' 
        WITH RECURSIVE children AS (
          SELECT 
            gn.geonameid,
            gn.name,
            gn.feature_code,
            NULL::INT AS child_id, 
            NULL::VARCHAR AS child_name 
          FROM geonames AS gn 
          WHERE geonameid = %s 
          UNION 
          SELECT 
            g.geonameid, 
            g.name,
            g.feature_code,
            h.child_id::INT AS child_id, 
            children.name AS child_name 
          FROM geonames AS g 
          JOIN geonames_hierarchy AS h 
            ON g.geonameid = h.parent_id 
          JOIN children 
            ON children.geonameid = h.child_id
        ) SELECT * FROM children;
    '''

    cursor = connection.cursor()
    cursor.execute(hierarchy, [geoname_id])
    
    columns = [c[0] for c in cursor.description]
    results_tuple = namedtuple('Geoname', columns)

    hierarchy = [results_tuple(*r) for r in cursor]
    
    return hierarchy

def get_org_hierarchy_by_id(org_id):
    hierarchy = ''' 
        WITH RECURSIVE children AS (
          SELECT 
            o.*,
            NULL::VARCHAR AS child_id, 
            NULL::VARCHAR AS child_name 
          FROM organization As o 
          WHERE id = %s 
          UNION 
          SELECT 
            o.*,
            h.child_id::VARCHAR AS child_id, 
            children.name AS child_name 
          FROM organization AS o 
          JOIN composition AS h 
            ON o.id = h.parent_id 
          JOIN children 
            ON children.id = h.child_id
        ) SELECT * FROM children;
    '''
    
    cursor = connection.cursor()
    cursor.execute(hierarchy, [org_id])
    
    columns = [c[0] for c in cursor.description]
    results_tuple = namedtuple('Organization', columns)

    hierarchy = [results_tuple(*r) for r in cursor]
    
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
