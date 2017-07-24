from django.shortcuts import render
import pysolr

from django.conf import settings

from source.models import Source, Publication
from organization.models import Organization
from person.models import Person
from violation.models import Violation
from sfm_pc.utils import get_osm_by_id


SEARCH_ENTITY_TYPES = {
#    'Source': Source,
#    'Publication': Publication,
    'Organization': Organization,
    'Person': Person,
    'Violation': Violation,
}

solr = pysolr.Solr(settings.SOLR_URL)

def search(request):

    # Parse request params
    user_query = request.GET.get('q')
    entity_types = request.GET.getlist('entity_type')
    location = request.GET.get('osm_id')
    radius = request.GET.get('radius')

    # Define query string
    if user_query is None or user_query == '':
        full_query = '*'
    else:
        full_query = user_query

    # Restrict the query based on the type of entity the user wants
    if entity_types == []:
        entity_types = [etype for etype in SEARCH_ENTITY_TYPES.keys()]

    for etype in entity_types:
        full_query += ' AND entity_type:{etype}'.format(etype=etype)

    # Start to build the parameters for the Lucene search query
    search_context = {'entity_type': entity_types}

    # Geo filters
    osm = None
    if location and radius:
        fq = '{!geofilt sfield=location}'
        osm = get_osm_by_id(location)
        x, y = osm.st_x, osm.st_y
        pt = '{x} {y}'.format(x=x, y=y)
        sort = 'score asc'
        d = radius

        search_context['fq'] = fq
        search_context['pt'] = pt
        search_context['sort'] = sort
        search_context['d'] = d

    # Search solr
    response = solr.search(full_query, **search_context)

    # Parse the results
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

    context = {
        'results': results,
        'query': user_query,
        'entity_types': entity_types,
        'radius': radius,
        'osm': osm,
        'radius_choices': ['1','5','10','25','50','100'],
    }

    return render(request, 'search/search.html', context)
