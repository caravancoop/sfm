from collections import OrderedDict
import itertools

from django.http import JsonResponse
from django.views.generic import TemplateView
from django.db import connection

from violation.models import Violation

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
              MAX(v.location) AS location,
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
            LEFT JOIN emplacement AS e
              ON o.id = e.organization_id
            LEFT JOIN geosite AS g
              ON e.site_id = g.id
            WHERE v.id = %s
            GROUP BY v.id
        '''

        cursor = connection.cursor()
        
        cursor.execute(event, [kwargs['id']])
        
        columns = [c[0] for c in cursor.description]
        
        # response = OrderedDict([
        #     ('id', kwargs['id']), 
        #     ('division_id', None),
        #     ('start_date, None'),
        #     ('end_date', None), ])

        # for event in cursor:


        events = [OrderedDict(zip(columns, r)) for r in cursor]
        
        # for uuid, event_group in itertools.groupby(events, key=lambda x: x['id']):
        #     group = list(event_group)
        # 
        # perpetrator_name = [r['perpetrator_name'] for r in group if r['perpetrator_name']]
        # perpetrator_classifications = list(set(r['perpetrator_classification'] for r in group))
        # violation_types = list(set([r['violation_type'] for r in group]))

        # resp = group[0]
        # del resp['violation_type']
        # del resp['perpetrator_classification']
        # resp['classification'] = violation_types
        # resp['perpetrator_classification'] = perpetrator_classifications
        # 
        # context.update(resp)
        
        context['events'] = events

        return context
