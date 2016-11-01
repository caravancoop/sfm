from collections import OrderedDict
import itertools

from django.http import JsonResponse
from django.views.generic import TemplateView
from django.db import connection

from violation.models import Violation
from sfm_pc.utils import get_org_hierarchy_by_id

class JSONResponseMixin(object):
    def render_to_json_response(self, context, **response_kwargs):
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        del context['view']
        # Make sure things are JSON serializable
        return context

class JSONAPIView(JSONResponseMixin, TemplateView):
    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)
        
    def makeFeature(self, geometry, properties):
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
            if org['id'] not in perp_org_ids:
                structured_org = self.makeOrganization(org, relationships=False)
                
                perp_orgs.append(structured_org)
                perp_org_ids.append(org['id'])

        properties['perpetrator_organization'] = perp_orgs
        return properties


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
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

class CountryEventsView(JSONAPIView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        

        return context

class EventDetailView(JSONAPIView):
    """ 
    {
      "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "division_id": "ocd-division/country:ng",
      "start_date": "2010-01-01",
      "end_date": null,
      "location": "...",
      "geonames_name": "Aba North",
      "admin_level_1_geonames_name": "Abia",
      "classification": [
        "Torture",
        "Disappearance"
      ],
      "description": "...",
      "perpetrator_name": "Terry Guerrier",
      "perpetrator_organization": {
        "id": "42bb1cff-eed5-4458-a9b4-b00bad09f615",
        "name": "Brigade 1",
        "other_names": [
          "Power Rangers"
        ]
      },
      "organizations_nearby": [
        {
          "id": "123e4567-e89b-12d3-a456-426655440000",
          "name": "Brigade 2",
          "other_names": [
            "The Planeteers"
          ],
          "root_id": "98185305-7ac0-4f7d-b354-efb052d1d3f1",
          "root_name": "Nigerian Army",
          "person_name": "Michael Maris",
          "events_count": 12
        },
        ...
      ]
    }
    """

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
