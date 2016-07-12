import json
from uuid import uuid4

from django.views.generic.base import TemplateView
from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic.edit import FormView
from django.forms import formset_factory
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.shortcuts import redirect, render
from django.contrib import messages
from django.utils.translation import get_language
from django.db import connection
from django.core.urlresolvers import reverse_lazy
from django.conf import settings

from reversion.models import Version
from extra_views import FormSetView

from source.models import Source, Publication
from organization.models import Organization
from person.models import Person
from cities.models import Place, City, Country, Region, Subregion, District
from violation.models import Violation
from sfm_pc.templatetags.render_from_source import get_relations, \
    get_relation_attributes
from complex_fields.models import CONFIDENCE_LEVELS
from sfm_pc.utils import import_class

SEARCH_CONTENT_TYPES = {
    'Source': Source,
    'Publication': Publication,
    'Organization': Organization,
    'Person': Person,
    'Violation': Violation,
}

GEONAME_TYPES = {
    'country': (Country, 'Country',),
    'city': (City, None, ),
    'district': (District, 'PPLX',),
    'region': (Region, 'ADM1',),
    'subregion': (Subregion, 'ADM2',),
}

class Dashboard(TemplateView):
    template_name = 'sfm/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        sources = Version.objects.filter(content_type__model='source').get_unique()
        context['edits'] = sorted(sources, 
                                  key=lambda x: x.revision.date_created, 
                                  reverse=True)
        
        if context['edits']:
            
            context['source_properties'] = get_relations(context['edits'][0].object)
            
        session_keys = ['organizations', 'people', 'memberships', 'source_id']
        
        for session_key in session_keys:
            if self.request.session.get(session_key):
                del self.request.session[session_key]
        
        return context

class SetConfidence(TemplateView):
    template_name = 'sfm/set-confidences.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            source_id = self.request.session['source_id']
        except KeyError:
            source_id = self.request.GET['source_id']

        source = Source.objects.get(id=source_id)
        context['source'] = source
        context['relations'] = []
        
        relation_properties = get_relations(context['source'])
        
        for rel_prop in relation_properties:
            props = getattr(source, rel_prop).all()
            
            if props:
                for prop in props:
                    attributes = get_relation_attributes(prop)
                    
                    additional_sources = prop.sources.exclude(id=source_id)
                    for s in additional_sources:
                        revision = Version.objects.get_for_object(s).first()
                        
                        user_data = {
                            'user': revision.revision.user,
                            'source': s
                        }

                        try:
                            attributes['additional_sources'].append(user_data)
                        except KeyError:
                            attributes['additional_sources'] = [user_data]

                    attributes['relation_id'] = prop.id
                    context['relations'].append(attributes)
        
        context['relations'] = sorted(context['relations'], 
                                      key=lambda x: x['object_ref_object_name'])

        context['confidence_choices'] = CONFIDENCE_LEVELS

        return context
    
    def post(self, request, *args, **kwargs):
        
        confidence_keys = [k for k in request.POST.keys() if k.startswith('confidence-')]
        
        updates = {}
        for key in confidence_keys:
            relation_label, relation_id, object_ref_object, object_ref_id = key.rsplit('-', 3)
            app_name, relation_object = relation_label.replace('confidence-', '').split('.')

            import_path = '{app_name}.models.{obj}'

            relation_path = import_path.format(app_name=app_name,
                                               obj=relation_object)
            relation_model = import_class(relation_path)
            relation_instance = relation_model.objects.get(id=relation_id)
            
            confidence = int(request.POST[key])
            if relation_instance.confidence != confidence:
                relation_instance.confidence = confidence
                relation_instance.save()

        return redirect(reverse_lazy('dashboard'))

def search(request):
    query = request.GET.get('q')
    filters = request.GET.getlist('entity_type')
    location = request.GET.get('geoname_id')
    radius = request.GET.get('radius')
    geoname_type = request.GET.get('geoname_type')

    results = {}
    select = ''' 
        SELECT DISTINCT ON(content_type, object_ref_id) 
          content_type,
          value_type,
          object_ref_id
        FROM search_index
        WHERE 1=1 
    '''
    
    params = []

    
    if query:
        
        select = ''' 
            {select}
            AND plainto_tsquery('english', %s) @@ content
        '''.format(select=select)
        
        params = [query]

    if filters:
        filts = ' OR '.join(["content_type = '{}'".format(f) for f in filters])
        select = ''' 
            {select}
            AND ({filts})
        '''.format(select=select, filts=filts)
    
    geoname_obj = None
    if location and radius and geoname_type:

        # TODO: Make this work for areas once we have them
        model, _ = GEONAME_TYPES[geoname_type]
        geoname_obj = model.objects.get(id=location)
        select = ''' 
            {select}
            AND ST_Intersects(ST_Buffer_Meters(ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326), {radius}), site)
        '''.format(select=select,
                   lon=geoname_obj.location.x,
                   lat=geoname_obj.location.y,
                   radius=(int(radius) * 1000))

    select = ''' 
        {select} 
        ORDER BY content_type, object_ref_id
    '''.format(select=select)
        
    cursor = connection.cursor()
        
    cursor.execute(select, params)
    
    result_types = {}
    
    for result in cursor:
        content_type, value_type, object_ref_id = result
        
        try:
            result_types[content_type].append(object_ref_id)
        except KeyError:
            result_types[content_type] = [object_ref_id]

    for content_type, objects in result_types.items():
        model = SEARCH_CONTENT_TYPES[content_type]
        results[content_type] = model.objects.filter(id__in=objects)
    
    context = {
        'results': results, 
        'query': query, 
        'filters': filters,
        'radius': radius,
        'geoname': geoname_obj,
        'geoname_type': geoname_type,
        'radius_choices': ['1','5','10','25','50','100'],
    }

    return render(request, 'sfm/search.html', context)

def geoname_autocomplete(request):
    term = request.GET.get('q')
    types = request.GET.getlist('types')

    if not types:
        types = request.GET.getlist('types[]', GEONAME_TYPES.keys())
    
    results = []
    for geo_type in types:
        model, code = GEONAME_TYPES[geo_type]
        
        query_kwargs = {'name__istartswith': term}
        
        for result in model.objects.filter(**query_kwargs):
            
            hierarchy = result.hierarchy
            hierarchy.reverse()

            value = ', '.join(m.name for m in hierarchy)

            map_image = None

            if hasattr(result, 'location'):
                latlng = '{0},{1}'.format(result.location.y, result.location.x)
                map_image = 'https://maps.googleapis.com/maps/api/staticmap'
                map_image = '{0}?center={1}&zoom=10&size=100x100&key={2}&scale=2'.format(map_image,
                                                                                         latlng,
                                                                                         settings.GOOGLE_MAPS_KEY)
            
            if geo_type == 'city':
                code = result.kind

            results.append({
                'text': '{0} (GeonameID: {1}, {2})'.format(value, result.id, code),
                'value': value,
                'id': result.id,
                'type': geo_type,
                'map_image': map_image,
                'code': code,
            })

    results.sort(key=lambda x:x['text'])
    return HttpResponse(json.dumps(results),content_type='application/json')
