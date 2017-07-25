from django.shortcuts import render
import pysolr

from django.conf import settings

from source.models import Source, Publication
from organization.models import Organization
from person.models import Person
from violation.models import Violation
from sfm_pc.utils import get_osm_by_id


DEFAULT_RESULT_COUNT = 10

SEARCH_ENTITY_TYPES = {
#    'Source': Source,
#    'Publication': Publication,
    'Organization': Organization,
    'Person': Person,
    'Violation': Violation,
}

solr = pysolr.Solr(settings.SOLR_URL)

def search(request):

    # Parse standard request params
    user_query = request.GET.get('q')
    entity_types = request.GET.getlist('entity_type')
    location = request.GET.get('osm_id')
    radius = request.GET.get('radius')

    # Define query string
    if user_query is None or user_query == '':
        full_query = '*'
    else:
        full_query = user_query

    search_context = {'rows': DEFAULT_RESULT_COUNT}

    # Configure geofilters
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

    # Make sure to handle empty entity types
    if entity_types is None or entity_types == '' or entity_types == []:
        entity_types = [etype for etype in SEARCH_ENTITY_TYPES.keys()]

    # Search solr
    results = {}
    pages = {}
    for etype in entity_types:

        pages[etype] = {}
        pagination = request.GET.get(etype + '_page')

        if pagination is not None:
            pagination = int(pagination)
            start = (pagination - 1) * DEFAULT_RESULT_COUNT
            if pagination > 1:
                pages[etype]['has_previous'] = True
                pages[etype]['previous_page_number'] = pagination - 1
        else:
            pagination = 1
            start = 0
            pages[etype]['has_previous'] = False

        search_context['start'] = start

        etype_query = full_query + ' AND entity_type:{etype}'.format(etype=etype)
        response = solr.search(etype_query, **search_context)

        if response.hits > DEFAULT_RESULT_COUNT:
            pages[etype]['has_next'] = True
            pages[etype]['next_page_number'] = pagination + 1
        else:
            pages[etype]['has_next'] = False

        object_ids = [result['id'] for result in response]

        if len(object_ids) > 0:
            model = SEARCH_ENTITY_TYPES[etype]
            results[etype] = model.objects.filter(uuid__in=object_ids)

    context = {
        'results': results,
        'query': user_query,
        'entity_types': entity_types,
        'radius': radius,
        'osm': osm,
        'radius_choices': ['1','5','10','25','50','100'],
        'pages': pages
    }

    return render(request, 'search/search.html', context)

