import json

from django.views.generic.base import TemplateView
from django.http import HttpResponse

from .models import Area
from .forms import ZoneForm


class AreaView(TemplateView):
    template_name = 'area/search.html'

    def get_context_data(self, **kwargs):
        context = super(AreaView, self).get_context_data(**kwargs)


class AreaUpdate(TemplateView):
    template_name = 'area/edit.html'

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.dict()['object'])
        try:
            area = Area.objects.get(pk=kwargs.get('pk'))
        except Area.DoesNotExist:
            msg = "This area does not exist, it should be created " \
                  "before updating it."
            return HttpResponse(msg, status=400)

        (errors, data) = area.validate(data)
        if len(errors):
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )

        area.update(data)

        return HttpResponse(
            json.dumps({"success": True}),
            content_type="application/json"
        )

    def get_context_data(self, **kwargs):
        context = super(AreaUpdate, self).get_context_data(**kwargs)
        area = Area.objects.get(pk=context.get('pk'))
        context['area'] = area
        data = {'value': area.geometry.get_value()}
        context['zone'] = ZoneForm(data)

        return context

class AreaCreate(TemplateView):
    template_name = 'area/edit.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        data = json.loads(request.POST.dict()['object'])

        (errors, data) = Area().validate(data)
        if len(errors):
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )

        area = Area.create(data)

        return HttpResponse(
            json.dumps({"success": True, "id": area.id}),
            content_type="application/json"
        )

    def get_context_data(self, **kwargs):
        context = super(AreaCreate, self).get_context_data(**kwargs)
        context['area'] = Area()
        context['zone'] = ZoneForm()


        return context
