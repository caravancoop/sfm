import json
from uuid import uuid4

from django.http import HttpResponse
from django.views.generic.edit import FormView, CreateView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render

from complex_fields.models import ComplexFieldContainer

from .forms import SourceForm
from .models import Source, Publication

class CreateSource(FormView):
    template_name = 'sfm/create-source.html'
    form_class = SourceForm
    success_url = '/'
    
    def get_context_data(self, **kwargs):
        context = super(CreateSource, self).get_context_data(**kwargs)
        context['publication_uuid'] = str(uuid4())
        
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        
        # Try to find the publication

        publication_uuid = form.data.get('publication')
        publication, created = Publication.objects.get_or_create(uuid=publication_uuid)
        
        if created:
            publication.title = form.data.get('publication_title')
            publication.country_iso = form.data.get('publication_country_iso')
            publication.country_name = form.data.get('publication_country_name')
            publication.save()
        
        self.publication = publication

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        response = super(CreateSource, self).form_valid(form)
        
        source = Source.objects.create(title=form.cleaned_data['title'],
                                       source_url=form.cleaned_data['source_url'],
                                       archive_url=form.cleaned_data['archive_url'],
                                       publication=self.publication,
                                       published_on=form.cleaned_data['published_on'])

        self.request.session['source_id'] = source.id
        return response
    
def publications_autocomplete(request):
    term = request.GET.get('q')
    publications = Publication.objects.filter(title__icontains=term).all()
    
    results = []
    for publication in publications:
        results.append({
            'text': publication.title,
            'country_iso': publication.country_iso,
            'id': str(publication.uuid),
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
