from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, CreateView
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy

from source.forms import SourceForm
from source.models import Source

class Dashboard(TemplateView):
    template_name = 'sfm/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(Dashboard, self).get_context_data(**kwargs)
        return context

class CreateSource(CreateView):
    template_name = 'sfm/create-source.html'
    form_class = SourceForm
    model = Source
    success_url = '/'

    def form_valid(self, form):
        response = super(CreateSource, self).form_valid(form)

        # Save the ID of the source object just created to the session data
        # so that we can link things up in the coming steps.
        self.request.session['source_id'] = self.object.id
        return response
