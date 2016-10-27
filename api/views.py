from django.http import JsonResponse
from django.views.generic import TemplateView

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
        return context
