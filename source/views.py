import json
from uuid import uuid4

from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from complex_fields.models import ComplexFieldContainer

from countries_plus.models import Country

from source.models import Source
from source.forms import SourceForm


class SourceView(DetailView):
    model = Source
    context_object_name = 'source'
    template_name = 'source/view.html'


class SourceUpdate(LoginRequiredMixin, UpdateView):
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
    template_name = 'source/update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['countries'] = Country.objects.all()

        return context

    def get_success_url(self):
        return reverse_lazy('view-source', kwargs={'pk': self.object.id})

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class SourceCreate(LoginRequiredMixin, CreateView):
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
    template_name = 'source/create.html'

    def get_success_url(self):
        return reverse_lazy('view-source', kwargs={'source_id': self.source_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['countries'] = Country.objects.all()

        return context


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
