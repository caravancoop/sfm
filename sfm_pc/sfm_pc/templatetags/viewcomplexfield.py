from django.template import Library

register = Library()

@register.inclusion_tag('complexfield/view.html')
def view_complex_field(field):
    field_id = field.table_object.__class__.__name__ + "_" + field.field_model.__name__

    return {
        'value' : field,
        'field_id': field_id,
        'field_name': field.field_name,
        'sourced': field.sourced,
        'translated': field.translated,
        'versioned': field.versioned,
    }

