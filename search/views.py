import urllib

from django.shortcuts import render
from django.conf import settings
import pysolr

from source.models import Source, Publication
from organization.models import Organization
from person.models import Person
from violation.models import Violation
from sfm_pc.utils import get_osm_by_id, format_facets


SEARCH_ENTITY_TYPES = {
#    'Source': Source,
#    'Publication': Publication,
    'Organization': {
        'model': Organization,
        'facet_fields': ['organization_classification_ss'],
        'facet_ranges': ['organization_start_date_dt',
                         'organization_end_date_dt'],
    },
    'Person': {
        'model': Person,
        'facet_fields': ['person_current_role_s',
                         'person_current_rank_s'],
        'facet_ranges': ['person_first_cited_dt',
                         'person_last_cited_dt'],
    },
    'Violation': {
        'model': Violation,
        'facet_fields': ['violation_type_ss',
                         'perpetrator_classification_ss',
                         'violation_location_description_ss'],
        'facet_ranges': ['violation_start_date_dt',
                         'violation_end_date_dt'],
    }
}

solr = pysolr.Solr(settings.SOLR_URL)

def search(request):

    # Parse standard request params
    user_query = request.GET.get('q')
    entity_types = request.GET.getlist('entity_type')
    location = request.GET.get('osm_id')
    radius = request.GET.get('radius')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # Parse selected facets
    selected_facet_vals = request.GET.getlist('selected_facets')
    selected_facets = {}
    for val in selected_facet_vals:
        if val:
            [k, v] = val.split('_exact:', 1)
            try:
                selected_facets[k].append(v)
            except KeyError:
                selected_facets[k] = [v]

    # Make sure to handle empty entity types
    if entity_types in (None, '', [], ['']):
        entity_types = [etype for etype in SEARCH_ENTITY_TYPES.keys()]

    # Re-format the query string for use in templating
    q_filters = ''
    url_params = [(p, val) for (p, val) in request.GET.items()
                  if '_page' not in p and p != 'selected_facets'
                  and p != 'entity_type' and p != 'amp' and p != '_']

    for facet_val in selected_facet_vals:
        url_params.append(('selected_facets', facet_val))

    for etype in entity_types:
        url_params.append(('entity_type', etype))

    if url_params:
        q_filters = urllib.parse.urlencode(url_params)

    # Define query string
    if user_query is None or user_query == '':
        full_query = '*'
    else:
        full_query = user_query

    # Filter on date params, if they exist; otherwise, don't bother
    if start_date or end_date:

        # Lucene needs us to replace missing params with *
        formatted_start = start_date
        formatted_end = end_date

        # Turn dates into a Lucene-readable timestamp
        if formatted_start in ('', None):
            formatted_start = '*'
        else:
            formatted_start += 'T00:00:00Z'

        if formatted_end in ('', None):
            formatted_end = '*'
        else:
            formatted_end += 'T00:00:00Z'

        if start_date and end_date:
            # In this case, we want results where there is complete overlap
            # between the dates set by the filter range and the first/last
            # cited. We also want to include records where `end_date` is empty:
            #   * (rec.start < q.start) AND (rec.end > q.end)

            full_query += ' AND start_date_dt:[* TO {start_date}]' +\
                          ' AND end_date_dt:[{end_date} TO *]'

            full_query = full_query.format(start_date=formatted_start,
                                           end_date=formatted_end)

        elif start_date:
            # Show records for which there is data on or after `start_date`.
            # Include records where `start_date` is empty:
            #   * (rec.start > q.start) OR (rec.end > q.start AND !rec.start)

            full_query += ' AND (start_date_dt:[{start_date} TO *]' +\
                          ' OR (end_date_dt:[{start_date} TO *]' +\
                           ' AND -start_date_dt:[* TO *]))'

            full_query = full_query.format(start_date=formatted_start)

        elif end_date:
            # Show records for which there is no data on or after `end_date`
            # (that is, exclude records for which there *is* data
            # after `end_date`). Include records where `end_date` is empty:
            #   * (rec.end < q.end) OR (rec.start < q.end AND !rec.end)

            full_query += ' AND (end_date_dt:[* TO {end_date}]' +\
                               ' OR (start_date_dt:[* TO {end_date}]' +\
                              ' AND -end_date_dt:[* TO *]))'\

            full_query = full_query.format(end_date=formatted_end)

    # Set limits for search pagination
    if len(entity_types) < 2:
        result_count = 10
    else:
        result_count = 5

    # Initialize extra Solr params with the default row count and facets on
    search_context = {'rows': result_count, 'facet': 'on'}

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

    # Search solr
    results = {}  # Model info
    pages = {}  # Pagination info
    facets = {etype: [] for etype in entity_types}  # Facet counts
    hits = {}  # Result counts
    for etype in entity_types:

        # Copy the query so we can modify it in the scope of this iteration
        etype_query = full_query

        print(etype_query)
        # Add facets to the query
        search_context['facet.field'] = SEARCH_ENTITY_TYPES[etype]['facet_fields']
        search_context['facet.range'] = SEARCH_ENTITY_TYPES[etype]['facet_ranges']
        search_context['facet.range.start'] = '2000-01-01T00:00:00Z/YEAR'
        search_context['facet.range.end'] = 'NOW/YEAR'
        search_context['facet.range.gap'] = '+1YEAR'

        # Handle pagination
        pages[etype] = {}
        pagination = request.GET.get(etype + '_page')

        if pagination is not None:
            pagination = int(pagination)
            start = (pagination - 1) * result_count
            if pagination > 1:
                pages[etype]['has_previous'] = True
                pages[etype]['previous_page_number'] = pagination - 1
        else:
            pagination = 1
            start = 0
            pages[etype]['has_previous'] = False

        search_context['start'] = start

        # Filter on selected facets and entity type
        for field, values in selected_facets.items():
            if field in search_context['facet.field']:
                for val in values:
                    etype_query += ' AND {field}:"{val}"'.format(field=field,
                                                                 val=val)
            # Handle date ranges
            elif field in search_context['facet.range']:
                for val in values:

                    # Increment the year to define an end date
                    start = val
                    start_year = int(start[:4])
                    end_year = start_year + 1
                    end = str(end_year) + start[4:]

                    etype_query += ' AND {field}:["{start}" TO "{end}"]'\
                                   .format(field=field,
                                           start=start,
                                           end=end)

        # Make sure to filter on this entity type
        etype_query += ' AND entity_type:{etype}'.format(etype=etype)

        # Search that bad boy!
        response = solr.search(etype_query, **search_context)

        if response.hits > result_count:
            pages[etype]['has_next'] = True
            pages[etype]['next_page_number'] = pagination + 1
        else:
            pages[etype]['has_next'] = False

        hits[etype] = response.hits
        facets[etype] = format_facets(response.facets)

        # Pull models from the DB based on search results
        object_ids = [result['id'] for result in response]
        if len(object_ids) > 0:
            model = SEARCH_ENTITY_TYPES[etype]['model']
            results[etype] = model.objects.filter(uuid__in=object_ids)

    # Determine total result count
    hits['global'] = sum(count for count in hits.values())

    context = {
        'results': results,
        'query': user_query,
        'entity_types': entity_types,
        'radius': radius,
        'osm': osm,
        'radius_choices': ['1','5','10','25','50','100'],
        'start_date': start_date,
        'end_date': end_date,
        'pages': pages,
        'q_filters': q_filters,
        'facets': facets,
        'selected_facets': selected_facets,
        'hits': hits
    }

    return render(request, 'search/search.html', context)

