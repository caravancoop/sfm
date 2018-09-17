import json
from uuid import uuid4
import itertools
import sys

import pysolr

from reversion.views import RevisionMixin
import reversion

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, TemplateView
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from complex_fields.models import ComplexFieldContainer

from countries_plus.models import Country

from api.base_views import JSONResponseMixin

from sfm_pc.base_views import NeverCacheMixin
from sfm_pc.utils import VersionsMixin
from sfm_pc.templatetags.citations import get_citation_string

from source.models import Source, AccessPoint
from source.forms import SourceForm


class SourceView(DetailView):
    model = Source
    context_object_name = 'source'
    template_name = 'source/view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        evidenced = context['source'].get_evidenced()

        evidenced_table = []

        for record in evidenced:
            name = str(record)
            record_type = record.object_ref._meta.object_name
            field_name = record._meta.model_name.replace(record_type.lower(), '').title()
            value = record.value

            link = None

            if record_type in ['Organization', 'Person']:
                link = reverse_lazy('view-{}'.format(record_type.lower()), kwargs={'slug': record.object_ref.uuid})

            evidenced_table.append([name, record_type, field_name, value, link])

        context['evidenced'] = evidenced_table
        context['versions'] = context['source'].getVersions()
        return context


class SourceEditView(NeverCacheMixin, RevisionMixin, LoginRequiredMixin):
    fields = [
        'title',
        'publication',
        'publication_country',
        'published_on',
        'source_url',
    ]
    model = Source
    template_name = 'source/edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['countries'] = Country.objects.all()
        context['versions'] = context['object'].getVersions()

        return context

    def get_success_url(self):
        return reverse_lazy('view-source', kwargs={'pk': self.object.uuid})

    def form_valid(self, form):
        self.form = form

        reversion.set_comment(self.request.POST['comment'])

        self.form.instance.user = self.request.user

        return super().form_valid(form)


class SourceUpdate(SourceEditView, UpdateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        source = context['object']
        context['versions'] = source.getVersions()

        for access_point in source.accesspoint_set.all():
            context['versions'].extend(access_point.getVersions())

        return context


class SourceCreate(SourceEditView, CreateView):
    fields = [
        'title',
        'publication',
        'publication_country',
        'published_on',
        'source_url',
        'uuid',
    ]
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['source_id'] = str(uuid4())

        return context

    def get_success_url(self):
        return reverse_lazy('update-source', kwargs={'pk': self.object.uuid})


class SourceRevertView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):

        version_id = request.POST['version_id']

        revision = Version.objects.get(id=version_id).revision

        reversion.set_comment(request.POST['comment'])
        reversion.set_user(request.user)

        revision.revert()

        return HttpResponseRedirect(reverse_lazy('update-source',
                                                 kwargs={'pk': kwargs['pk']}))


class AccessPointContextMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['source'] = Source.objects.get(uuid=self.kwargs['source_id'])
        context['versions'] = context['source'].getVersions()

        for access_point in context['source'].accesspoint_set.all():
            context['versions'].extend(access_point.getVersions())

        context['versions'] = sorted(context['versions'],
                                     key=lambda x: x['modification_date'],
                                     reverse=True)

        return context


class AccessPointEdit(AccessPointContextMixin,
                      NeverCacheMixin,
                      VersionsMixin,
                      LoginRequiredMixin,
                      RevisionMixin):
    fields = [
        'page_number',
        'accessed_on',
        'archive_url'
    ]
    model = AccessPoint
    template_name = 'source/access-points.html'

    def get_success_url(self):
        return reverse_lazy('add-access-point', kwargs={'source_id': self.object.source.uuid})

    def form_valid(self, form):
        self.form = form
        source = Source.objects.get(uuid=self.kwargs['source_id'])

        reversion.set_comment(self.request.POST['comment'])
        reversion.add_to_revision(source)

        self.form.instance.source = source
        self.form.instance.user = self.request.user

        return super().form_valid(form)


class AccessPointDetail(AccessPointContextMixin,
                        NeverCacheMixin,
                        VersionsMixin,
                        LoginRequiredMixin,
                        ListView):
    model = AccessPoint
    template_name = 'source/access-points.html'

    def get_queryset(self):
        return AccessPoint.objects.filter(source__uuid=self.kwargs['source_id'])


class AccessPointUpdate(AccessPointEdit, UpdateView):
    pass


class AccessPointCreate(AccessPointEdit, CreateView):
    pass


class StashSourceView(TemplateView, JSONResponseMixin, LoginRequiredMixin):

    http_method_names = ['get']

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):

        source_id = self.request.GET['source_id']

        source = Source.objects.get(uuid=source_id)

        context = {
            'title': source.title,
            'id': str(source.uuid),
            'publication': source.publication,
            'publication_country': source.publication_country,
            'source_url': source.source_url,
            'access_points': [],
            'uncommitted': True,
        }

        for access_point in source.accesspoint_set.all():
            ap_info = {
                'id': str(access_point.uuid),
                'page_number': access_point.page_number,
                'archive_url': access_point.archive_url,
            }

            context['access_points'].append(ap_info)

        return context


def source_autocomplete(request):
    term = request.GET.get('q')

    response = {
        'results': []
    }

    if term:
        sources = Source.objects.filter(title__icontains=term).order_by('-date_updated')

        for source in sources:

            publication_title = ''
            publication_country = ''

            text = '{0} ({1} - {2})'.format(source.title,
                                            source.publication,
                                            source.publication_country)
            response['results'].append({
                'text': text,
                'id': str(source.uuid),
            })

    return HttpResponse(json.dumps(response), content_type='application/json')


def extract_source(source, uncommitted=False):
    source_info = {
        'title': source.title,
        'id': str(source.uuid),
        'publication': source.publication,
        'publication_country': source.publication_country,
        'source_url': source.source_url,
        'access_points': [],
        'uncommitted': uncommitted,
    }

    for access_point in source.accesspoint_set.all():
        ap_info = {
            'id': str(access_point.uuid),
            'page_number': access_point.page_number,
            'archive_url': access_point.archive_url,
        }

        source_info['access_points'].append(ap_info)

    return source_info


def get_sources(request):
    object_type = request.GET['object_type']
    object_id = request.GET['object_id']
    field_name = request.GET['field_name']

    field = ComplexFieldContainer.field_from_str_and_id(
        object_type, object_id, field_name
    )

    sources = field.get_sources()
    sources_json = {
        "confidence": field.get_confidence(),
        "sources": []
    }

    for source in sources:
        sources_json['sources'].append(extract_source(source))

    return HttpResponse(json.dumps(sources_json), content_type='application/json')


def get_citation(request):
    object_info = request.GET['object_info']

    field_object_name, object_id = object_info.split('_')

    last_dot = field_object_name.rfind('.')
    classname = field_object_name[last_dot + 1:len(field_object_name)]
    module = __import__(field_object_name[0:last_dot],
                        globals(),
                        locals(),
                        [classname])
    field_object_class = getattr(module, classname)
    field_object = field_object_class.objects.get(id=object_id)

    source_html = get_citation_string(field_object)

    return HttpResponse(source_html)


def publication_autocomplete(request):
    term = request.GET.get('q')
    publications = Source.objects.filter(publication__icontains=term).distinct('publication')

    results = []
    for publication in publications:
        results.append({
            'id': publication.publication,
            'text': publication.publication,
            'country': publication.publication_country,
        })

    return HttpResponse(json.dumps(results), content_type='application/json')


def remove_source(request):

    field_name = request.GET['field_name']
    object_id = request.GET['object_id']
    object_type = request.GET['object_type']
    source_id = request.GET['id']

    field = ComplexFieldContainer.field_from_str_and_id(
        object_type, object_id, field_name
    )

    source = Source.objects.get(uuid=source_id)

    field.get_field().sources.remove(source)

    return HttpResponse(json.dumps({}), content_type='application/json')
