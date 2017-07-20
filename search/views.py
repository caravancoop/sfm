from django.shortcuts import render
import pysolr

from django.conf import settings

from source.models import Source, Publication
from organization.models import Organization
from person.models import Person
from violation.models import Violation


SEARCH_ENTITY_TYPES = {
    'Source': Source,
    'Publication': Publication,
    'Organization': Organization,
    'Person': Person,
    'Violation': Violation,
}

solr = pysolr.Solr(settings.SOLR_URL)

def search(request):
    query = request.GET.get('q')
    filters = request.GET.getlist('entity_type', ['*'])
    location = request.GET.get('osm_id', '*')
    radius = request.GET.get('radius', '*')

    response = solr.search(query, **{
        'entity_type': filters,
        'location': location,
    })

    result_types = {}

    for result in response:

        entity_type = result['entity_type']
        object_ref_id = result['id']

        try:
            result_types[entity_type].append(object_ref_id)
        except KeyError:
            result_types[entity_type] = [object_ref_id]

    results = {}

    for entity_type, objects in result_types.items():

        model = SEARCH_ENTITY_TYPES[entity_type]
        results[entity_type] = model.objects.filter(uuid__in=objects)

    osm = None

    context = {
        'results': results,
        'query': query,
        'filters': filters,
        'radius': radius,
        'osm': osm,
        'radius_choices': ['1','5','10','25','50','100'],
    }

    return render(request, 'search/search.html', context)
