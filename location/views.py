import overpass
import requests

from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic import ListView
from django.core.urlresolvers import reverse_lazy

from location.models import Location, LocationForm

class LocationView(DetailView):
    model = Location
    template_name = 'location/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class LocationCreate(CreateView):
    form_class = LocationForm
    template_name = 'location/create.html'
    success_url=reverse_lazy('create-location')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    #get osm data
    def get(self, request):
        features = {}
        location_type = request.GET.get('location_type')
        location_name = request.GET.get('location_name')

        if location_type and location_name:
            api = overpass.API()
            overpass_query = location_type + '[\"name\"=\"' + location_name + '\"]'
            # overpass_query = location_type + '(' + location_id + ')'
            response = api.get(overpass_query)
            features = response["features"]

            print(overpass_query)
            print(features)
            # print([(feature['properties']['name'], feature['id']) for feature in response['features']])

        return render(request,'location/create.html', {'features':features})

class LocationList(ListView):
    model = Location
    template_name = 'location/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['locations'] = Location.objects.all()
        return context
