from django.template import Library
from django_date_extensions.fields import ApproximateDate

from complex_fields.models import ComplexFieldListContainer

register = Library()

@register.inclusion_tag('complexfield/view.html')
def view_complex_field(field, object_id, path):
    if isinstance(field, str):
        raise Exception("Can't render field: field is str")
    if object_id is None:
        object_id = 0

    value = field.get_value()
    if (not isinstance(value, str) and value is not None and
        not isinstance(value, ApproximateDate)):
        if hasattr(value, "get_value"):
            value = value.get_value()
        else:
            value = value.value

    return {
        'value' : value,
        'object_id': object_id,
        'object_name': field.get_object_name(),
        'field_str_id': field.get_field_str_id(),
        'attr_name': field.get_attr_name(),
        'field_name': field.field_name,
        'sourced': field.sourced,
        'translated': field.translated,
        'versioned': field.versioned,
        'is_list': isinstance(field, ComplexFieldListContainer),
        'field_id': field.id_,
        'path': path,
    }
