from django import template
from django.conf import settings
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _

register = template.Library()

@register.inclusion_tag('partials/source_and_confidence.html')
def cite(obj):

    context = {}

    if not obj:
        # Set the empty string as the default for cases where we don't have any
        # information
        context['object_value'] = ''
    else:
        context['object_value'] = obj

        source_info = (
            (_('Title'), 'title'),
            (_('Publication'), 'publication'),
            (_('Published on'), 'published_on'),
            (_('Source URL'), 'source_url'),
            (_('Archive URL'), 'archive_url'),
            (_('Date added'), 'date_added'),
            (_('Date updated'), 'date_updated'),
            (_('Added by'), 'user'),
            (_('Page number'), 'page_number'),
            (_('Accessed'), 'accessed_on'),
        )

        source_citation = ''
        sources = obj.sources.all()
        for idx, src in enumerate(sources):
            info = ((attr_map[0], getattr(src, attr_map[1]))
                     for attr_map in source_info if getattr(src, attr_map[1], None))
            if any(info):
                if idx != 0:
                    html = '<hr/>'
                else:
                    html = ''
                html += '<br/>'.join('<strong>{0}</strong>: {1}'.format(attr[0], attr[1]) for attr in info)
                source_citation += html

        context['source_citation'] = source_citation

        confidence = obj.confidence
        if confidence == '3':
            context['confidence_citation'] = _('We are very confident in the ' +
                                               'integrity of this information.')

    return context


