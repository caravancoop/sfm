from django import template
from django.utils.translation import get_language

register = template.Library()

def get_relations(source):
    return [p for p in dir(source) if p.endswith('_related')]

def get_relation_attributes(relation):

    return  {
        'lang': get_language(),
        'object_ref_model_name': relation.object_ref._meta.model_name,
        'object_ref_object_name': relation.object_ref._meta.object_name,
        'relation_object_name': relation._meta.object_name,
        'relation_label': relation._meta.label,
        'object_ref_id': relation.object_ref_id,
        'property': relation._meta.verbose_name.title(),
        'value': relation.value,
        'confidence': relation.confidence,
        'sources': relation.sources.all(),
    }


@register.filter
def render_from_source(source, attribute):
    html = ''
    
    props = getattr(source, attribute).all()

    if props:
        for prop in props:
            
            attributes = get_relation_attributes(prop)
            
            html += ''' 
                <tr>
                    <td><a href="/{lang}/{object_ref_model_name}/edit/{object_ref_id}/">{object_ref_object_name}</a></td>
                    <td>{property}</td>
                    <td>{value}</td>
                </tr>
            '''.format(**attributes)

    return html
