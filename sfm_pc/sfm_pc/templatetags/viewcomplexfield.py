from django.template import Library

register = Library()

@register.inclusion_tag('complexfield/view.html')
def view_complex_field(field, object_id, path):
    field_id = field.get_field_str_id()

    return {
        'value' : field,
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
    }
