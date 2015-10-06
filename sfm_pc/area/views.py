import json

from django.views.generic.base import TemplateView
from django.http import HttpResponse

from .models import Area
from .forms import ZoneForm



class AreaCreate(TemplateView):
    template_name = 'area/edit.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        data = json.loads(request.POST.dict()['object'])
        area = Area.create(data)

        return HttpResponse(json.dumps({"success": True}), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super(AreaCreate, self).get_context_data(**kwargs)
        context['area'] = Area()
        context['zone'] = ZoneForm()


        return context
