from collections import OrderedDict

from django.db import connection

from api.base_views import JSONAPIView, dateValidator, integerValidator

class OrganizationSearchView(JSONAPIView):
    
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
        # 'events_count': {
        #     'field': 'events_count',
        #     'operators': ['gte', 'lte',],
        #     'validator': integerValidator,
        # },
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
    
    facet_fields = ['classification']

    def get_context_data(self, **kwargs):
        context = {}
        
        country_code = kwargs['id']
        division_id = 'ocd-division/country:{}'.format(country_code)
        
        query_term = self.request.GET['q']
        
        query_args = [query_term, division_id]
        
        # Create last half of query so counts and main query are working with
        # the same joins
        base_query = ''' 
            FROM organization AS o
            JOIN organization_organization AS oo
              ON o.id = oo.uuid
            JOIN search_index AS si
              ON oo.id = si.object_ref_id
            LEFT JOIN emplacement AS e
              ON o.id = e.organization_id
            LEFT JOIN geosite as g
              ON e.site_id = g.id
            LEFT JOIN violation AS v
              ON o.id = v.perpetrator_organization_id
            WHERE plainto_tsquery('english', %s) @@ si.content
              AND si.content_type = 'Organization'
              AND o.division_id = %s
        '''
        
        context['count'] = 0
        context['facets'] = {}

        for facet, count, facet_count in self.retrieveFacetsCounts(base_query, query_args):
            context['count'] = count
            context['facets'][facet] = facet_count
        
        # Reinitialize query params so we can re-run the query with limit / offset
        query_args = [query_term, division_id]

        organizations = '''
            SELECT 
              o.id, 
              MAX(o.name) AS name,
              array_agg(DISTINCT TRIM(o.alias)) AS other_names,
              ST_AsGeoJSON(MAX(g.coordinates))::json AS location,
              MAX(e.start_date) AS start_date,
              MAX(e.end_date) AS end_date,
              COUNT(DISTINCT v.id) AS events_count
            {}
        '''.format(base_query)
        
        organizations, query_args = self.appendWhereClauses(organizations, query_args)
        
        organizations = '{} GROUP BY o.id'.format(organizations)

        organizations = self.orderPaginate(organizations)
        
        cursor = connection.cursor()
        cursor.execute(organizations, query_args)
        columns = [c[0] for c in cursor.description]
        
        organizations = [self.makeOrganization(OrderedDict(zip(columns, r))) for r in cursor]
        
        context['results'] = organizations

        return context

class PeopleSearchView(JSONAPIView):
    
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
        'rank': {
            'field': 'rank',
            'operators': ['in'],
            'validator': None,
        },
        'role': {
            'field': 'role',
            'operators': ['in'],
            'validator': None,
        },
        'geonames_id': {
            'field': 'geoname_id',
            'operators': ['eq'],
            'validator': integerValidator,
        },
        # 'events_count': {
        #     'field': 'events_count',
        #     'operators': ['gte', 'lte',],
        #     'validator': integerValidator,
        # },
    }
    
    order_by_fields = {
        'name': {'field': 'name'},
        # 'events_count': {},
        '-name': {'field': 'name'},
        # '-events_count',
    }
    
    required_params = ['q']
    optional_params = ['o', 'p']
    facet_fields = ['rank', 'role']

    def get_context_data(self, **kwargs):
        context = {}
        
        country_code = kwargs['id']
        division_id = 'ocd-division/country:{}'.format(country_code)
        
        query_term = self.request.GET['q']
        
        query_args = [query_term, division_id]
        
        base_query = '''
            FROM person AS p
            JOIN person_person AS pp
              ON p.id = pp.uuid
            JOIN search_index AS si
              ON pp.id = si.object_ref_id
            LEFT JOIN violation AS v
              ON p.id = v.perpetrator_id
            LEFT JOIN membershipperson AS mp
              ON p.id = mp.member_id
            WHERE si.content_type = 'Person'
              AND plainto_tsquery('english', %s) @@ si.content
              AND p.division_id = %s
        '''
        
        context['count'] = 0
        context['facets'] = {}

        for facet, count, facet_count in self.retrieveFacetsCounts(base_query, query_args):
            context['count'] = count
            context['facets'][facet] = facet_count

        query_args = [query_term, division_id]
        
        people = ''' 
            SELECT
              p.id,
              MAX(p.name) AS name,
              array_agg(DISTINCT TRIM(p.alias)) AS other_names,
              COUNT(DISTINCT v.id) AS events_count
              {}
        '''.format(base_query)
        
        people, query_args = self.appendWhereClauses(people, query_args)
        
        people = '{} GROUP BY p.id'.format(people)
        
        people = self.orderPaginate(people)

        cursor = connection.cursor()
        cursor.execute(people, query_args)
        columns = [c[0] for c in cursor.description]
        
        context['results'] = [self.makePerson(OrderedDict(zip(columns, r))) for r in cursor]

        return context

class EventSearchView(JSONAPIView):
    filter_fields = {
        'start_date': {
            'field': 'start_date', 
            'operators': ['gte', 'lte'],
            'validator': dateValidator,
        },
        'geonames_id': {
            'field': 'geoname_id',
            'operators': ['eq'],
            'validator': integerValidator,
        },
        'violation_type': {
            'field': 'violation_type',
            'operators': ['in'],
            'validator': None,
        },
    }
    
    order_by_fields = {
        'start_date': {'field': 'start_date'},
        # 'events_count': {},
        '-start_date': {'field': 'start_date'},
        # '-events_count',
    }
    
    required_params = ['q']
    optional_params = ['o', 'p']
    facet_fields = ['violation_type']
    
    def get_context_data(self, **kwargs):
        context = {}
        
        country_code = kwargs['id']
        division_id = 'ocd-division/country:{}'.format(country_code)
        
        query_term = self.request.GET['q']
        
        query_args = [query_term, division_id]

        base_query = '''
            FROM violation AS v
            JOIN violation_violation AS vv
              ON v.id = vv.uuid
            JOIN search_index AS si
              ON vv.id = si.object_ref_id
            LEFT JOIN person AS p
              ON v.perpetrator_id = p.id
            LEFT JOIN organization AS o
              ON v.perpetrator_organization_id = o.id
            LEFT JOIN geosite AS g
              ON ST_Intersects(ST_Buffer_Meters(v.location, 35000), g.coordinates)
            WHERE si.content_type = 'Violation'
              AND plainto_tsquery('english', %s) @@ si.content
              AND v.division_id = %s
        ''' 
        
        context['count'] = 0
        context['facets'] = {}

        for facet, count, facet_count in self.retrieveFacetsCounts(base_query, query_args):
            context['count'] = count
            context['facets'][facet] = facet_count

        query_args = [query_term, division_id]
        
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
              MAX(p.name) AS perpetrator_name,
              array_agg(DISTINCT TRIM(v.perpetrator_classification)) AS perpetrator_classification,
              array_agg(DISTINCT TRIM(v.violation_type)) AS violation_types,
              array_agg(row_to_json(o.*)) AS perpetrator_organization,
              array_agg(json_build_object('name', g.name,
                                          'id', g.id,
                                          'geometry', ST_AsGeoJSON(g.coordinates)::json)) AS sites_nearby
            {}
        ''' .format(base_query)
        
        events, query_args = self.appendWhereClauses(events, query_args)
        
        events = '{} GROUP BY v.id'.format(events)
        
        events = self.orderPaginate(events)
        
        cursor = connection.cursor()
        
        cursor.execute(events, query_args)
        columns = [c[0] for c in cursor.description]
        events = [self.makeEvent(OrderedDict(zip(columns, r))) for r in cursor]
        
        context['results'] = events

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
        
        when = self.request.GET['at']
        bbox = self.request.GET.get('bbox')
        classification = self.request.GET.get('classification__in')
        
        if classification:
            classifications = classification.split(',')
        
        organizations = ''' 
            SELECT 
              o.id, 
              MAX(o.name) AS name,
              array_agg(DISTINCT TRIM(o.alias)) AS other_names,
              ST_AsGeoJSON(MAX(g.coordinates))::json AS location,
              MAX(e.start_date) AS start_date,
              MAX(e.end_date) AS end_date
            FROM organization AS o
            JOIN emplacement AS e
              ON o.id = e.organization_id
            JOIN geosite as g
              ON e.site_id = g.id
            WHERE o.division_id = %s
              AND (e.start_date <= %s AND e.end_date >= %s)
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
              array_agg(v.violation_type) AS violation_types,
              json_agg(row_to_json(o.*)) AS perpetrator_organization
            FROM violation AS v
            LEFT JOIN person AS p
              ON v.perpetrator_id = p.id
            LEFT JOIN organization AS o
              ON v.perpetrator_organization_id = o.id
            WHERE v.division_id = %s
              AND (v.start_date <= %s AND v.end_date >= %s)
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
              MAX(p.name) AS perpetrator_name,
              array_agg(v.perpetrator_classification) AS perpetrator_classification,
              array_agg(v.violation_type) AS violation_types,
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
              array_agg(v.violation_type) AS violation_types,
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
                array_agg(DISTINCT TRIM(o.alias)) AS other_names
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
