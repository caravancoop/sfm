import json

from django.views.generic.base import TemplateView
from django.http import HttpResponse

from .models import Violation, Type
from source.models import Source
from .forms import ZoneForm


class ViolationView(TemplateView):
    template_name = 'violation/search.html'

    def get_context_data(self, **kwargs):
        context = super(ViolationView, self).get_context_data(**kwargs)


class ViolationUpdate(TemplateView):
    template_name = 'violation/edit.html'

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.dict()['object'])
        try:
            violation = Violation.objects.get(pk=kwargs.get('pk'))
        except Violation.DoesNotExist:
            msg = "This violation does not exist, it should be created " \
                  "before updating it."
            return HttpResponse(msg, status=400)

        errors = violation.update(data)
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
        context = super(ViolationUpdate, self).get_context_data(**kwargs)
        violation = Violation.objects.get(pk=context.get('pk'))
        context['violation'] = violation

        return context

class ViolationCreate(TemplateView):
    template_name = 'violation/edit.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        data = json.loads(request.POST.dict()['object'])
        violation = Violation.create(data)

        return HttpResponse(json.dumps({"success": True}), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super(ViolationCreate, self).get_context_data(**kwargs)
        context['violation'] = Violation()
        context['violationtypes'] = Type.objects.all()
        context['sources'] = Source.objects.all()
        context['point'] = ZoneForm()

        return context
