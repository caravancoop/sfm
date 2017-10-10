from django import template
from django.conf import settings
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _

register = template.Library()

@register.inclusion_tag('partials/help_widget.html')
def help(text):
    context = {}

    context['help_text'] = text

    return context
