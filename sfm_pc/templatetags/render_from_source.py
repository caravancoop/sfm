import re

from django import template

register = template.Library()

@register.filter
def render_from_source(source, attribute):
    html = ''
    if getattr(source, attribute).all():
        for prop in getattr(source, attribute).all():
            html += ''' 
                <tr>
                    <td>{0}</td>
                    <td>{1}</td>
                    <td>{2}</td>
                </tr>
            '''.format(attribute.split('_')[0].title(),
                       prop._meta.verbose_name.title(),
                       prop.value)
    return html
