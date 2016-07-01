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

from reversion.models import Version
from extra_views import FormSetView

from source.models import Source, Publication
from organization.models import Organization
from person.models import Person
from cities.models import Place, City, Country, Region, Subregion, District
from violation.models import Violation

SEARCH_CONTENT_TYPES = {
    'Source': Source,
    'Publication': Publication,
    'Organization': Organization,
    'Person': Person,
    'Violation': Violation,
}

GEONAME_TYPES = {
    'country': (Country, 'name',),
    'city': (City, 'name_std',),
    'district': (District, 'name_std',),
    'region': (Region, 'name_std',),
    'subregion': (Subregion, 'name_std',),
}

class Dashboard(TemplateView):
    template_name = 'sfm/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(Dashboard, self).get_context_data(**kwargs)
        
        sources = Version.objects.filter(content_type__model='source').get_unique()
        context['edits'] = sorted(sources, 
                                  key=lambda x: x.revision.date_created, 
                                  reverse=True)
        
        if context['edits']:

            context['source_properties'] = [p for p in \
                                                dir(context['edits'][0].object) \
                                                    if p.endswith('_related')]
            
        session_keys = ['organizations', 'people', 'memberships', 'source_id']
        
        for session_key in session_keys:
            if self.request.session.get(session_key):
                del self.request.session[session_key]
        
        return context



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
        model, field = GEONAME_TYPES[geo_type]
        
        query_kwargs = {'{}__istartswith'.format(field): term}
        
        for result in model.objects.filter(**query_kwargs):
            value = getattr(result, field)
            results.append({
                'text': '{0} ({1})'.format(value, geo_type),
                'value': value,
                'id': result.id,
                'type': geo_type,
            })

    results.sort(key=lambda x:x['text'])
    return HttpResponse(json.dumps(results),content_type='application/json')
