from collections import OrderedDict

from django.db import connection, utils

from api.base_views import JSONAPIView

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
            WHERE v.id = %s
            GROUP BY v.id
        '''

        nearby = '''
              SELECT
                o.id,
                MAX(o.name) AS name,
                array_agg(DISTINCT TRIM(o.alias))
                  FILTER (WHERE TRIM(o.alias) IS NOT NULL) AS other_names
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

        try:
            cursor.execute(event, [kwargs['id']])
        except utils.DataError as e:
            return {'status': 'error', 'message': 'Event with id "{}" not found'.format(kwargs['id'])}

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
            q_args.extend(bbox.split(','))

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

        context['sites'] = [self.makeFeature(r[-1],
                            dict(zip(columns, r))) for r in cursor]

        # Fetch events
        events, nearby_events = self.makeEntityEvents(organization_id,
                                                      when=when,
                                                      bbox=bbox)

        context['events'] = events
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
              array_agg(DISTINCT TRIM(o.alias))
                FILTER (WHERE TRIM(o.alias) IS NOT NULL) AS other_names,
              COUNT(DISTINCT v.id) AS events_count,
              array_agg(DISTINCT TRIM(o.classification))
                FILTER (WHERE TRIM(o.classification) IS NOT NULL) AS classifications
            FROM organization AS o
            LEFT JOIN violation AS v
              ON o.id = v.perpetrator_organization_id,
            LEFT JOIN membershiporganization AS mo
              ON o.id = mo.member_id
            WHERE o.id = %s
            GROUP BY o.id
        '''

        cursor = connection.cursor()

        cursor.execute(query, [organization_id])
        columns = [c[0] for c in cursor.description]

        row = cursor.fetchone()

        if row:
            context.update(self.makeOrganization(OrderedDict(zip(columns, row)),
                                                 relationships=False))
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
        context = {}

        organization_id = kwargs['id']

        query = '''
            SELECT
              o.id,
              MAX(o.name_value) AS name_value,
              MAX(o.name_confidence) AS name_confidence,
              json_agg(o.name_source) AS name_sources,
              array_agg(DISTINCT TRIM(o.alias_value))
                FILTER (WHERE TRIM(o.alias_value) IS NOT NULL) AS other_names_value,
              MAX(o.alias_confidence) AS other_names_confidence,
              json_agg(o.alias_source) AS other_names_sources,
              array_agg(DISTINCT TRIM(o.classification_value))
                FILTER (WHERE TRIM(o.classification_value) IS NOT NULL) AS classifications_value,
              MAX(o.classification_confidence) AS classifications_confidence,
              json_agg(o.classification_source) AS classifications_sources,
              MAX(o.division_id) AS division_id,
              COUNT(DISTINCT v.id) AS events_count,
              COALESCE(MIN(e.start_date::date), MIN(a.start_date::date)) AS first_cited,
              COALESCE(MAX(e.end_date::date), MAX(a.end_date::date)) AS last_cited,
              array_agg(DISTINCT mo.organization_id)
                FILTER (WHERE mo.organization_id IS NOT NULL) AS memberships
            FROM organization_sources AS o
            LEFT JOIN violation AS v
              ON o.id = v.perpetrator_organization_id
            LEFT JOIN emplacement AS e
              ON o.id = e.organization_id
            LEFT JOIN association AS a
              ON o.id = a.organization_id
            LEFT JOIN membershiporganization AS mo
              ON o.id = mo.member_id
            WHERE o.id = %s
            GROUP BY o.id
        '''

        cursor = connection.cursor()
        cursor.execute(query, [organization_id])
        columns = [c[0] for c in cursor.description]

        row = cursor.fetchone()
        if row:
            organization = self.makeOrganization(dict(zip(columns, row)),
                                                 all_geography=True,
                                                 memberships=True)

            context.update(self.splitSources(organization))

            context['parents'] = []
            context['children'] = []

            parents = get_org_hierarchy_by_id(organization_id, sources=True)
            children = get_child_orgs_by_id(organization_id, sources=True)

            for parent in parents:
                parent = self.makeOrganization(parent,
                                               relationships=False,
                                               simple=True,
                                               commanders=False)
                context['parents'].append(parent)

            for child in children:
                child = self.makeOrganization(child,
                                              relationships=False,
                                              simple=True,
                                              commanders=False)
                context['children'].append(child)

            context['people'] = self.makeOrganizationMembers(organization_id)

            events, events_nearby = self.makeEntityEvents(organization_id)
            context['events'] = events
            context['events_nearby'] = events_nearby

        return context


class PersonDetailView(JSONAPIView):
    def get_context_data(self, **kwargs):
        context = {}

        person_id = kwargs['id']

        people = '''
            SELECT
              p.id,
              MAX(p.name_value) AS name_value,
              MAX(p.name_confidence) AS name_confidence,
              json_agg(p.name_source) AS name_sources,
              array_agg(DISTINCT TRIM(p.alias_value))
                FILTER (WHERE TRIM(p.alias) IS NOT NULL) AS other_names_value,
              MAX(p.alias_confidence) AS other_names_confidence,
              json_agg(p.alias_source) AS other_names_sources,
              MAX(p.division_id) AS division_id,
              COUNT(DISTINCT v.id) AS events_count
            FROM person_sources AS p
            LEFT JOIN violation AS v
              ON p.id = v.perpetrator_id
            WHERE p.id = %s
            GROUP BY p.id
        '''
        cursor = connection.cursor()
        cursor.execute(people, [person_id])
        columns = [c[0] for c in cursor.description]

        row = cursor.fetchone()
        if row:
            person = dict(zip(columns, row))

            context.update(self.splitSources(person))

            memberships = '''
                SELECT
                  MAX(member_id::VARCHAR) AS id,
                  organization_id_value AS organization_id_value,
                  MAX(organization_id_confidence) AS organization_id_confidence,
                  json_agg(organization_id_sources) AS organization_id_sources,
                  MAX(name_value) AS organization_name_value,
                  MAX(name_confidence) AS organization_name_confidence,
                  json_agg(name_source) AS organization_name_sources,
                  MAX(role_value) AS role_value,
                  MAX(role_confidence) AS role_confidence,
                  json_agg(role_sources) AS role_sources,
                  MAX(rank_value) AS rank_value,
                  MAX(rank_confidence) AS rank_confidence,
                  json_agg(rank_sources) AS rank_sources,
                  MAX(title_value) AS title_value,
                  MAX(title_confidence) AS title_confidence,
                  json_agg(title_sources) AS title_sources,
                  bool_or(real_start_value) AS real_start_value,
                  MAX(real_start_confidence) AS real_start_confidence,
                  json_agg(real_start_sources) AS real_start_sources,
                  bool_or(real_end_value) AS real_end_value,
                  MAX(real_end_confidence) AS real_end_confidence,
                  json_agg(real_end_sources) AS real_end_sources,
                  MAX(start_context_value) AS start_context_value,
                  MAX(start_context_confidence) AS start_context_confidence,
                  json_agg(start_context_sources) AS start_context_sources,
                  MAX(first_cited_value) AS date_first_cited_value,
                  MAX(first_cited_confidence) AS date_first_cited_confidence,
                  json_agg(first_cited_sources) AS date_first_cited_sources,
                  MAX(last_cited_value) AS date_last_cited_value,
                  MAX(last_cited_confidence) AS date_last_cited_confidence,
                  json_agg(last_cited_sources) AS date_last_cited_sources
                FROM membershipperson_sources AS mp
                JOIN organization_sources AS o
                  ON mp.organization_id_value = o.id
                WHERE member_id = %s
                GROUP BY member_id, organization_id_value
            '''
            cursor.execute(memberships, [person_id])
            columns = [c[0] for c in cursor.description]

            memberships = [self.splitSources(dict(zip(columns, r))) for r in cursor]

            context['memberships'] = memberships

            events, events_nearby = self.makeEntityEvents(person_id,
                                                          entity_type='person')

            context['events'] = events
            context['events_nearby'] = events_nearby

            current_site = '''
                SELECT
                  e.*,
                  ST_AsGeoJSON(g.coordinates)::json AS geometry
                FROM membershipperson AS m
                JOIN emplacement AS e
                  USING(organization_id)
                JOIN geosite AS g
                  ON e.site_id = g.id
                WHERE member_id = %s
                  AND (m.last_cited::date > NOW()::date OR m.last_cited IS NULL)
                  AND (e.end_date::date > NOW()::date OR e.end_date IS NULL)
                LIMIT 1
            '''

            cursor.execute(current_site, [person_id])
            columns = [c[0] for c in cursor.description]

            context['site_present'] = {}

            row = cursor.fetchone()
            if row:
                context['site_present'] = dict(zip(columns, row))

            current_area = '''
                SELECT
                  ass.*,
                  ST_AsGeoJSON(a.geometry)::json AS geometry
                FROM membershipperson AS m
                JOIN association AS ass
                  USING(organization_id)
                JOIN area AS a
                  ON ass.area_id = a.id
                WHERE member_id = %s
                  AND (m.last_cited::date > NOW()::date OR m.last_cited IS NULL)
                  AND (ass.end_date::date > NOW()::date OR ass.end_date IS NULL)
                LIMIT 1
            '''

            cursor.execute(current_area, [person_id])
            columns = [c[0] for c in cursor.description]

            context['area_present'] = {}

            row = cursor.fetchone()
            if row:
                context['area_present'] = dict(zip(columns, row))

        return context
