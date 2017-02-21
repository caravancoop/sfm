from collections import OrderedDict

from django.db import connection

from api.base_views import JSONAPIView, NotImplementedView


class CountryListView(JSONAPIView):

    safe = False
    optional_params = ['tolerance']

    def get_context_data(self, **kwargs):

        tolerance = self.request.GET.get('tolerance', 0.001)

        query = '''
            SELECT
              name,
              country_code AS id,
              json_build_array(json_build_object('lon', ST_XMin(ST_Envelope(geometry)),
                                                 'lat', ST_YMin(ST_Envelope(geometry))),
                               json_build_object('lon', ST_XMax(ST_Envelope(geometry)),
                                                 'lat', ST_YMax(ST_Envelope(geometry)))) AS bbox,
              tags,
              ST_ASGeoJSON(ST_Simplify(geometry, %s))::json AS geometry
            FROM osm_data
            WHERE admin_level = 2
              AND feature_type = 'boundary'
        '''

        cursor = connection.cursor()
        cursor.execute(query, [tolerance])
        columns = [c[0] for c in cursor.description]

        context = [self.makeFeature(r[4], dict(zip(columns, r))) for r in cursor]

        return context


class CountryDetailView(JSONAPIView):

    def get_context_data(self, **kwargs):

        context = {}

        country_code = kwargs['id'].lower()
        division_id = 'ocd-division/country:{}'.format(country_code)

        query = '''
            SELECT
              MAX(c.name) AS name,
              MAX(c.name) AS title,
              NULL::VARCHAR AS description,
              COUNT(DISTINCT v.id) AS events_count
            FROM osm_data AS c, violation AS v
            WHERE c.country_code = %s
              AND c.admin_level = 2
              AND c.feature_type = 'boundary'
              AND v.division_id = %s
            GROUP BY c.id
        '''

        cursor = connection.cursor()
        cursor.execute(query, [country_code, division_id])
        columns = [c[0] for c in cursor.description]

        row = cursor.fetchone()

        if row:

            context = OrderedDict(zip(columns, row))

        return context


class CountryZipView(NotImplementedView):
    pass


class CountryTxtView(NotImplementedView):
    pass


class CountryGeoJSONView(JSONAPIView):

    safe = False
    optional_params = ['tolerance']

    def get_context_data(self, **kwargs):

        country_code = kwargs['id'].lower()

        tolerance = self.request.GET.get('tolerance', 0.001)

        query = '''
            SELECT
              id AS osm_id,
              country_code AS id,
              name,
              ST_AsGeoJSON(ST_Simplify(geometry, %s))::json AS geometry
            FROM osm_data
            WHERE 1=1
        '''

        q_args = [tolerance]

        if country_code != 'xa':
            query = '{} AND country_code = %s'.format(query)
            q_args.append(country_code)

        query = "{} AND feature_type = 'boundary' AND admin_level = 2".format(query)

        cursor = connection.cursor()
        cursor.execute(query, q_args)
        columns = [c[0] for c in cursor.description]

        context = [self.makeFeature(r[3], dict(zip(columns, r))) for r in cursor]

        return context


class CountryGeometryView(JSONAPIView):

    optional_params = ['tolerance', 'classification', 'bbox']

    safe = False

    def get_context_data(self, **kwargs):

        tolerance = self.request.GET.get('tolerance', 0.001)
        classification = self.request.GET.get('classification')
        bbox = self.request.GET.get('bbox')
        
        country_code = self.kwargs['id']

        query = '''
            SELECT
              id AS osm_id,
              country_code AS id,
              name,
              admin_level AS classification,
              ST_AsGeoJSON(ST_Simplify(geometry, %s))::json AS geometry
            FROM osm_data
            WHERE country_code = %s
        '''

        q_args = [tolerance, country_code]

        if classification:
            query = '{} AND admin_level = %s'.format(query)
            q_args.append(classification)

        if bbox:
            query = '''
                {} AND ST_Intersects(geometry,
                                     ST_MakeEnvelope(%s, %s, %s, %s, 4326))
            '''.format(query)
            q_args.extend(bbox.split(','))

        cursor = connection.cursor()
        cursor.execute(query, q_args)
        columns = [c[0] for c in cursor.description]

        context = [self.makeFeature(r[-1], dict(zip(columns, r))) for r in cursor]

        return context


class CountryMapView(JSONAPIView):

    required_params = ['at']
    optional_params = ['bbox', 'tolerance']
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
        tolerance = self.request.GET.get('tolerance', 0.001)

        organizations = '''
            SELECT
              o.id,
              MAX(o.name) AS name,
              array_agg(DISTINCT TRIM(o.alias))
                FILTER (WHERE TRIM(o.alias) IS NOT NULL) AS other_names,
              array_agg(DISTINCT TRIM(o.classification))
                FILTER (WHERE TRIM(o.classification) IS NOT NULL) AS classifications,
              ST_AsGeoJSON(MAX(g.coordinates))::json AS location,
              MAX(e.start_date) AS start_date,
              MAX(e.end_date) AS end_date,
              COUNT(DISTINCT v.id) AS events_count
            FROM organization AS o
            JOIN emplacement AS e
              ON o.id = e.organization_id
            JOIN geosite as g
              ON e.site_id = g.id
            LEFT JOIN violation AS v
              ON o.id = v.perpetrator_organization_id
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
        
        organizations = []

        for row in cursor:
            org_dict = OrderedDict(zip(columns, row))
            organization = self.makeOrganization(org_dict, 
                                                 tolerance=tolerance)

            organizations.append(organization)

        context['organizations'] = [self.makeFeature(o['location'], o) for o in organizations]

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
              MAX(v.division_id) AS division_id,
              ST_ASGeoJSON(MAX(v.location))::json AS location,
              MAX(v.description) AS description,
              MAX(p.name) AS perpetrator_name,
              array_agg(DISTINCT TRIM(v.perpetrator_classification))
                FILTER (WHERE TRIM(v.perpetrator_classification) IS NOT NULL) AS perpetrator_classification,
              array_agg(DISTINCT TRIM(v.violation_type))
                FILTER (WHERE TRIM(v.violation_type) IS NOT NULL) AS classifications,
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

        country_code = kwargs['id'].lower()
        division_id = 'ocd-division/country:{}'.format(country_code)

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
              MAX(v.division_id) AS division_id,
              ST_ASGeoJSON(MAX(v.location))::json AS location,
              MAX(p.name) AS perpetrator_name,
              array_agg(DISTINCT TRIM(v.perpetrator_classification))
                FILTER (WHERE TRIM(v.perpetrator_classification) IS NOT NULL) AS perpetrator_classification,
              array_agg(DISTINCT TRIM(v.violation_type))
                FILTER (WHERE TRIM(v.violation_type) IS NOT NULL) AS classifications,
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
