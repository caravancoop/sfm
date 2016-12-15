import json
import csv

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.admin.utils import NestedObjects
from django.views.generic.edit import DeleteView
from django.views.generic.base import TemplateView
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db import DEFAULT_DB_ALIAS

from .forms import ZoneForm
from .models import Geosite
from sfm_pc.utils import deleted_in_str


class GeositeDelete(DeleteView):
    model = Geosite
    template_name = "delete_confirm.html"

    def get_context_data(self, **kwargs):
        context = super(GeositeDelete, self).get_context_data(**kwargs)
        collector = NestedObjects(using=DEFAULT_DB_ALIAS)
        collector.collect([context['object']])
        deleted_elements = collector.nested()
        context['deleted_elements'] = deleted_in_str(deleted_elements)
        return context

    def get_object(self, queryset=None):
        obj = super(GeositeDelete, self).get_object()

        return obj


class SiteView(TemplateView):
    template_name = 'site/search.html'


def geosite_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="geosites.csv"'

    terms = request.GET.dict()
    geosite_query = Geosite.search(terms)

    writer = csv.writer(response)
    for geosite in geosite_query:
        writer.writerow([
            geosite.id,
            geosite.name.get_value(),
            geosite.adminlevel1.get_value(),
            geosite.adminlevel2.get_value(),
            geosite.osmname.get_value(),
            geosite.osmid.get_value(),
            str(geosite.coordinates.get_value())
        ])

    return response


def site_search(request):
    terms = request.GET.dict()

    page = int(terms.get('page', 1))
    geosite_query = Geosite.search(terms)

    keys = ['name', 'geoname', 'geonameid']

    paginator = Paginator(geosite_query, 15)
    try:
        geosite_page = paginator.page(page)
    except PageNotAnInteger:
        geosite_page = paginator.page(1)
        page = 1
    except EmptyPage:
        geosite_page = paginator.page(paginator.num_pages)
        page = paginator.num_pages

    geosites = [
        {
            "id": geosite.id,
            "name": str(geosite.name.get_value()),
            "geoname": str(geosite.geoname.get_value()),
            "geonameid": str(geosite.geonameid.get_value()),
        }
        for geosite in geosite_page
    ]

    html_paginator = render_to_string(
        'paginator.html',
        {'actual': page, 'min': page - 5, 'max': page + 5,
         'paginator': geosite_page,
         'pages': range(1, paginator.num_pages + 1)}
    )

    return HttpResponse(json.dumps({
        'success': True,
        'keys': keys,
        'objects': geosites,
        'paginator': html_paginator,
        'result_number': len(geosite_query)
    }))


class SiteUpdate(TemplateView):
    template_name = 'site/edit.html'

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.dict()['object'])
        try:
            geosite = Geosite.objects.get(pk=kwargs.get('pk'))
        except Geosite.DoesNotExist:
            msg = "This site does not exist, it should be created " \
                  "before updating it."
            return HttpResponse(msg, status=400)

        (errors, data) = geosite.validate(data)
        if len(errors):
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )

        geosite.update(data)

        return HttpResponse(
            json.dumps({"success": True}),
            content_type="application/json"
        )

    def get_context_data(self, **kwargs):
        context = super(SiteUpdate, self).get_context_data(**kwargs)
        site = Geosite.objects.get(pk=context.get('pk'))
        context['site'] = site
        data = {'value': site.coordinates.get_value()}
        context['zone'] = ZoneForm(data)

        return context


class SiteCreate(TemplateView):
    template_name = 'site/edit.html'

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.dict()['object'])

        (errors, data) = Geosite().validate(data)
        if len(errors):
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )

        site = Geosite.create(data)

        return HttpResponse(json.dumps({"success": True, "id": site.id}),
                            content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super(SiteCreate, self).get_context_data(**kwargs)
        context['site'] = Geosite()
        context['zone'] = ZoneForm()

        return context


def site_autocomplete(request):
    data = request.GET.dict()['term']

    sites = Geosite.objects.filter(
        geositename__value__icontains=data
    )

    sites = [
        {"value": site.id, "label": _(site.name.get_value())}
        for site in sites
    ]

    return HttpResponse(json.dumps(sites))
