import re
import zipfile
import json
from io import BytesIO

import overpass
import overpy
import requests

from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic import ListView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

from countries_plus.models import Country

from .models import Location
from .forms import LocationForm

class LocationView(DetailView):
    model = Location
    template_name = 'location/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class LocationDelete(LoginRequiredMixin, DeleteView):
    model = Location
    success_url = reverse_lazy('list-location')
    template_name = 'location/delete.html'


class LocationCreate(LoginRequiredMixin, CreateView):
    form_class = LocationForm
    template_name = 'location/create.html'
    # success_url = reverse_lazy('list-location')
    def get_success_url(self):
        return reverse('view-location', kwargs={'pk' : self.object.id})

    def queryOverpass(self, location_type, location_country, location_name):
        # search by location type, country, and name
        # query_fmt = 'area["ISO3166-1"="{location_country}"];{location_type}(area)["name"~"^{location_name}",i];(._;>;);out;'

        # search by location type, country, name, and english name
        query_fmt = 'area["ISO3166-1"="{location_country}"];{location_type}(area)[~"^nam[e|e:en]"~"^{location_name}",i];(._;>;);out;'

        # search by location type and name
        # query_fmt = '{location_type}[~"^nam[e|e:en]"~"^{location_name}",i];(._;>;);out;'

        overpass_endpoint = 'https://overpass.kumi.systems/api/interpreter'
        api = overpy.Overpass(url=overpass_endpoint)
        query = query_fmt.format(location_type=location_type,
                                 location_country=location_country,
                                 location_name=location_name)

        response = api.query(query)

        feature_collection = {
            'type': 'FeatureCollection',
            'features': []
        }
        all_ids = []

        if location_type == 'node':
            for feature in response.nodes:
                feat = {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [float(feature.lon), float(feature.lat)],
                    },
                    'properties': feature.tags,
                }
                feat['properties']['id'] = feature.id
                feature_collection['features'].append(feat)
                all_ids.append(feature.id)

        if location_type == "rel":

            relation_ids = [str(r.id) for r in response.relations]
            all_ids.extend(relation_ids)

            wambacher = 'https://wambachers-osm.website/boundaries'
            query_params = {
                'selected': ','.join(relation_ids),
                'cliVersion': '1.0',
                'cliKey': settings.OSM_API_KEY,
                'exportFormat': 'json',
            }

            relations = requests.get('{}/exportBoundaries'.format(wambacher), params=query_params)

            try:
                with zipfile.ZipFile(BytesIO(relations.content)) as zf:

                    for filename in zf.namelist():

                        if 'GeoJson' in filename:

                            with zf.open(filename) as geojson:

                                geojson_cleaned = re.sub(r'""(?!,)', '', geojson.read().decode('utf-8'))
                                relation_data = json.loads(geojson_cleaned)
                                feature_collection['features'].extend(relation_data['features'])
            except zipfile.BadZipFile:
                pass

        saved_location_ids = [l.id for l in Location.objects.filter(id__in=all_ids)]

        for feature in feature_collection['features']:
            is_in = [v for k, v in feature['properties'].items() if k.startswith('is_in')]
            feature['properties']['is_in'] = ','.join(is_in).replace(',', ', ')
            feature['json_properties'] = json.dumps(feature['properties'])
            feature['properties']['saved'] = 'no'

            if int(feature['properties']['id']) in saved_location_ids:
                feature['properties']['saved'] = 'yes'

        return feature_collection

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['countries'] = Country.objects.all()

        if self.request.method == 'GET':
            location_type = self.request.GET.get('location_type')
            location_country = self.request.GET.get('location_country')
            location_name = self.request.GET.get('location_name')

            if location_name and location_type and location_country:
                try:
                    context['features'] = self.queryOverpass(location_type,
                                                             location_country,
                                                             location_name)
                    context['feature_count'] = len(context['features']['features'])
                except overpy.exception.OverpassTooManyRequests as e:
                    print (e)
                    context['overpass_error'] = True

            context['location_type'] = location_type
            context['location_country'] = location_country
            context['location_name'] = location_name

        return context


class LocationList(ListView):
    model = Location
    template_name = 'location/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['locations'] = Location.objects.all()
        return context
