from datetime import date

import json

from django.views.generic.base import TemplateView
from django.http import HttpResponse

from .models import Emplacement


class EmplacementView(TemplateView):
    template_name = 'emplacement/search.html'

    def get_context_data(self, **kwargs):
        context = super(EmplacementView, self).get_context_data(**kwargs)

        context['year_range'] = range(1955, date.today().year + 1)
        context['day_range'] = range(1, 31)

        return context

class EmplacementUpdate(TemplateView):
    template_name = 'emplacement/edit.html'

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.dict()['object'])
        try:
            emplacement = Emplacement.objects.get(pk=kwargs.get('pk'))
        except Emplacement.DoesNotExist:
            msg = "This emplacement does not exist, it should be created " \
                  "before updating it."
            return HttpResponse(msg, status=400)

        (errors, data) = emplacement.validate(data)
        if errors is None:
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )

        emplacement.update(data)
        return HttpResponse(
            json.dumps({"success": True}),
            content_type="application/json"
        )

    def get_context_data(self, **kwargs):
        context = super(EmplacementUpdate, self).get_context_data(**kwargs)
        emplacement = Emplacement.objects.get(pk=context.get('pk'))
        context['emplacement'] = emplacement

        return context

class EmplacementCreate(TemplateView):
    template_name = 'emplacement/edit.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        data = json.loads(request.POST.dict()['object'])
        (errors, data) = Emplacement().validate(data)

        if len(errors):
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )

        emplacement = Emplacement.create(data)

        return HttpResponse(json.dumps({"success": True, "id": emplacement.id}),
                            content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super(EmplacementCreate, self).get_context_data(**kwargs)
        context['emplacement'] = Emplacement()

        return context

