import urllib

from django.shortcuts import render
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.decorators.cache import never_cache
import pysolr

from source.models import Source, Publication
from organization.models import Organization
from person.models import Person
from violation.models import Violation
from sfm_pc.utils import get_osm_by_id, format_facets

import pprint

SEARCH_ENTITY_TYPES = {
#    'Source': Source,
#    'Publication': Publication,
    'Organization': {
        'model': Organization,
        'facet_fields': ['organization_classification_ss_fct',
                         'country_ss_fct'],
        'facet_ranges': ['organization_start_date_dt',
                         'organization_end_date_dt'],
    },
    'Person': {
        'model': Person,
        'facet_fields': ['person_current_role_s_fct',
                         'person_current_rank_s_fct',
                         'country_ss_fct'],
        'facet_ranges': ['person_first_cited_dt',
                         'person_last_cited_dt'],
    },
    'Violation': {
        'model': Violation,
        'facet_fields': ['violation_type_ss_fct',
                         'perpetrator_classification_ss_fct',
                         'violation_location_description_ss_fct',
                         'country_ss_fct'],
        'facet_ranges': ['violation_start_date_dt',
                         'violation_end_date_dt'],
    }
}

# Search engine
solr = pysolr.Solr(settings.SOLR_URL)

# Suggester engine
suggester = pysolr.Solr(settings.SOLR_URL, search_handler='suggest')

def get_search_context(request, all_results=False):

    # Parse standard request params
    user_query = request.GET.get('q')
    entity_types = request.GET.getlist('entity_type')
    location = request.GET.get('osm_id')
    radius = request.GET.get('radius')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # Use params to generate the link for downloading CSV
    params = request.GET.urlencode()

    download_url = reverse('download')

    if params:
        download_url += '?' + params + '&'
    else:
        download_url += '/?'

    download_urls = {}
    for etype in ('Person', 'Organization', 'Violation'):
        download_urls[etype] = download_url + 'download_etype={0}'.format(etype)

    # Parse selected facets (since URLs format lists of params in multiples, like
    # `type=foo&type=bar` for `type = [foo, bar]`, we have to unpack the lists)
    selected_facet_vals = request.GET.getlist('selected_facets')
    selected_facets = {}
    for val in selected_facet_vals:
        if val:
            [k, v] = val.split('_exact:', 1)
            # Convert facets on null values to a more pythonic format
            if v == 'None':
                v = None
            if selected_facets.get(k):
                selected_facets[k].append(v)
            else:
                selected_facets[k] = [v]

    # Only show the "clear" button if the user has selected facets
    show_clear = any((selected_facets, start_date, end_date))

    # Make sure to handle empty entity types
    if entity_types in (None, '', [], ['']):
        entity_types = [etype for etype in SEARCH_ENTITY_TYPES.keys()]

    # Re-format the query string for use in templating
    q_filters, filters_no_query = '', ''
    url_params = [(p, val) for (p, val) in request.GET.items()
                  if '_page' not in p and p != 'selected_facets'
                  and p != 'entity_type' and p != 'amp' and p != '_']

    for facet_val in selected_facet_vals:
        url_params.append(('selected_facets', facet_val))

    for etype in entity_types:
        url_params.append(('entity_type', etype))

    if url_params:
        q_filters = urllib.parse.urlencode(url_params)
        # Strip the query for use in "Did you mean?" links
        params_no_query = [(param[0], param[1]) for param in url_params
                           if param[0] != 'q']
        filters_no_query = urllib.parse.urlencode(params_no_query)

    # Define query string
    if user_query is None or user_query == '':
        full_query = '*'
    else:
        full_query = ' '.join(term + '~' for term in user_query.strip().split(' '))

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
    if not all_results:
        if len(entity_types) < 2:
            result_count = 10
        else:
            result_count = 5
    else:
        # The `all_results` parameter indicates to skip pagination entirely
        result_count = 10000

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

        # Add facets to the query
        search_context['facet.field'] = SEARCH_ENTITY_TYPES[etype]['facet_fields']
        search_context['facet.range'] = SEARCH_ENTITY_TYPES[etype]['facet_ranges']
        search_context['facet.range.start'] = '2000-01-01T00:00:00Z/YEAR'
        search_context['facet.range.end'] = 'NOW/YEAR'
        search_context['facet.range.gap'] = '+1YEAR'
        # Show facets for fields that are missing (have nulls)
        search_context['facet.missing'] = 'true'

        # Handle pagination
        pages[etype] = {}
        pagination = request.GET.get(etype + '_page')

        if all_results:
            search_context['start'] = 0
        else:
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
                    if val:
                        etype_query += ' AND {field}:"{val}"'.format(field=field,
                                                                    val=val)
                    else:
                        # In this case, the user is faceting on null values,
                        # so use the appropriate syntax
                        etype_query += 'AND -{field}:[* TO *]'.format(field=field)

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

    # If we didn't get many hits, look for search term suggestions
    suggested_terms = None
    if hits['global'] < 10 and user_query:
        lookup = suggester.search(user_query)
        suggestions = lookup.raw_response['suggest']['Suggester'][user_query]['suggestions']
        # Filter out suggestions that exactly match the user's query
        suggested_terms = list(sugg['term'] for sugg in suggestions
                               if sugg['term'].lower() != user_query.lower())

    # Count universal facets
    country_counts = {}
    for etype, found_facets in facets.items():
        # This retrieves tuples of facet counts, like `('mexico', 10)`
        facet_counts = found_facets['facet_fields']['country_ss_fct']['counts']
        for fac in facet_counts:
            cname, ccount = fac[0], fac[1]
            if not country_counts.get(cname):
                country_counts[cname] = ccount
            else:
                country_counts[cname] += ccount

    facets['All'] = {'facet_fields': {'country_ss_fct': {'any': False,
                                                     'counts': []}}}

    for country, count in country_counts.items():
        if count > 0:
            facets['All']['facet_fields']['country_ss_fct']['any'] = True
            facets['All']['facet_fields']['country_ss_fct']['counts'].append((country, count))

    context = {
        'results': results,
        'suggested_terms': suggested_terms,
        'query': user_query,
        'entity_types': entity_types,
        'radius': radius,
        'osm': osm,
        'radius_choices': ['1','5','10','25','50','100'],
        'start_date': start_date,
        'end_date': end_date,
        'show_clear': show_clear,
        'pages': pages,
        'q_filters': q_filters,
        'filters_no_query': filters_no_query,
        'facets': facets,
        'selected_facets': selected_facets,
        'hits': hits,
        'download_urls': download_urls
    }

    return context

@never_cache
def search(request):

    context = get_search_context(request)

    return render(request, 'search/search.html', context)
