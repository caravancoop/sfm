import re

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def short_title(text_blob):
    if len(text_blob) > 28:
        blurb = text_blob[:24]
        blurb = blurb[:blurb.rfind(' ')] + ' ...'
        return blurb
    else:
        return text_blob
