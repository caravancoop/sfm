from collections import OrderedDict
import itertools
import json
from datetime import datetime

from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView
from django.db import connection

from violation.models import Violation
from sfm_pc.utils import get_org_hierarchy_by_id

OPERATOR_LOOKUP = {
    'lte': '<=',
    'gte': '>=',
    'eq': '=',
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

class JSONAPIView(JSONResponseMixin, TemplateView):
    safe = True
    
    def dispatch(self, request, *args, **kwargs):
        errors = []
        self.wheres = []
        self.order_bys = []

        filter_fields = list(getattr(self, 'filter_fields', {}).keys())
        order_by_fields = list(getattr(self, 'order_by_fields', {}).keys())
        required_params = getattr(self, 'required_params', [])
        optional_params = getattr(self, 'optional_params', [])

        valid_params = required_params + filter_fields + order_by_fields + optional_params
        
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
        
        feature = {
            'type': 'Feature',
            'id': properties['id'],
            'properties': properties,
            'geometry': geometry
        }

        return feature
    
    def makeOrganization(self, properties, relationships=True):
        
        if relationships:
            hierarchy = get_org_hierarchy_by_id(properties['id'])
            
            properties['root_name'] = None
            properties['root_id'] = None

            if hierarchy:
                top = hierarchy[-1]
                properties['root_name'] = top.name
                properties['root_id'] = top.id

        event_count = ''' 
            SELECT COUNT(*) AS count
            FROM violation
            WHERE perpetrator_organization_id = %s
        '''

        cursor = connection.cursor()
        cursor.execute(event_count, [properties['id']])
        
        properties['event_count'] = cursor.fetchone()[0]
        
        current_commander = ''' 
            SELECT DISTINCT ON (o.id)
              o.id,
              p.name,
              m.first_cited,
              m.last_cited
            FROM organization AS o
            JOIN membershipperson AS m
              ON o.id = m.organization_id
            JOIN person AS p
              ON m.member_id = p.id
            WHERE o.id = %s
            ORDER BY o.id, 
                     m.last_cited DESC, 
                     m.first_cited DESC
        '''
        
        cursor = connection.cursor()
        cursor.execute(current_commander, [properties['id']])
        columns = [c[0] for c in cursor.description]
        
        row = cursor.fetchone()
        
        if row:
            properties['current_commander'] = dict(zip(columns, row))
        else:
            properties['current_commander'] = {}
        
        site_present = ''' 
            SELECT DISTINCT ON (o.id)
              o.id,
              g.name AS location,
              g.admin_level_1 AS admin_level_1_geonames_name,
              g.geoname AS geonames_name,
              g.first_cited AS date_first_cited,
              g.last_cited AS date_last_cited
            FROM organization AS o
            JOIN emplacement AS e
              ON o.id = e.organization_id
            JOIN geosite AS g
              ON e.site_id = g.id
            WHERE o.id = %s
            ORDER BY o.id, 
                     g.last_cited DESC, 
                     g.first_cited DESC
        '''
        
        cursor = connection.cursor()
        cursor.execute(site_present, [properties['id']])
        columns = [c[0] for c in cursor.description]
        
        row = cursor.fetchone()
        
        if row:
            properties['site_current'] = dict(zip(columns, row))
        else:
            properties['site_current'] = {}
        
        area_present = ''' 
            SELECT DISTINCT ON (o.id)
              o.id,
              a.name,
              a.geoname AS geonames_name,
              a.geonameid,
              a.geometry
            FROM organization AS o
            JOIN association AS ass
              ON o.id = ass.organization_id
            JOIN area AS a
              ON ass.area_id = a.id
            WHERE o.id = %s
            ORDER BY o.id, 
                     a.last_cited DESC, 
                     a.first_cited DESC
        '''
        
        cursor = connection.cursor()
        cursor.execute(area_present, [properties['id']])
        columns = [c[0] for c in cursor.description]
        
        row = cursor.fetchone()
        
        if row:
            properties['area_current'] = dict(zip(columns, row))
        else:
            properties['area_current'] = {}

        return properties

    def makeEvent(self, properties):
        properties['classification'] = list(set(properties['classification']))

        perp_class = [c for c in list(set(properties['perpetrator_classification'])) if c]
        if perp_class:
            properties['perpetrator_classification'] = perp_class
        else:
            properties['perpetrator_classification'] = None

        perp_org_ids = []
        perp_orgs = []
        for org in properties['perpetrator_organization']:
            if org and org['id'] not in perp_org_ids:
                structured_org = self.makeOrganization(org, relationships=False)
                
                perp_orgs.append(structured_org)
                perp_org_ids.append(org['id'])

        properties['perpetrator_organization'] = perp_orgs
        return properties
    
    def makeWhereClauses(self):
        where_clauses = []

        for field, operator, value in self.wheres:
            operator = OPERATOR_LOOKUP[operator]
            
            if self.filter_fields.get(field):
                db_field = self.filter_fields[field]['field']
            
                clause = '{0} {1} %s'.format(db_field, operator)
                where_clauses.append((clause, value,))
        
        return where_clauses
        
    def makeOrderBy(self):
        order_bys = []

        for field, sort_order in self.order_bys:
            db_field = self.order_by_fields[field]['field']
            order_bys.append('{0} {1}'.format(db_field, sort_order))

        return order_bys

class OrganizationSearchView(JSONAPIView):
    
    page_count = 20

    filter_fields = {
        'date_first_cited': {
            'field': 'start_date', 
            'operators': ['gte', 'lte'],
            'validator': dateValidator,
        },
        'date_last_cited': {
            'field': 'end_date',
            'operators': ['gte', 'lte'],
            'validator': dateValidator,
        },
        'classification': {
            'field': 'classification',
            'operators': ['in'],
            'validator': None,
        },
        'geonames_id': {
            'field': 'geoname_id',
            'operators': ['eq'],
            'validator': integerValidator,
        },
        'events_count': {
            'field': 'events_count',
            'operators': ['gte', 'lte',],
            'validator': integerValidator,
        },
    }
    
    order_by_fields = {
        'name': {'field': 'name'},
        'date_first_cited': {'field': 'start_date'},
        'date_last_cited': {'field': 'end_date'},
        # 'events_count': {},
        '-name': {'field': 'name'},
        '-date_first_cited': {'field': 'start_date'},
        '-date_last_cited': {'field': 'end_date'},
        # '-events_count',
    }
    
    required_params = ['q']
    optional_params = ['o', 'p']

    def appendWhereClauses(self, query, query_args):
        where_clauses = self.makeWhereClauses()
        
        for clause, value in where_clauses:
            query = '{0} AND {1}'.format(query, clause)
            query_args.append(value)
        
        return query, query_args

    def getFacets(self, base_query, query_args):
        
        facets_counts = '''
            SELECT 
              o.classification AS facet,
              COUNT(*) AS facet_count
            {}
        '''.format(base_query)
        
        facets_counts, query_args = self.appendWhereClauses(facets_counts, query_args)

        facets_counts = '{} GROUP BY o.classification'.format(facets_counts)
        
        cursor = connection.cursor()
        cursor.execute(facets_counts, query_args)
        
        facets_counts = [r for r in cursor]
        
        count = sum(f[1] for f in facets_counts)
        
        return count, facets_counts
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        country_code = kwargs['id']
        division_id = 'ocd-division/country:{}'.format(country_code)
        
        query_term = self.request.GET['q']
        
        query_args = [query_term, division_id]
        
        base_query = ''' 
            FROM organization AS o
            JOIN organization_organization AS oo
              ON o.id = oo.uuid
            JOIN search_index AS si
              ON oo.id = si.id
            JOIN emplacement AS e
              ON o.id = e.organization_id
            JOIN geosite as g
              ON e.site_id = g.id
            WHERE plainto_tsquery('english', %s) @@ si.content
              AND si.content_type = 'Organization'
              AND o.division_id = %s
        '''
        
        count, facets_counts = self.getFacets(base_query, query_args)
        
        context['count'] = count
        context['facets'] = facets_counts
        
        query_args = [query_term, division_id]

        organizations = '''
            SELECT 
              o.id, 
              MAX(o.name) AS name,
              array_agg(DISTINCT o.alias) AS other_names,
              ST_AsGeoJSON(MAX(g.coordinates))::json AS location,
              MAX(e.start_date) AS start_date,
              MAX(e.end_date) AS end_date
            {}
        '''.format(base_query)
        
        organizations, query_args = self.appendWhereClauses(organizations, query_args)
        
        organizations = '{} GROUP BY o.id'.format(organizations)

        order_by = self.makeOrderBy()
        
        if order_by:
            order_by = ', '.join(order_by)
            organizations = '{0} ORDER BY {1}'.format(organizations, order_by)
        
        organizations = '{0} LIMIT {1}'.format(organizations, self.page_count)

        if self.request.GET.get('p'):
            page = self.request.GET.get('p')
            
            if int(page) >= 1:
                offset = (int(page) - 1) * self.page_count
                organizations = '{0} OFFSET {1}'.format(organizations, offset)

        cursor = connection.cursor()
        cursor.execute(organizations, query_args)
        columns = [c[0] for c in cursor.description]
        
        organizations = [self.makeOrganization(OrderedDict(zip(columns, r))) for r in cursor]
        
        context['results'] = organizations

        return context

class GeonameAutoView(JSONAPIView):
    
    safe = False
    required_params = ['q']
    optional_params = ['bbox']
    filter_fields = {
        'classification': {
            'field': 'classification',
            'operators': ['in'],
            'validator': None,
        },
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # TODO: Add some error handling for poorly formatted requests
        q = self.request.GET['q']
        classification = self.request.GET.get('classification')
        bbox = self.request.GET.get('bbox')

        geonames = ''' 
            SELECT
              geonameid AS id,
              name,
              alternatenames,
              feature_code AS classification,
              ST_AsGeoJSON(location)::json AS location
            FROM geonames
            WHERE plainto_tsquery('english', %s) @@ search_index
            AND country_code = %s
        '''
        
        args = [q, kwargs['id'].upper()]

        if classification:
            geonames = '{} AND feature_code = %s'.format(geonames)
            args.append(classification)

        if bbox:
            geonames = '''
                {} ST_Within(location,  
                             ST_MakeEnvelope(%s, %s, %s, %s, 4326))
            '''.format(geonames)
            args.extend(bbox.split(','))
        
        cursor = connection.cursor()
        cursor.execute(geonames, args)
        columns = [c[0] for c in cursor.description]
        
        context = [self.makeFeature(r[4], dict(zip(columns, r))) for r in cursor]

        return context

class CountryListView(JSONAPIView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class CountryDetailView(JSONAPIView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class CountryZipView(JSONAPIView):
    # TODO: This should actually return a zipfile
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class CountryTxtView(JSONAPIView):
    # TODO: This should actually return a text file
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class CountryMapView(JSONAPIView):
    
    required_params = ['at']
    optional_params = ['bbox']
    filter_fields = {
        'classification': {
            'field': 'classification',
            'operators': ['in'],
            'validator': None,
        },
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        country_code = kwargs['id']
        division_id = 'ocd-division/country:{}'.format(country_code)
        
        # TODO: Add some error handling for poorly formatted requests
        when = self.request.GET['at']
        bbox = self.request.GET.get('bbox')
        classification = self.request.GET.get('classification__in')
        
        if classification:
            classifications = classification.split(',')
        
        organizations = ''' 
            SELECT 
              o.id, 
              MAX(o.name) AS name,
              array_agg(DISTINCT o.alias) AS other_names,
              ST_AsGeoJSON(MAX(g.coordinates))::json AS location,
              MAX(e.start_date) AS start_date,
              MAX(e.end_date) AS end_date
            FROM organization AS o
            JOIN emplacement AS e
              ON o.id = e.organization_id
            JOIN geosite as g
              ON e.site_id = g.id
            WHERE o.division_id = %s
              AND (e.start_date <= %s OR e.end_date >= %s)
        '''
        
        args = [division_id, when, when]

        if bbox:
            organizations = '''
                {} AND ST_Within(g.coordinates,  
                                 ST_MakeEnvelope(%s, %s, %s, %s, 4326))
            '''.format(organizations)
            args.extend(bbox.split(','))
        
        organizations = '{} GROUP BY o.id'.format(organizations)

        cursor = connection.cursor()
        
        cursor.execute(organizations, args)
        columns = [c[0] for c in cursor.description]
        
        organizations = [self.makeOrganization(OrderedDict(zip(columns, r))) for r in cursor]
        
        context['organizations'] = [self.makeFeature(o['location'], o) for o in organizations]
        
        events = ''' 
            SELECT 
              v.id,
              MAX(v.start_date) AS start_date,
              MAX(v.end_date) AS end_date,
              MAX(v.location_description) AS location_description,
              MAX(v.admin_level_1) AS admin_level_1,
              MAX(v.admin_level_2) AS admin_level_2,
              MAX(v.geoname) AS geoname,
              MAX(v.geoname_id) AS geoname_id,
              MAX(v.division_id) AS division_id,
              ST_ASGeoJSON(MAX(v.location))::json AS location,
              MAX(v.description) AS description,
              MAX(p.name) AS perpetrator_name,
              array_agg(v.perpetrator_classification) AS perpetrator_classification,
              array_agg(v.violation_type) AS classification,
              json_agg(row_to_json(o.*)) AS perpetrator_organization
            FROM violation AS v
            LEFT JOIN person AS p
              ON v.perpetrator_id = p.id
            LEFT JOIN organization AS o
              ON v.perpetrator_organization_id = o.id
            WHERE v.division_id = %s
              AND (v.start_date <= %s OR v.end_date >= %s)
        '''
        
        args = [division_id, when, when]
        
        if bbox:
            events = '''
                {} AND ST_Within(v.location,  
                                 ST_MakeEnvelope(%s, %s, %s, %s, 4326))
            '''.format(events)
            args.extend(bbox.split(','))
        
        if classification:
            events = ''' 
                {} AND TRIM(violation_type) IN %s
            '''.format(events)

            args.append(tuple(classification.split(',')))

        events = '{} GROUP BY v.id'.format(events)
        
        cursor.execute(events, args)
        columns = [c[0] for c in cursor.description]
        
        events = [self.makeEvent(OrderedDict(zip(columns, r))) for r in cursor]
        
        context['events'] = [self.makeFeature(o['location'], o) for o in events]
        
        return context

class CountryEventsView(JSONAPIView):
    
    safe = False
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        country_code = kwargs['id']
        division_id = 'ocd-division/country:{}'.format(country_code)
        
        events = ''' 
            SELECT 
              v.id,
              MAX(v.start_date) AS start_date,
              MAX(v.end_date) AS end_date,
              MAX(v.location_description) AS location_description,
              MAX(v.admin_level_1) AS admin_level_1,
              MAX(v.admin_level_2) AS admin_level_2,
              MAX(v.geoname) AS geoname,
              MAX(v.geoname_id) AS geoname_id,
              MAX(v.division_id) AS division_id,
              ST_ASGeoJSON(MAX(v.location))::json AS location,
              MAX(v.description) AS description,
              MAX(p.name) AS perpetrator_name,
              array_agg(v.perpetrator_classification) AS perpetrator_classification,
              array_agg(v.violation_type) AS classification,
              json_agg(row_to_json(o.*)) AS perpetrator_organization
            FROM violation AS v
            LEFT JOIN person AS p
              ON v.perpetrator_id = p.id
            LEFT JOIN organization AS o
              ON v.perpetrator_organization_id = o.id
            WHERE v.division_id = %s
            GROUP BY v.id
        ''' 
        
        cursor = connection.cursor()
        
        cursor.execute(events, [division_id])
        columns = [c[0] for c in cursor.description]
        
        events = []
        
        for event in cursor:
            event = OrderedDict(zip(columns, event))
            event = self.makeEvent(event)
            feature = self.makeFeature(event['location'], event)
            events.append(feature)

        return events

class EventDetailView(JSONAPIView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        event = {}
        nearby = []

        event = ''' 
            SELECT 
              v.id,
              MAX(v.start_date) AS start_date,
              MAX(v.end_date) AS end_date,
              MAX(v.location_description) AS location_description,
              MAX(v.admin_level_1) AS admin_level_1,
              MAX(v.admin_level_2) AS admin_level_2,
              MAX(v.geoname) AS geoname,
              MAX(v.geoname_id) AS geoname_id,
              MAX(v.division_id) AS division_id,
              ST_ASGeoJSON(MAX(v.location))::json AS location,
              MAX(v.description) AS description,
              MAX(p.name) AS perpetrator_name,
              array_agg(v.perpetrator_classification) AS perpetrator_classification,
              array_agg(v.violation_type) AS classification,
              json_agg(row_to_json(o.*)) AS perpetrator_organization
            FROM violation AS v
            LEFT JOIN person AS p
              ON v.perpetrator_id = p.id
            LEFT JOIN organization AS o
              ON v.perpetrator_organization_id = o.id
            WHERE v.id = %s
            GROUP BY v.id
        ''' 
        
        nearby = '''
              SELECT 
                o.id, 
                MAX(o.name) AS name,
                array_agg(DISTINCT o.alias) AS other_names
              FROM violation AS v
              JOIN geosite AS g
                ON  ST_Intersects(ST_Buffer_Meters(v.location, 35000), g.coordinates)
              JOIN emplacement AS e
                ON g.id = e.site_id
              JOIN organization AS o
                ON e.organization_id = o.id
              WHERE v.id = %s
                AND v.perpetrator_organization_id != e.organization_id
              GROUP BY o.id
        '''

        cursor = connection.cursor()
        
        cursor.execute(event, [kwargs['id']])
        columns = [c[0] for c in cursor.description]
        events = [OrderedDict(zip(columns, r)) for r in cursor]
        
        if events:
            event = self.makeEvent(events[0])
            
            cursor.execute(nearby, [kwargs['id']])
            columns = [c[0] for c in cursor.description]
            nearby = [self.makeOrganization(OrderedDict(zip(columns, r))) for r in cursor]
            
            event['organizations_nearby'] = nearby

        context.update(event)

        return context
