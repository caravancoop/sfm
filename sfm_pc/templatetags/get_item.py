import re

from django import template

register = template.Library()


@register.filter
def from_index(value, i):
    return value[i]
