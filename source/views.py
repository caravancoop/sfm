import json

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

    def form_valid(self, form):
        response = super(CreateSource, self).form_valid(form)

        # Save the ID of the source object just created to the session data
        # so that we can link things up in the coming steps.
        self.request.session['source_id'] = self.object.id
        return response
    
def publications_autocomplete(request):
    term = request.GET.get('term')
    publications = Publication.objects.filter(title__icontains=term).all()
    
    results = []
    for publication in publications:
        results.append({
            'title': publication.title,
            'country': publication.country,
            'id': publication.id,
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
