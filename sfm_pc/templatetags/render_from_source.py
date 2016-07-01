from django import template
from django.utils.translation import get_language

register = template.Library()

@register.filter
def render_from_source(source, attribute):
    html = ''
    if getattr(source, attribute).all():
        for prop in getattr(source, attribute).all():
            
            attributes = {
                'lang': get_language(),
                'object_ref_model_name': prop.object_ref._meta.model_name,
                'object_ref_object_name': prop.object_ref._meta.object_name,
                'object_ref_id': prop.object_ref_id,
                'property': prop._meta.verbose_name.title(),
                'value': prop.value,
            }
            
            html += ''' 
                <tr>
                    <td><a href="/{lang}/{object_ref_model_name}/edit/{object_ref_id}/">{object_ref_object_name}</a></td>
                    <td>{property}</td>
                    <td>{value}</td>
                </tr>
            '''.format(**attributes)
    return html
