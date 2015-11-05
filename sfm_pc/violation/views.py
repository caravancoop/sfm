import json
from datetime import date

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic.base import TemplateView
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db.models import Max
from django.contrib.gis import geos

from .models import Violation, Type
from source.models import Source
from .forms import ZoneForm


class ViolationView(TemplateView):
    template_name = 'violation/search.html'

    def get_context_data(self, **kwargs):
        context = super(ViolationView, self).get_context_data(**kwargs)

        context['year_range'] = range(1950, date.today().year + 1)
        context['day_range'] = range(1, 32)

        return context

def violation_search(request):
    terms = request.GET.dict()

    order_by = terms.get('orderby')
    if not order_by:
        order_by = 'violationstartdate__value'
    elif order_by in ['startdate']:
        order_by = 'violation' + order_by + '__value'

    direction = terms.get('direction')
    if not direction:
        direction = 'ASC'

    dirsym = ''
    if direction == 'DESC':
        dirsym = '-'

    violation_query = (Violation.objects
                    .annotate(Max(order_by))
                    .order_by(dirsym + order_by + "__max"))

    startdate_year = terms.get('startdate_year')
    if startdate_year:
        violation_query = violation_query.filter(
            violationstartdate__value__startswith=startdate_year
        )

    startdate_month = terms.get('startdate_month')
    if startdate_month:
        violation_query = violation_query.filter(
            violationstartdate__value__contains="-" + startdate_month + "-"
        )

    startdate_day = terms.get('startdate_day')
    if startdate_day:
        violation_query = violation_query.filter(
            violationstartdate__value__endswith=startdate_day
        )

    enddate_year = terms.get('enddate_year')
    if enddate_year:
        violation_query = violation_query.filter(
            violationenddate__value__startswith=enddate_year
        )

    enddate_month = terms.get('enddate_month')
    if enddate_month:
        violation_query = violation_query.filter(
            violationenddate__value__contains="-" + enddate_month + "-"
        )

    enddate_day = terms.get('enddate_day')
    if enddate_day:
        violation_query = violation_query.filter(
            violationenddate__value__endswith=enddate_day
        )

    admin1 = terms.get('adminlevel1')
    if admin1:
        violation_query = violation_query.filter(
            violationadminlevel1__value__icontains=admin1
        )

    admin2 = terms.get('adminlevel2')
    if admin2:
        violation_query = violation_query.filter(
            violationadminlevel2__value__icontains=admin2
        )

    loc_desc = terms.get('locationdescription')
    if loc_desc:
        violation_query = violation_query.filter(
            violationlocationdescription__value__icontains=loc_desc
        )

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
            violation_query = violation_query.filter(
                violationlocation__value__dwithin=(point, radius)
            )
        else:
            violation_query = violation_query.filter(
               violationlocation__value__bbcontains=point
            )

    geoname = terms.get('geoname')
    if geoname:
        violation_query = violation_query.filter(
            violationgeoname__value__icontains=geoname
        )

    geonameid = terms.get('geonameid')
    if geonameid:
        violation_query = violation_query.filter(violationgeonameid__value=geonameid)

    source = terms.get('source')
    if source:
        violation_query = violation_query.filter(
            violationsource__source__source__icontains=source
        )

    v_type = terms.get('v_type')
    if v_type:
        violation_query = violation_query.filter(
            violationtype__value__code__icontains=v_type
        )

    viol_descr = terms.get('description')
    if viol_descr:
        violation_query = violation_query.filter(
            violationdescription__value__icontains=viol_descr
        )

    perpetrator = terms.get('perpetrator')
    if perpetrator:
        violation_query = violation_query.filter(
            violationperpetrator__value__icontains=perpetrator
        )

    perpetratororganization = terms.get('perpetratororganization')
    if perpetratororganization:
        violation_query = violation_query.filter(
            violationperpetratororganization__value__icontains=perpetratororganization
        )


    page = int(terms.get('page', 1))

    keys = ['startdate', 'enddate', 'geoname', 'perpetrator', 'organization']

    paginator = Paginator(violation_query, 15)
    try:
        violation_page = paginator.page(page)
    except PageNotAnInteger:
        person_page = paginator.page(1)
        page = 1
    except EmptyPage:
        person_page = paginator.page(paginator.num_pages)
        page = paginator.num_pages

    violations = [
        {
            "id": violation.id,
            "startdate": str(violation.startdate.get_value()),
            "enddate": str(violation.enddate.get_value()),
            "geoname": str(violation.geoname.get_value()),
            "perpetrator": str(violation.perpetrator.get_value()),
            "organization": str(violation.perpetratororganization.get_value()),
        }
        for violation in violation_page
    ]

    html_paginator = render_to_string(
        'paginator.html',
        {'actual': page, 'min': page - 5, 'max': page + 5,
         'paginator': violation_page,
         'pages': range(1, paginator.num_pages + 1)}
    )

    return HttpResponse(json.dumps({
        'success': True,
        'keys': keys,
        'objects': violations,
        'paginator': html_paginator,
        'result_number': len(violation_query)
    }))


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

        (errors, data) = violation.validate(data)
        if len(errors):
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )

        violation.update(data)

        return HttpResponse(
            json.dumps({"success": True}),
            content_type="application/json"
        )

    def get_context_data(self, **kwargs):
        context = super(ViolationUpdate, self).get_context_data(**kwargs)
        violation = Violation.objects.get(pk=context.get('pk'))
        context['violation'] = violation
        data = {"value": violation.location.get_value()}
        context['point'] = ZoneForm(data)

        return context

class ViolationCreate(TemplateView):
    template_name = 'violation/edit.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        data = json.loads(request.POST.dict()['object'])
        (errors, data) = Violation().validate(data)

        if len(errors):
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )
        violation = Violation.create(data)

        return HttpResponse(json.dumps({"success": True, "id": violation.id}),
                            content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super(ViolationCreate, self).get_context_data(**kwargs)
        context['violation'] = Violation()
        context['violationtypes'] = Type.objects.all()
        context['sources'] = Source.objects.all()
        context['point'] = ZoneForm()

        return context
