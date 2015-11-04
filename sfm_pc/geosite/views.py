import json

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic.base import TemplateView
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db.models import Max
from django.contrib.gis import geos

from .forms import ZoneForm
from .models import Geosite


class SiteView(TemplateView):
    template_name = 'site/search.html'

    def get_context_data(self, **kwargs):
        context = super(SiteView, self).get_context_data(**kwargs)

def site_search(request):
    terms = request.GET.dict()

    order_by = terms.get('orderby')
    if not order_by:
        order_by = 'geositename__value'
    elif order_by in ['name']:
        order_by = 'geosite' + order_by + '__value'

    direction = terms.get('direction')
    if not direction:
        direction = 'ASC'

    dirsym = ''
    if direction == 'DESC':
        dirsym = '-'

    geosite_query = (Geosite.objects
                    .annotate(Max(order_by))
                    .order_by(dirsym + order_by + "__max"))

    page = int(terms.get('page', 1))

    name = terms.get('name')
    if name:
        geosite_query = geosite_query.filter(geositename__value__icontains=name)

    admin1 = terms.get('adminlevel1')
    if admin1:
        geosite_query = geosite_query.filter(geositeadminlevel1__value__icontains=admin1)

    admin2 = terms.get('adminlevel2')
    if admin2:
        geosite_query = geosite_query.filter(geositeadminlevel2__value__icontains=admin2)

    latitude = terms.get('latitude')
    longitude = terms.get('longitude')
    if latitude and longitude:
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            latitude = 0
            longitude = 0

        point = geos.Point(latitude, longitude)
        radius = terms.get('radius')
        if radius:
            try:
                radius = float(radius)
            except ValueError:
                radius = 0
            geosite_query = geosite_query.filter(
                geositecoordinates__value__dwithin=(point, radius)
            )
        else:
            geosite_query = geosite_query.filter(
               geositecoordinates__value__bbcontains=point
            )

    geoname = terms.get('geoname')
    if geoname:
        geosite_query = geosite_query.filter(geositegeoname__value__icontains=geoname)

    geonameid = terms.get('geonameid')
    if geonameid:
        geosite_query = geosite_query.filter(geositegeonameid__value=geonameid)

    keys = ['name', 'geoname', 'geonameid']

    paginator = Paginator(geosite_query, 15)
    try:
        geosite_page = paginator.page(page)
    except PageNotAnInteger:
        person_page = paginator.page(1)
        page = 1
    except EmptyPage:
        person_page = paginator.page(paginator.num_pages)
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
        context = self.get_context_data()
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
