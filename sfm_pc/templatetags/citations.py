from django import template
from django.conf import settings
from django.utils.translation import get_language
from django.utils.translation import ugettext as _

register = template.Library()

def get_citation_string(obj):

    source_citation = ''
    sources = obj.sources.select_related('user').all()
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
        info = tuple((attr_map[0], getattr(src, attr_map[1]))
                      for attr_map in source_info if getattr(src, attr_map[1], None))

        if any(info):

            # Border logic
            html = ''
            if idx != 0:
                html = '<hr/>'

            for i, attr in enumerate(info):
                key, val = attr[0], attr[1]

                # Wrap links in anchors
                if key == _('Source URL') or key == _('Archive URL'):
                    html_fmt = '<strong>{0}</strong>: <a href="{1}">{1}</a>'
                else:
                    html_fmt = '<strong>{0}</strong>: {1}'

                html_str = ''
                if i != 0:
                    html_str = '<br/>'

                html_str += html_fmt.format(key, val)
                html += html_str

            source_citation += html

    return source_citation


@register.inclusion_tag('partials/source_input.html')
def source_input(field_name, source):

    context = {
        'field_name': field_name,
        'uncommitted': False,
        'id': source.uuid,
        'publication': source.publication,
        'title': source.title,
        'access_points': []
    }

    for access_point in source.accesspoint_set.all():
        access_point_info = {
            'archive_url': access_point.archive_url,
            'id': access_point.uuid,
            'page_number': access_point.page_number,
            'accessed_on': access_point.accessed_on,
        }
        context['access_points'].append(access_point_info)

    return context


@register.inclusion_tag('partials/source_and_confidence.html')
def cite(obj):

    context = {}

    if obj:
        context['object_value'] = obj

        if isinstance(obj, str):
            # Pass over the source/confidence logic if this is just a string
            return context

        field_name = '{0}.{1}'.format(obj._meta.model.__module__,
                                      obj._meta.object_name)

        context['object_info'] = '{0}_{1}'.format(field_name,
                                                  obj.id)

        src_string = _('Sources for this datapoint')

        confidence = obj.confidence

        # Default to low confidence
        if not confidence:
            confidence = '1'

        if confidence == '1':
            context['confidence_class'] = 'low-confidence'
            confidence_string = _('Confidence: LOW')

        elif confidence == '2':
            context['confidence_class'] = 'medium-confidence'
            confidence_string = _('Confidence: MEDIUM')

        elif confidence == '3':
            context['confidence_class'] = 'high-confidence'
            confidence_string = _('Confidence: HIGH')

        context['confidence_string'] = confidence_string

    return context


@register.inclusion_tag('partials/datetype.html')
def datetype(citation_date, position):

    if not citation_date:
        context = {'citation_date': ''}
        return context

    context = {'citation_date': citation_date}

    object_ref = getattr(citation_date, 'object_ref', None)

    if object_ref:

        html = None
        src = ''

        if position == 'start':

            realstart = getattr(object_ref, 'realstart', None)
            if realstart:
                if realstart.get_value():
                    src = get_citation_string(realstart.get_value())
                    realstart = realstart.get_value().value

                    if realstart is True:

                        context['real_date'] = True
                        context['title'] = _('Real start date')
                        html = _('We believe that this date represents a real start date, as well as being the first recorded citation date.')

        elif position == 'end':

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
                html = _('We believe that this date represents a real end date, as well as being the last recorded citation date.')

        if html:
            html = '<div class="tooltip-content"><p class="text-left">{0}</p>{1}</div>'.format(html, src)

            context['content'] = html

    return context
