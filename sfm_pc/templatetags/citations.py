from django import template
from django.conf import settings
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _


register = template.Library()

def get_citation_string(obj):

    source_citation = ''
    sources = obj.sources.all()
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

    return source_citation


@register.inclusion_tag('partials/source_and_confidence.html')
def cite(obj, date=False, position=None):

    context = {}

    if not obj:
        # Set the empty string as the default for cases where we don't have any
        # information
        context['object_value'] = ''
    else:
        context['object_value'] = obj
        context['date'] = date
        context['position'] = position

        if isinstance(obj, str):
            # Pass over the source/confidence logic if this is just a string
            return context

        source_citation = get_citation_string(obj)
        context['source_citation'] = source_citation

        confidence = obj.confidence
        if confidence == '3':
            context['confidence_citation'] = _('We are very confident in the ' +
                                               'integrity of this information.')

    return context


@register.inclusion_tag('partials/help-widget.html')
def help(text):
    pass


@register.inclusion_tag('partials/datetype.html')
def datetype(citation_date, position):

    if not citation_date:
        context = {'citation_date': ''}
        return context

    context = {'citation_date': citation_date}

    object_ref = getattr(citation_date, 'object_ref', None)

    if object_ref:

        html = None

        if position == 'start':

            realstart = getattr(object_ref, 'realstart', None)
            if realstart:
                if realstart.get_value():
                    realstart_src = get_citation_string(realstart.get_value())
                    realstart = realstart.get_value().value

                    if realstart is True:

                        context['real_date'] = True
                        context['title'] = _('Real start date')
                        html = _('We believe that this date represents the real start date of the organization, as well as being the first recorded citation date.')
                        html += '<br/>'
                        html += realstart_src

                        context['content'] = html

        elif position == 'end':

            src = None
            open_ended =  getattr(object_ref, 'open_ended', None)
            if open_ended:
                if open_ended.get_value():
                    src = get_citation_string(open_ended.get_value())
                    open_ended = open_ended.get_value().value

            realend =  getattr(object_ref, 'realend', None)
            if realend:
                if realend.get_value():
                    src = get_citation_string(realend.get_value())
                    realend = realend.get_value().value

            if open_ended == 'E' or realend is True:

                context['real_date'] = True
                context['title'] = _('Real end date')
                html = _('We believe that this date represents the real start date of the organization, as well as being the first recorded citation date.')
                html += '<br/>'
                html += src

                context['content'] = html

    return context
