import json
from datetime import date

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic.base import TemplateView
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.http import HttpResponse

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

    page = int(terms.get('page', 1))
    violation_query = Violation.search(terms)

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
