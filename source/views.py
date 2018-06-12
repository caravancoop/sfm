import json
from uuid import uuid4
import itertools

from reversion.views import RevisionMixin
from reversion.models import Version
import reversion

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.views.generic import ListView

from complex_fields.models import ComplexFieldContainer

from countries_plus.models import Country

from sfm_pc.base_views import NeverCacheMixin

from source.models import Source, AccessPoint
from source.forms import SourceForm
from source.utils import DictDiffer


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

            if record_type in ['Organization', 'Person', 'Violation']:
                link = reverse_lazy('view-{}'.format(record_type.lower()), kwargs={'pk': record.object_ref.id})

            evidenced_table.append([name, record_type, field_name, value, link])

        context['evidenced'] = evidenced_table

        return context


class VersionsMixin(object):
    def getVersions(self, obj):
        versions = Version.objects.get_for_object(obj)

        differences = []

        for index, version in enumerate(versions):
            try:
                previous = versions[index - 1]
            except (IndexError, AssertionError):
                continue

            differ = DictDiffer(version.field_dict, previous.field_dict)

            diff = {
                'modification_date': previous.revision.date_created,
                'comment': previous.revision.comment,
                'user': previous.revision.user,
                'from_id': version.id,
                'to_id': previous.id,
                'field_diffs': [],
                'model': obj._meta.object_name,
            }

            skip_fields = ['date_updated']

            # For the moment this will only ever return changes because all the
            # fields are required.
            if differ.changed():

                for field in differ.changed():

                    if field not in skip_fields:
                        field_diff = {
                            'field_name': field,
                            'to': differ.past_dict[field],
                            'from': differ.current_dict[field],
                        }

                        diff['field_diffs'].append(field_diff)

                differences.append(diff)

        return differences

class SourceEditView(NeverCacheMixin, RevisionMixin, VersionsMixin, LoginRequiredMixin):
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
        context['versions'] = self.getVersions(source)

        for access_point in source.accesspoint_set.all():
            context['versions'].extend(self.getVersions(access_point))

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

        context['source'] = Source.objects.get(uuid=self.kwargs['pk'])
        context['versions'] = self.getVersions(context['source'])

        for access_point in context['source'].accesspoint_set.all():
            context['versions'].extend(self.getVersions(access_point))

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
                        DetailView):
    model = Source
    template_name = 'source/access-points.html'


class AccessPointUpdate(AccessPointEdit, UpdateView):
    pass


class AccessPointCreate(AccessPointEdit, CreateView):
    pass


def source_autocomplete(request):
    term = request.GET.get('q')
    sources = Source.objects.filter(title__icontains=term).all()

    results = []
    for source in sources:

        publication_title = ''
        publication_country = ''

        text = '{0} ({1} - {2})'.format(source.title,
                                        source.publication,
                                        source.publication_country)
        results.append({
            'text': text,
            'id': str(source.uuid),
        })

    return HttpResponse(json.dumps(results), content_type='application/json')

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


def get_sources(request, object_type, object_id, field_name):
    field = ComplexFieldContainer.field_from_str_and_id(
        object_type, object_id, field_name
    )
    sources = field.get_sources()
    sources_json = {
        "confidence": field.get_confidence(),
        "sources": [
            {
                "source": source.source,
                "id": str(source.id)
            }
            for source in sources
        ]
    }

    return HttpResponse(json.dumps(sources_json))
