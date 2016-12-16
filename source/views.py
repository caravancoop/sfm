import json
from uuid import uuid4

from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy

from complex_fields.models import ComplexFieldContainer

from countries_plus.models import Country

from source.models import Source, Publication
from source.forms import SourceForm


class SourceCreate(FormView):
    template_name = 'source/create.html'
    form_class = SourceForm
    success_url = reverse_lazy('create-organization')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['publication_uuid'] = str(uuid4())

        pub_title = self.request.POST.get('publication_title')
        if pub_title:
            context['publication_title'] = pub_title

        pub_country = self.request.POST.get('publication_country')
        if pub_country:
            context['publication_country'] = pub_country

        context['countries'] = Country.objects.all()

        if self.request.session.get('source_id'):
            del self.request.session['source_id']

        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        response = super().form_valid(form)
        # Try to find the publication

        publication_uuid = form.data.get('publication')

        if publication_uuid == 'None':
            return self.form_invalid(form)

        publication, created = Publication.objects.get_or_create(id=publication_uuid)

        if created:
            publication.title = form.data.get('publication_title')
            publication.country = form.data.get('publication_country')
            publication.save()

        self.publication = publication

        source, created = Source.objects.get_or_create(title=form.cleaned_data['title'],
                                                       source_url=form.cleaned_data['source_url'],
                                                       publication=self.publication,
                                                       published_on=form.cleaned_data['published_on'],
                                                       page_number=form.cleaned_data['page_number'],
                                                       accessed_on=form.cleaned_data['accessed_on'],
                                                       user=self.request.user)

        self.request.session['source_id'] = source.id
        return response

def source_autocomplete(request):
    term = request.GET.get('q')
    sources = Source.objects.filter(title__icontains=term).all()

    results = []
    for source in sources:

        publication_title = ''
        publication_country = ''

        if source.publication:
            publication_title = source.publication.title
            publication_country = source.publication.country

        text = '{0} ({1} - {2})'.format(source.title,
                                        publication_title,
                                        publication_country)
        results.append({
            'text': text,
            'id': str(source.id),
        })

    return HttpResponse(json.dumps(results), content_type='application/json')

def publication_autocomplete(request):
    term = request.GET.get('q')
    publications = Publication.objects.filter(title__icontains=term).all()

    results = []
    for publication in publications:
        results.append({
            'text': publication.title,
            'country': publication.country,
            'id': str(publication.id),
        })

    return HttpResponse(json.dumps(results), content_type='application/json')

def view_source(request, source_id):
    try:
        source = Source.objects.get(id=source_id)

    except Source.DoesNotExist:
        return HttpResponseNotFound()

    return render(request,
                  'source/view.html',
                  context={'source': source})

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
