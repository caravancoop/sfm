from datetime import date

import json

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic.base import TemplateView
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db.models import Max

from .models import Emplacement


class EmplacementView(TemplateView):
    template_name = 'emplacement/search.html'

    def get_context_data(self, **kwargs):
        context = super(EmplacementView, self).get_context_data(**kwargs)

        context['year_range'] = range(1950, date.today().year + 1)
        context['day_range'] = range(1, 32)

        return context


def emplacement_search(request):
    terms = request.GET.dict()

    order_by = terms.get('orderby')
    if not order_by:
        order_by = 'emplacementstartdate__value'
    elif order_by in ['startdate']:
        order_by = 'person' + order_by + '__value'

    direction = terms.get('direction')
    if not direction:
        direction = 'ASC'

    dirsym = ''
    if direction == 'DESC':
        dirsym = '-'

    emplacement_query = (Emplacement.objects
                         .annotate(Max(order_by))
                         .order_by(dirsym + order_by + "__max"))

    page = int(terms.get('page', 1))

    startdate_year = terms.get('startdate_year')
    if startdate_year:
        emplacement_query = emplacement_query.filter(
            emplacementstartdate__value__startswith=startdate_year
        )

    startdate_month = terms.get('startdate_month')
    if startdate_month:
        emplacement_query = emplacement_query.filter(
            emplacementstartdate__value__contains="-" + startdate_month + "-"
        )

    startdate_day = terms.get('startdate_day')
    if startdate_day:
        emplacement_query = emplacement_query.filter(
            emplacementstartdate__value__endswith=startdate_day
        )

    enddate_year = terms.get('enddate_year')
    if enddate_year:
        emplacement_query = emplacement_query.filter(
            emplacementenddate__value__startswith=enddate_year
        )

    enddate_month = terms.get('enddate_month')
    if enddate_month:
        emplacement_query = emplacement_query.filter(
            emplacementenddate__value__contains="-" + enddate_month + "-"
        )

    enddate_day = terms.get('enddate_day')
    if enddate_day:
        emplacement_query = emplacement_query.filter(
            emplacementenddate__value__endswith=enddate_day
        )

    organization = terms.get('organization')
    if organization:
        emplacement_query = emplacement_query.filter(
            emplacementorganization__value__organizationname__value__icontains=organization
        )

    site = terms.get('site')
    if site:
        emplacement_query = emplacement_query.filter(
            emplacementsite__value__geositename__value__icontains=site
        )

    keys = ['startdate', 'enddate', 'organization', 'site']

    paginator = Paginator(emplacement_query, 15)
    try:
        emplacement_page = paginator.page(page)
    except PageNotAnInteger:
        person_page = paginator.page(1)
        page = 1
    except EmptyPage:
        person_page = paginator.page(paginator.num_pages)
        page = paginator.num_pages

    emplacements = [
        {
            "id": emplacement.id,
            "organization": str(emplacement.organization.get_value()),
            "site": str(emplacement.site.get_value()),
            "startdate": str(emplacement.startdate.get_value()),
            "enddate": str(emplacement.enddate.get_value()),
        }
        for emplacement in emplacement_page
    ]

    html_paginator = render_to_string(
        'paginator.html',
        {'actual': page, 'min': page - 5, 'max': page + 5,
         'paginator': emplacement_page,
         'pages': range(1, paginator.num_pages + 1)}
    )

    return HttpResponse(json.dumps({
        'success': True,
        'keys': keys,
        'objects': emplacements,
        'paginator': html_paginator,
        'result_number': len(emplacement_query)
    }))


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

