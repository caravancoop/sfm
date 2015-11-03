from datetime import date

import json

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic.base import TemplateView
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.http import HttpResponse

from .models import Association


class AssociationView(TemplateView):
    template_name = 'association/search.html'

    def get_context_data(self, **kwargs):
        context = super(AssociationView, self).get_context_data(**kwargs)

        context['year_range'] = range(1955, date.today().year + 1)
        context['day_range'] = range(1, 31)

        return context


def association_search(request):
    terms = request.GET.dict()

    association_query = Association.objects.all()
    page = int(terms.get('page', 1))

    column_names = [_('Start date'), _('End date'), _('Organization'), _('Area')]
    keys = ['startdate', 'enddate', 'organization', 'area']

    paginator = Paginator(association_query, 15)
    try:
        association_page = paginator.page(page)
    except PageNotAnInteger:
        person_page = paginator.page(1)
        page = 1
    except EmptyPage:
        person_page = paginator.page(paginator.num_pages)
        page = paginator.num_pages

    associations = [
        {
            "id": association.id,
            "organization": str(association.organization.get_value()),
            "area": str(association.area.get_value()),
            "startdate": str(association.startdate.get_value()),
            "enddate": str(association.enddate.get_value()),
        }
        for association in association_page
    ]

    html_paginator = render_to_string(
        'paginator.html',
        {'actual': page, 'min': page - 5, 'max': page + 5,
         'paginator': association_page,
         'pages': range(1, paginator.num_pages + 1)}
    )

    return HttpResponse(json.dumps({
        'success': True,
        'column_names': column_names,
        'keys': keys,
        'objects': associations,
        'paginator': html_paginator,
        'result_number': len(association_query)
    }))


class AssociationUpdate(TemplateView):
    template_name = 'association/edit.html'

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.dict()['object'])
        try:
            association = Association.objects.get(pk=kwargs.get('pk'))
        except Association.DoesNotExist:
            msg = "This association does not exist, it should be created " \
                  "before updating it."
            return HttpResponse(msg, status=400)

        (errors, data) = association.validate(data)
        if len(errors):
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )

        association.update(data)
        return HttpResponse(
            json.dumps({"success": True}),
            content_type="application/json"
        )

    def get_context_data(self, **kwargs):
        context = super(AssociationUpdate, self).get_context_data(**kwargs)
        association = Association.objects.get(pk=context.get('pk'))
        context['association'] = association

        return context

class AssociationCreate(TemplateView):
    template_name = 'association/edit.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        data = json.loads(request.POST.dict()['object'])
        (errors, data) = Association().validate(data)
        if len(errors):
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )

        association = Association.create(data)

        return HttpResponse(json.dumps({"success": True, "id": association.id}),
                            content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super(AssociationCreate, self).get_context_data(**kwargs)
        context['association'] = Association()

        return context

