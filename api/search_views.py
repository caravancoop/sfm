from collections import OrderedDict

from django.db import connection

from api.base_views import JSONAPIView, dateValidator, integerValidator


class OrganizationSearchView(JSONAPIView):

    filter_fields = {
        'date_first_cited': {
            'field': 'e.start_date',
            'operators': ['gte', 'lte'],
            'validator': dateValidator,
        },
        'date_last_cited': {
            'field': 'e.end_date',
            'operators': ['gte', 'lte'],
            'validator': dateValidator,
        },
        'classification': {
            'field': 'o.classification',
            'operators': ['in'],
            'validator': None,
        },
        'osm_id': {
            'field': 'osm_id',
            'operators': ['eq'],
            'validator': integerValidator,
        },
    }

    having_fields = {
        'events_count': {
            'field': 'DISTINCT v.id',
            'operators': ['gte', 'lte'],
            'validator': integerValidator,
            'function': 'COUNT',
        },
    }

    order_by_fields = {
        'name': {'field': 'name'},
        'date_first_cited': {'field': 'date_first_cited'},
        'date_last_cited': {'field': 'date_last_cited'},
        'events_count': {'field': 'events_count'},
        '-name': {'field': 'name'},
        '-date_first_cited': {'field': 'date_first_cited'},
        '-date_last_cited': {'field': 'date_last_cited'},
        '-events_count': {'field': 'events_count'},
    }

    required_params = ['q']
    optional_params = ['o', 'p', 'tolerance']

    facet_fields = ['classification']

    def get_context_data(self, **kwargs):
        context = {}

        country_code = kwargs['id'].lower()
        division_id = 'ocd-division/country:{}'.format(country_code)
        
        tolerance = self.request.GET.get('tolerance', 0.001)

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
              array_agg(DISTINCT TRIM(o.alias))
                FILTER (WHERE TRIM(o.alias) IS NOT NULL) AS other_names,
              array_agg(DISTINCT TRIM(o.classification))
                FILTER (WHERE TRIM(o.classification) IS NOT NULL) AS classifications,
              ST_AsGeoJSON(MAX(g.coordinates))::json AS location,
              MAX(e.start_date) AS date_first_cited,
              MAX(e.end_date) AS date_last_cited,
              COUNT(DISTINCT v.id) AS events_count
            {}
        '''.format(base_query)

        organizations, where_args = self.appendWhereClauses(organizations)

        organizations = '{} GROUP BY o.id'.format(organizations)

        organizations, having_args = self.appendHavingClauses(organizations)

        new_args = query_args + having_args + where_args

        organizations = self.orderPaginate(organizations)

        cursor = connection.cursor()

        cursor.execute(organizations, new_args)
        columns = [c[0] for c in cursor.description]
        
        organizations = []
        
        for row in cursor:
            org_dict = OrderedDict(zip(columns, row))
            organization = self.makeOrganization(org_dict, tolerance=tolerance)
            
            organizations.append(organization)

        context['results'] = organizations

        return context


class PeopleSearchView(JSONAPIView):

    filter_fields = {
        'date_first_cited': {
            'field': 'mp.first_cited',
            'operators': ['gte', 'lte'],
            'validator': dateValidator,
        },
        'date_last_cited': {
            'field': 'mp.last_cited',
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
        'osm_id': {
            'field': 'osm_id',
            'operators': ['eq'],
            'validator': integerValidator,
        },
    }

    having_fields = {
        'events_count': {
            'field': 'DISTINCT v.id',
            'operators': ['gte', 'lte'],
            'validator': integerValidator,
            'function': 'COUNT',
        },
    }

    order_by_fields = {
        'name': {'field': 'name'},
        'events_count': {'field': 'events_count'},
        '-name': {'field': 'name'},
        '-events_count': {'field': 'events_count'},
    }

    required_params = ['q']
    optional_params = ['o', 'p']
    facet_fields = ['rank', 'role']

    def get_context_data(self, **kwargs):
        context = {}

        country_code = kwargs['id'].lower()
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
              array_agg(DISTINCT TRIM(p.alias))
                FILTER (WHERE TRIM(p.alias) IS NOT NULL) AS other_names,
              COUNT(DISTINCT v.id) AS events_count
              {}
        '''.format(base_query)

        people, where_args = self.appendWhereClauses(people)

        people = '{} GROUP BY p.id'.format(people)

        people, having_args = self.appendHavingClauses(people)

        new_args = query_args + where_args + having_args

        people = self.orderPaginate(people)

        cursor = connection.cursor()
        cursor.execute(people, new_args)
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
        'osm_id': {
            'field': 'osm_id',
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

        country_code = kwargs['id'].lower()
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
              MAX(v.osmname) AS osm_name,
              MAX(v.osm_id) AS osm_id,
              MAX(p.name) AS perpetrator_name,
              array_agg(DISTINCT TRIM(v.perpetrator_classification))
                FILTER (WHERE TRIM(v.perpetrator_classification) IS NOT NULL) AS perpetrator_classification,
              array_agg(DISTINCT TRIM(v.violation_type))
                FILTER (WHERE TRIM(v.violation_type) IS NOT NULL) AS classifications,
              array_agg(row_to_json(o.*)) AS perpetrator_organization,
              array_agg(json_build_object('name', g.name,
                                          'id', g.id,
                                          'geometry', ST_AsGeoJSON(g.coordinates)::json)) AS sites_nearby
            {}
        ''' .format(base_query)

        events, new_args = self.appendWhereClauses(events)

        new_args = query_args + new_args

        events = '{} GROUP BY v.id'.format(events)

        events = self.orderPaginate(events)

        cursor = connection.cursor()

        cursor.execute(events, new_args)
        columns = [c[0] for c in cursor.description]
        events = [self.makeEvent(OrderedDict(zip(columns, r))) for r in cursor]

        context['results'] = events

        return context
