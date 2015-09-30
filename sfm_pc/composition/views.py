import json

from django.views.generic.base import TemplateView
from django.http import HttpResponse
from django.db.models import Max

from organization.models import Classification
from composition.models import Composition


class CompositionCreate(TemplateView):
    template_name = 'composition/edit.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        data = json.loads(request.POST.dict()['composition'])
        composition = Composition.create(data)

        return HttpResponse(json.dumps({"success": True}), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super(CompositionCreate, self).get_context_data(**kwargs)
        context['composition'] = Composition()
        context['classification'] = Classification.objects.all()

        return context
