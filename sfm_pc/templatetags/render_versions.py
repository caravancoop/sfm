from django import template
from reversion.models import Version
import itertools

register = template.Library()

def get_versions(object_ref):

    complex_fields = [f for f in dir(object_ref) if f.endswith('_set')]

    versioned_types = []

    for field in complex_fields:
        for related in getattr(object_ref, field).all():
            if related.versioned:
                versions = Version.objects.get_for_object(related)

                versioned_types.append((related.field_name, versions,))

    versioned_types = sorted(versioned_types, key=lambda x: x[0])

    return versioned_types

@register.inclusion_tag('partials/version_list.html')
def render_versions(object_ref):

    context = {'versions': []}

    versioned_types = get_versions(object_ref)

    for object_type, grouping in itertools.groupby(versioned_types, key=lambda x: x[0]):
        context['versions'].append({object_type: list(grouping)})

    return context


@register.simple_tag
def has_versions(object_ref):

    versioned_types = get_versions(object_ref)

    # versioned_types is a list of tuples, so we want to sum over the second
    # element of each tuple to get the count of versioned elements
    count = sum(len(x[1]) for x in versioned_types if len(x[1]))

    return count

