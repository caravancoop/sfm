from datetime import date

import json

from django.views.generic.base import TemplateView
from django.http import HttpResponse

from .models import Association


class AssociationView(TemplateView):
    template_name = 'association/search.html'

    def get_context_data(self, **kwargs):
        context = super(AssociationView, self).get_context_data(**kwargs)

        context['year_range'] = range(1955, date.today().year + 1)
        context['day_range'] = range(1, 31)

        return context

class AssociationUpdate(TemplateView):
    template_name = 'association/edit.html'

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.dict()['object'])
        try:
            association = Association.objects.get(pk=kwargs.get('pk'))
        except Association.DoesNotExist:
            msg = "This association does not exist, it should be created " \
                  "before updating it."
            return HttpResponse(msg, status=400)

        errors = association.update(data)
        if errors is None:
            return HttpResponse(
                json.dumps({"success": True}),
                content_type="application/json"
            )
        else:
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )

    def get_context_data(self, **kwargs):
        context = super(AssociationUpdate, self).get_context_data(**kwargs)
        association = Association.objects.get(pk=context.get('pk'))
        context['association'] = association

        return context

class AssociationCreate(TemplateView):
    template_name = 'association/edit.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        data = json.loads(request.POST.dict()['object'])
        association = Association.create(data)

        return HttpResponse(json.dumps({"success": True}), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super(AssociationCreate, self).get_context_data(**kwargs)
        context['association'] = Association()

        return context

