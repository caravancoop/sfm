from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def country_name(division_id):
    '''
    Map an OCD division ID to a country name, e.g.:

    "ocd-division/country:ng" -> "Nigeria"
    '''
    if division_id and division_id != '':
        country_code = division_id.split('country:')[1]

        for country in settings.OSM_DATA:

            if country['country_code'] == country_code:

                return country['country']

    # If for some reason we can't find this country, return None
    # so that we don't mess with the template
    return '' 

@register.inclusion_tag('partials/location_string.html')
def render_location_string(obj, countries=True):

    context = {'locations': []}

    locations = [obj.locationdescription.get_value(),
                 obj.adminlevel1.get_value(),
                 obj.adminlevel2.get_value()]

    remove_nulls = [loc for loc in locations if loc is not None]
    context['locations'] = [loc.value for loc in remove_nulls
                            if loc.value is not None]

    if countries and country_name(obj.division_id.get_value()) is not None:
        context['locations'].append(country_name(obj.division_id.get_value()))

    return context
