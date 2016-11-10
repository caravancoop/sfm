from collections import OrderedDict

from django.db import connection

from api.base_views import JSONAPIView, dateValidator, integerValidator

from sfm_pc.utils import get_org_hierarchy_by_id, get_child_orgs_by_id

class OSMAutoView(JSONAPIView):
    
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

        osm = ''' 
            SELECT
              id,
              name,
              alternatenames,
              admin_level AS classification,
              ST_AsGeoJSON(location)::json AS location
            FROM osm_data
            WHERE plainto_tsquery('english', %s) @@ search_index
            AND country_code = %s
        '''
        
        args = [q, kwargs['id']]

        if classification:
            osm = '{} AND admin_level = %s'.format(osm)
            args.append(classification)

        if bbox:
            osm = '''
                {} ST_Within(location,  
                             ST_MakeEnvelope(%s, %s, %s, %s, 4326))
            '''.format(osm)
            args.extend(bbox.split(','))
        
        cursor = connection.cursor()
        cursor.execute(osm, args)
        columns = [c[0] for c in cursor.description]
        
        context = [self.makeFeature(r[4], dict(zip(columns, r))) for r in cursor]

        return context

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
              MAX(v.osmname) AS osm_name,
              MAX(v.osm_id) AS osm_id,
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

class OrganizationMapView(JSONAPIView):
    
    required_params = ['at']
    optional_params = ['bbox']
    filter_fields = {}

    def get_context_data(self, **kwargs):
        context = {}
        
        # Four things: Area, Sites, Events, and Events nearby. All as GeoJSON
        
        organization_id = kwargs['id']
        when = self.request.GET['at']
        bbox = self.request.GET.get('bbox')
        
        q_args = [organization_id, when, when]
        
        if bbox:
            q_args.extend(bbox.split(','))

        area_query = ''' 
            SELECT DISTINCT ON (area.id)
              area.osmid AS id,
              area.name,
              ST_AsGeoJSON(area.geometry)::json AS geometry,
              ass.start_date,
              ass.end_date
            FROM area 
            JOIN association AS ass
              ON area.id = ass.area_id
            WHERE ass.organization_id = %s
              AND (ass.start_date::date <= %s OR ass.end_date::date >= %s)
        '''
        
        if bbox:
            area_query = '''
                {} AND ST_Intersects(area.geometry,  
                                     ST_MakeEnvelope(%s, %s, %s, %s, 4326))
            '''.format(area_query)

        area_query = '{} ORDER BY area.id, ass.end_date DESC, ass.start_date DESC'.format(area_query)
        
        sites_query = ''' 
            SELECT 
              site.osm_id AS id,
              site.name,
              site.osmname AS location,
              site.admin_level_1,
              emplacement.start_date,
              emplacement.end_date,
              ST_AsGeoJSON(site.coordinates)::json AS geometry
            FROM geosite AS site
            JOIN emplacement 
              ON site.id = emplacement.site_id
            WHERE emplacement.organization_id = %s
              AND (emplacement.start_date::date <= %s OR 
                   emplacement.end_date::date >= %s)
        '''
        
        if bbox:
            sites_query = '''
                {} AND ST_Within(site.geometry, ST_MakeEnvelope(%s, %s, %s, %s, 4326))
            '''.format(sites_query)

        events_query = ''' 
            SELECT DISTINCT ON (MAX(o.id::VARCHAR))
              v.id,
              MAX(v.start_date) AS start_date,
              MAX(v.end_date) AS end_date,
              MAX(v.location_description) AS location_description,
              MAX(v.admin_level_1) AS admin_level_1,
              MAX(v.admin_level_2) AS admin_level_2,
              MAX(v.osmname) AS osm_name,
              MAX(v.osm_id) AS osm_id,
              MAX(v.division_id) AS division_id,
              MAX(v.description) AS description,
              MAX(p.name) AS perpetrator_name,
              array_agg(DISTINCT v.perpetrator_classification) AS perpetrator_classification,
              array_agg(DISTINCT v.violation_type) AS violation_types,
              json_agg(row_to_json(o.*)) AS perpetrator_organization,
              ST_ASGeoJSON(MAX(v.location))::json AS location
            FROM violation AS v
            LEFT JOIN person AS p
              ON v.perpetrator_id = p.id
            LEFT JOIN organization AS o
              ON v.perpetrator_organization_id = o.id
        '''
        
        wheres = ''' 
            WHERE o.id = %s
              AND (v.start_date::date <= %s OR v.end_date::date >= %s)
        '''

        if bbox:
            wheres = ''' 
                {} AND ST_Within(v.location, ST_MakeEnvelope(%s, %s, %s, %s, 4326))
            '''.format(wheres)
        
        nearby_events_query = '''
            {0} 
            JOIN violation AS center
              ON ST_Intersects(ST_Buffer_Meters(center.location, 35000), v.location)
            WHERE (center.start_date::date <= %s OR center.end_date >= %s)
              AND v.id != center.id
            GROUP BY v.id
        '''.format(events_query)

        events_query = '''
            {0} {1} GROUP BY v.id
        '''.format(events_query, wheres)

        cursor = connection.cursor()
        
        # Fetch Area
        cursor.execute(area_query, q_args)
        columns = [c[0] for c in cursor.description]
        
        area = cursor.fetchone()
        
        context['area'] = {}
        
        if area:
            area = OrderedDict(zip(columns, area))
            context['area'] = self.makeFeature(area['geometry'], area)
        
        # Fetch sites
        cursor.execute(sites_query, q_args)
        columns = [c[0] for c in cursor.description]
        
        context['sites'] = [self.makeFeature(r[-1], \
                            dict(zip(columns, r))) for r in cursor]

        # Fetch events
        cursor.execute(events_query, q_args)
        columns = [c[0] for c in cursor.description]
        
        events = []
        for event in cursor:
            event = self.makeEvent(dict(zip(columns, event)), simple=True)
            feature = self.makeFeature(event['location'], event)
            events.append(feature)

        context['events'] = events
        
        # Fetch nearby events
        del q_args[0]
        
        cursor.execute(nearby_events_query, q_args)
        columns = [c[0] for c in cursor.description]
        
        event_ids = [e['id'] for e in context['events']]
        events = []
        for event in cursor:
            if event[0] not in event_ids:
                event = self.makeEvent(dict(zip(columns, event)), simple=True)
                feature = self.makeFeature(event['location'], event)
                events.append(feature)
        
        context['events_nearby'] = events

        return context

class OrganizationChartView(JSONAPIView):
    
    required_params = ['at']
    filter_fields = {}

    def get_context_data(self, **kwargs):
        
        context = {}

        organization_id = kwargs['id']
        when = self.request.GET['at']
        
        query = ''' 
            SELECT 
              o.id,
              MAX(o.name) AS name,
              array_agg(DISTINCT o.alias) AS other_names,
              COUNT(DISTINCT v.id) AS events_count,
              array_agg(DISTINCT o.classification) AS classifications
            FROM organization AS o
            LEFT JOIN violation AS v
              ON o.id = v.perpetrator_organization_id
            WHERE o.id = %s
            GROUP BY o.id
        '''
        
        cursor = connection.cursor()

        cursor.execute(query, [organization_id])
        columns = [c[0] for c in cursor.description]
        
        row = cursor.fetchone()
        
        if row:
            context.update(self.makeOrganization(OrderedDict(zip(columns, row)), relationships=False))
            context['parents'] = []
            context['children'] = []
            
            parents = get_org_hierarchy_by_id(organization_id, when=when)
            children = get_child_orgs_by_id(organization_id, when=when)

            for parent in parents:
                parent = self.makeOrganization(parent, 
                                               relationships=False, 
                                               simple=True)
                context['parents'].append(parent)
            
            for child in children:
                child = self.makeOrganization(child, 
                                              relationships=False,
                                              simple=True)
                context['children'].append(child)

        return context

class OrganizationDetailView(JSONAPIView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class PersonDetailView(JSONAPIView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
