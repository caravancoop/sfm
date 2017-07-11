from django.shortcuts import render

from search.search import Searcher

# SEARCH_CONTENT_TYPES = {
#     'Source': Source,
#     'Publication': Publication,
#     'Organization': Organization,
#     'Person': Person,
#     'Violation': Violation,
# }

def search(request):
    query = request.GET.get('q')
    filters = request.GET.getlist('entity_type')
    location = request.GET.get('osm_id')
    radius = request.GET.get('radius')

    # result_types = {}

    # for result in cursor:
    #     content_type, value_type, object_ref_id = result

    #     try:
    #         result_types[content_type].append(object_ref_id)
    #     except KeyError:
    #         result_types[content_type] = [object_ref_id]

    # for content_type, objects in result_types.items():
    #     model = SEARCH_CONTENT_TYPES[content_type]
    #     results[content_type] = model.objects.filter(id__in=objects)

    context = {
        'results': results,
        'query': query,
        'filters': filters,
        'radius': radius,
        'osm': osm,
        'radius_choices': ['1','5','10','25','50','100'],
    }

    return render(request, 'search/search.html', context)
