from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
from countries_plus.models import Country

register = template.Library()

@register.filter
@stringfilter
def country_name(division_id):
    '''
    Map an OCD division ID to a country name, e.g.:

    "ocd-division/country:ng" -> "Nigeria"
    '''

    if division_id and division_id != '':

        split_id = division_id.split('country:')

        if len(split_id) > 1:

            iso = split_id[1].upper()
            country = Country.objects.get(iso=iso)

            return country.name

        else:

            return division_id

    # If for some reason we can't find this country, return None
    # so that we don't mess with the template
    return ''

@register.inclusion_tag('partials/location_string.html')
def render_location_string(obj, countries=True):

    context = {}

    locations = [obj.locationdescription.get_value(),
                 obj.location_name.get_value(),
                 obj.osmname.get_value(),
                 obj.adminlevel1.get_value(),
                 obj.adminlevel2.get_value()]

    context['locations'] = [loc for loc in locations if loc is not None]

    if countries and country_name(obj.division_id.get_value()) is not None:
        context['locations'].append(country_name(obj.division_id.get_value()))

    return context
