import json
from uuid import uuid4
from collections import OrderedDict

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
from django.contrib.auth.models import User

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
from sfm_pc.utils import import_class, get_geoname_by_id

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
        
        source_count_q = 'SELECT COUNT(*) AS count, user_id FROM source_source'

        c = connection.cursor()
        c.execute('{} GROUP BY user_id'.format(source_count_q), [])
        
        for row in c:
            context['count_by_user'] = {
                User.objects.get(id=row[1]): {
                    'all_source_count': row[0],
                },
            }

        c.execute('''
            {} WHERE age(now(), date_added) <= make_interval(weeks := 1) 
               GROUP BY user_id
        '''.format(source_count_q), [])
        
        for row in c:
            context['count_by_user'][User.objects.get(id=row[1])]['last_week_count'] = row[0]
        
        c.execute('''
            {} WHERE age(now(), date_added) <= make_interval(months := 1) 
               GROUP BY user_id
        '''.format(source_count_q), [])

        for row in c:
            context['count_by_user'][User.objects.get(id=row[1])]['last_month_count'] = row[0]
        
        entity_type_counts = ''' 
            SELECT COUNT(*), d.value 
            FROM {0}_{0} AS o 
            JOIN {0}_{0}divisionid AS d 
              ON o.id = d.object_ref_id 
            GROUP BY d.value
        '''
        
        context['counts'] = {}

        for entity_type in ['organization', 'person', 'violation']:
            c.execute(entity_type_counts.format(entity_type), [])
            
            for row in c:

                try:
                    context['counts'][row[1]][entity_type] = row[0]
                except KeyError:
                    context['counts'][row[1]] = {entity_type: row[0]}
        
        c.execute(''' 
            SELECT g.value, array_agg(o.object_ref_id)
            FROM emplacement_emplacementorganization AS o 
            JOIN emplacement_emplacement AS e 
              ON o.object_ref_id = e.id 
            JOIN emplacement_emplacementsite AS s 
              ON e.id = s.object_ref_id 
            JOIN geosite_geosite AS gs 
              ON s.value_id = gs.id 
            JOIN geosite_geositegeonameid AS g 
              ON gs.id = g.object_ref_id 
            GROUP BY g.value 
            HAVING(COUNT(*)>1) 
            ORDER BY COUNT(*) DESC
            LIMIT 5
        ''', [])
        
        context['org_geo_counts'] = OrderedDict()
        for row in c:
            context['org_geo_counts'][get_geoname_by_id(row[0])] = [Organization.objects.get(id=i) for i in row[1]]
        
        c.execute(''' 
            SELECT g.value, array_agg(v.id) 
            FROM violation_violation AS v 
            JOIN violation_violationgeonameid AS g 
              ON v.id = g.object_ref_id
            GROUP BY g.value 
            HAVING(COUNT(*)>1) 
            ORDER BY COUNT(*) DESC 
            LIMIT 5;
        ''')
        
        context['event_geo_counts'] = OrderedDict()
        for row in c:
            context['event_geo_counts'][get_geoname_by_id(row[0])] = [Violation.objects.get(id=i) for i in row[1]]

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
        context['relations'] = OrderedDict()
        
        relation_properties = get_relations(context['source'])
        
        for rel_prop in relation_properties:
            props = getattr(source, rel_prop).all()
            
            if props:
                for prop in props:
                    
                    attributes = get_relation_attributes(prop)
                    
                    additional_sources = prop.sources.exclude(id=source_id)
                    for s in additional_sources:
                        revision = Version.objects.get_for_object(s).first()
                        
                        user_data = {}
                        
                        if revision:
                            user_data['user'] = revision.revision.user
                            user_data['source'] = s

                        try:
                            attributes['additional_sources'].append(user_data)
                        except KeyError:
                            attributes['additional_sources'] = [user_data]

                    attributes['relation_id'] = prop.id
                    
                    title = '{0} ({1})'.format(prop.object_ref._meta.object_name, 
                                               prop.object_ref.get_value())
                    
                    try:
                        context['relations'][prop.object_ref]['attributes'].append(attributes)
                        context['relations'][prop.object_ref]['title'] = title
                    except KeyError:
                        context['relations'][prop.object_ref] = {
                            'attributes': [attributes],
                            'title': title,
                        }
        
        context['relations'] = OrderedDict(sorted(context['relations'].items(), 
                                           key=lambda x: x[0]._meta.object_name))

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

    if not query:
        select = ''' 
            {select}
            LIMIT 100
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

def division_autocomplete(request):
    term = request.GET.get('q')
    countries = Country.objects.filter(name__icontains=term)

    results = []
    for country in countries:
        results.append({
            'text': '{0} (ocd-division/country:{1})'.format(str(country.name), country.code.lower()),
            'id': 'ocd-division/country:{}'.format(country.code.lower()),
        })
    return HttpResponse(json.dumps(results), content_type='application/json')
