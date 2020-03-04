from django import template
from django.conf import settings
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _

register = template.Library()

@register.inclusion_tag('partials/help_widget.html')
def help(href=''):
    '''
    Link a button out to the appropriate section in the SFM Research Handbook.

    To make linking easier, we pull in the base URL from the settings file, so
    all you have to do to make a link is add an inclusion tag like so:

    `{% help 'personsrec.html' %}`

    Which will link out to:

    `https://help.securityforcemonitor.org/{lang}/latest/personsrec.html`
    '''
    context = {}

    context['base_url'] = settings.RESEARCH_HANDBOOK_URL
    context['href'] = href

    return context
