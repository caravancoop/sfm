from django.template import Library

register = Library()

@register.inclusion_tag('complexfield/view_geo.html')
def view_complex_field_geo(field, object_id, geo_form, path):
    field_id = field.get_field_str_id()
    if object_id is None:
        object_id = 0
    value = field.get_value()
    if value is not None:
        value = value.geojson
    return {
        'value' : value,
        'object_id': object_id,
        'object_name': field.get_object_name(),
        'field_str_id': field.get_field_str_id(),
        'attr_name': field.get_attr_name(),
        'field_id': field_id,
        'field_name': field.field_name,
        'sourced': field.sourced,
        'translated': field.translated,
        'versioned': field.versioned,
        'path': path,
        'geo_form': geo_form,
    }
