from django import template

register = template.Library()


@register.filter
def verbose_field_name(Model, field):
    """
    Return the verbose fieldname for a given 'field' on a Model.
    """
    if hasattr(Model, 'get_verbose_field_name'):
        return Model.get_verbose_field_name(field)
    else:
        return Model._meta.get_field(field).verbose_name
