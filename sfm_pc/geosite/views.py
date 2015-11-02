import json

from django.views.generic.base import TemplateView
from django.utils.translation import ugettext as _
from django.http import HttpResponse

from .models import Site


class SiteView(TemplateView):
    template_name = 'site/search.html'

    def get_context_data(self, **kwargs):
        context = super(SiteView, self).get_context_data(**kwargs)


class SiteUpdate(TemplateView):
    template_name = 'site/edit.html'

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.dict()['object'])
        try:
            site = Site.objects.get(pk=kwargs.get('pk'))
        except Site.DoesNotExist:
            msg = "This site does not exist, it should be created " \
                  "before updating it."
            return HttpResponse(msg, status=400)

        errors = site.update(data)
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
        context = super(SiteUpdate, self).get_context_data(**kwargs)
        site = Site.objects.get(pk=context.get('pk'))
        context['site'] = site

        return context

class SiteCreate(TemplateView):
    template_name = 'site/edit.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        data = json.loads(request.POST.dict()['object'])
        site = Site.create(data)

        return HttpResponse(json.dumps({"success": True}), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super(SiteCreate, self).get_context_data(**kwargs)
        context['site'] = Site()


        return context


def site_autocomplete(request):
    data = request.GET.dict()['term']

    sites = Site.objects.filter(
        sitename__value__icontains=data
    )

    sites = [
        {"value": site.id, "label": _(site.name.get_value())}
        for site in sites
    ]

    return HttpResponse(json.dumps(sites))
