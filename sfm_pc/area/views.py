import json

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template.loader import render_to_string
from django.views.generic.base import TemplateView
from django.utils.translation import ugettext as _
from django.http import HttpResponse
from django.db.models import Max
from django.contrib.gis import geos

from .models import Area, Code
from .forms import ZoneForm


class AreaView(TemplateView):
    template_name = 'area/search.html'

    def get_context_data(self, **kwargs):
        context = super(AreaView, self).get_context_data(**kwargs)

        context['codes'] = Code.objects.all()

        return context


def area_search(request):
    terms = request.GET.dict()

    order_by = terms.get('orderby')
    if not order_by:
        order_by = 'areaname__value'
    elif order_by in ['name']:
        order_by = 'area' + order_by + '__value'

    direction = terms.get('direction')
    if not direction:
        direction = 'ASC'

    dirsym = ''
    if direction == 'DESC':
        dirsym = '-'

    area_query = (Area.objects
                    .annotate(Max(order_by))
                    .order_by(dirsym + order_by + "__max"))

    page = int(terms.get('page', 1))

    name = terms.get('name')
    if name:
        area_query = area_query.filter(areaname__value__icontains=name)

    code = terms.get('classification')
    if code:
        area_query = area_query.filter(areacode__value=code)

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
            area_query = area_query.filter(
                areageometry__value__dwithin=(point, radius)
            )
        else:
            area_query = area_query.filter(
               areageometry__value__bbcontains=point
            )

    keys = ['name', 'code']

    paginator = Paginator(area_query, 15)
    try:
        area_page = paginator.page(page)
    except PageNotAnInteger:
        person_page = paginator.page(1)
        page = 1
    except EmptyPage:
        person_page = paginator.page(paginator.num_pages)
        page = paginator.num_pages

    areas = [
        {
            "id": area.id,
            "name": str(area.name.get_value()),
            "code": str(area.code.get_value()),
        }
        for area in area_page
    ]

    html_paginator = render_to_string(
        'paginator.html',
        {'actual': page, 'min': page - 5, 'max': page + 5,
         'paginator': area_page,
         'pages': range(1, paginator.num_pages + 1)}
    )

    return HttpResponse(json.dumps({
        'success': True,
        'keys': keys,
        'objects': areas,
        'paginator': html_paginator,
        'result_number': len(area_query)
    }))


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


def area_autocomplete(request):
    data = request.GET.dict()['term']

    areas = Area.objects.filter(
        areaname__value__icontains=data
    )

    areas = [
        {"value": area.id, "label": _(area.name.get_value())}
        for area in areas
    ]

    return HttpResponse(json.dumps(areas))


def code_autocomplete(request):
    data = request.GET.dict()['term']

    codes = Code.objects.filter(
        value__icontains=data
    )

    codes = [
        {"value": code.id, "label": _(code.value)}
        for code in codes
    ]

    return HttpResponse(json.dumps(codes))
