import re
import zipfile
import json
from io import BytesIO

import requests

from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic import ListView, DeleteView, TemplateView
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.template.defaultfilters import truncatewords

from countries_plus.models import Country

from api.base_views import JSONResponseMixin

from sfm_pc.templatetags.countries import country_name

from .models import Location
from .forms import LocationForm

class OverpassException(Exception):
    def __init__(self, status_code):
        self.status_code = status_code

    @property
    def message(self):
        if 400 < self.status_code < 500:
            return 'Could not find that relation in Overpass'
        elif 500 < self.status_code:
            return 'Overpass returned an error. Try again later.'


class LocationView(DetailView):
    model = Location
    template_name = 'location/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        related_entities = []
        location = context['location']

        for area in location.associationarea_set.all():
            association = area.object_ref
            organization = association.organization.get_value().value
            entity = {
                'name': organization.name.get_value().value,
                'entity_type': 'Organization',
                'url': reverse('view-organization', kwargs={'slug': organization.uuid}),
                'start_date': association.startdate.get_value(),
                'end_date': association.enddate.get_value(),
                'open_ended': association.open_ended.get_value(),
            }

            related_entities.append(entity)

        for site in location.emplacementsite_set.all():
            emplacement = site.object_ref
            organization = emplacement.organization.get_value().value
            entity = {
                'name': organization.name.get_value().value,
                'entity_type': 'Organization',
                'url': reverse('view-organization', kwargs={'slug': organization.uuid}),
                'start_date': emplacement.startdate.get_value(),
                'end_date': emplacement.enddate.get_value(),
                'open_ended': emplacement.open_ended.get_value(),
            }

            related_entities.append(entity)

        context['related_entities'] = related_entities

        for violation_location in location.violationlocation_set.all():
            violation = violation_location.object_ref

            entity = {
                'name': truncatewords(violation.description.get_value(), 10),
                'entity_type': 'Incident',
                'url': reverse('view-violation', kwargs={'slug': violation.uuid}),
                'start_date': violation.startdate.get_value(),
                'end_date': violation.enddate.get_value(),
                'open_ended': '',
            }

            related_entities.append(entity)

        return context

class LocationDelete(LoginRequiredMixin, DeleteView):
    model = Location
    success_url = reverse_lazy('list-location')
    template_name = 'location/delete.html'


class LocationCreate(LoginRequiredMixin, CreateView):
    form_class = LocationForm
    template_name = 'location/create.html'

    def get_success_url(self):
        return reverse('view-location', kwargs={'pk' : self.object.id})

    def queryOverpass(self, location_type, location_id):
        # search by location ID
        query_fmt = '[out:json];{location_type}({location_id});(._;>;);out;'

        overpass_endpoint = 'https://overpass.kumi.systems/api/interpreter'

        post_data = {
            'data': query_fmt.format(location_type=location_type,
                                     location_id=location_id)
        }

        response = requests.post(overpass_endpoint, data=post_data)

        if response.status_code != 200:
            raise OverpassException(response.status_code)

        feature_collection = {
            'type': 'FeatureCollection',
            'features': []
        }
        all_ids = []

        elements = response.json()

        if location_type == 'node':

            nodes = [e for e in elements['elements'] if e['type'] == 'node']
            all_ids.extend([f['id'] for f in nodes])

        if location_type == 'way':
            ways = [e for e in elements['elements'] if e['type'] == 'way']
            all_ids.extend([f['id'] for f in ways])

        if location_type == "relation":
            relations = [e for e in elements['elements'] if e['type'] == 'relation']
            all_ids.extend([f['id'] for f in relations])

        saved_location_ids = [l.id for l in Location.objects.filter(id__in=all_ids)]

        for feature in elements['elements']:

            if feature['type'] == location_type:
                feature['tags']['saved'] = 'no'

                if int(feature['id']) in saved_location_ids:
                    feature['tags']['saved'] = 'yes'

                feature['form_tags'] = json.dumps(feature['tags'])

        return elements

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['countries'] = Country.objects.all()

        if self.request.method == 'GET':
            location_type = self.request.GET.get('location_type')
            location_id = self.request.GET.get('location_id')

            if location_id and location_type:
                context['features'] = self.queryOverpass(location_type,
                                                         location_id)
                context['json_features'] = json.dumps(context['features'])
                context['feature_count'] = len(context['features']['elements'])

                context['location_type'] = location_type
                context['location_id'] = int(location_id)

        return context


class LocationList(ListView):
    model = Location
    template_name = 'location/list.html'
    per_page = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results'] = Location.objects.all()

        if self.request.method == 'GET':
            query = self.request.GET.get('q')
            sort = self.request.GET.get('sort')
            page = self.request.GET.get('page', default=1)

            if query:
                context['results'] = Location.objects.filter(Q(name__icontains=query) | Q(id__startswith=query))
                context['query'] = query

            if sort:
                context['results'] = context['results'].order_by(sort)
                context['sort'] = sort

            paginator = Paginator(context['results'], self.per_page)
            context['page'] = int(page)
            context['pages'] = int(paginator.num_pages)

            try:
                context['results'] = paginator.page(page)
            except PageNotAnInteger:
                context['results'] = paginator.page(1)
            except EmptyPage:
                context['results'] = paginator.page(paginator.num_pages)

        context['paginator'] = paginator
        context['hits'] = paginator.count
        return context


class LocationAutoComplete(JSONResponseMixin, TemplateView):
    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        query = self.request.GET.get('q')

        results = Location.objects.filter(Q(name__icontains=query) | Q(id__startswith=query))

        if self.request.GET.get('feature_type'):
            feature_type = self.request.GET['feature_type']
            results = results.filter(feature_type=feature_type)

        context = {
            'results': []
        }

        for result in results:
            location = {
                'id': result.id,
                'text': '{}, {} ({} - {})'.format(result.name,
                                                  country_name(result.division_id),
                                                  result.feature_type,
                                                  result.id)
            }
            context['results'].append(location)

        return context
