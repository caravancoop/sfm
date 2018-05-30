import json
from uuid import uuid4
import itertools

from reversion.views import RevisionMixin
from reversion.models import Version
import reversion

from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View

from complex_fields.models import ComplexFieldContainer

from countries_plus.models import Country

from source.models import Source
from source.forms import SourceForm
from source.utils import DictDiffer


class SourceView(DetailView):
    model = Source
    context_object_name = 'source'
    template_name = 'source/view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        versions = Version.objects.get_for_object(context['object'])

        differences = []

        for index, version in enumerate(versions):
            try:
                previous = versions[index - 1]
            except (IndexError, AssertionError):
                continue

            differ = DictDiffer(version.field_dict, previous.field_dict)

            diff = {
                'modification_date': version.revision.date_created,
                'comment': version.revision.comment,
                'user': version.revision.user,
                'id': '{0} => {1}'.format(version.id, previous.id),
                'field_diffs': []
            }

            # For the moment this will only ever return changes because all the
            # fields are required.
            if differ.changed():
                for field in differ.changed():
                    field_diff = {
                        'field_name': field,
                        'to': differ.past_dict[field],
                        'from': differ.current_dict[field],
                    }

                    diff['field_diffs'].append(field_diff)

                differences.append(diff)

        context['versions'] = differences

        return context


class SourceEditView(RevisionMixin, LoginRequiredMixin):
    fields = [
        'title',
        'publication',
        'publication_country',
        'published_on',
        'source_url',
        'page_number',
        'accessed_on'
    ]
    model = Source

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['countries'] = Country.objects.all()

        return context

    def get_success_url(self):
        return reverse_lazy('view-source', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        self.form = form

        self.addRevisionComment()

        self.form.instance.user = self.request.user
        return super().form_valid(form)


class SourceUpdate(SourceEditView, UpdateView):
    template_name = 'source/update.html'

    def addRevisionComment(self):
        reversion.set_comment('Updated by {}'.format(self.request.user.username))


class SourceCreate(SourceEditView, CreateView):
    template_name = 'source/create.html'

    def addRevisionComment(self):
        reversion.set_comment('Created by {}'.format(self.request.user.username))


class SourceRevertView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):

        print(request.POST)

        return super().post(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
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
            'id': str(source.id),
        })

    return HttpResponse(json.dumps(results), content_type='application/json')

def publication_autocomplete(request):
    term = request.GET.get('q')
    publications = Source.objects.filter(publication__icontains=term).all()

    results = []
    for publication in publications:
        results.append({
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
                "id": source.id
            }
            for source in sources
        ]
    }

    return HttpResponse(json.dumps(sources_json))
