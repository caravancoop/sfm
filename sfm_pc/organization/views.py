import json
import csv
from datetime import date

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.admin.util import NestedObjects
from django.views.generic.edit import DeleteView
from django.views.generic.base import TemplateView
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.gis import geos
from django.db import DEFAULT_DB_ALIAS

from .models import Organization, Classification
from sfm_pc.utils import deleted_in_str


class OrganizationDelete(DeleteView):
    model = Organization
    template_name = "delete_confirm.html"

    def get_context_data(self, **kwargs):
        context = super(OrganizationDelete, self).get_context_data(**kwargs)
        collector = NestedObjects(using=DEFAULT_DB_ALIAS)
        collector.collect([context['object']])
        deleted_elements = collector.nested()
        context['deleted_elements'] = deleted_in_str(deleted_elements)
        context['title'] = _("Organization")
        context['model'] = "organization"
        return context


    def get_object(self, queryset=None):
        obj = super(OrganizationDelete, self).get_object()

        return obj


class OrganizationView(TemplateView):
    template_name = 'organization/search.html'

    def get_context_data(self, **kwargs):
        context = super(OrganizationView, self).get_context_data(**kwargs)

        context['year_range'] = range(1950, date.today().year + 1)
        context['day_range'] = range(1, 32)
        context['classifications'] = Classification.objects.all()

        return context


def organization_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="organizations.csv"'

    terms = request.GET.dict()
    organization_query = Organization.search(terms)

    writer = csv.writer(response)
    for organization in organization_query:
        writer.writerow([
            organization.id,
            organization.name.get_value(),
            organization.alias.get_value(),
            organization.classification.get_value(),
            repr(organization.foundingdate.get_value()),
            repr(organization.dissolutiondate.get_value()),
            organization.realfounding.get_value(),
            organization.realdissolution.get_value(),
        ])

    return response


def organization_search(request):
    terms = request.GET.dict()

    page = int(terms.get('page', 1))

    keys = ['name', 'alias', 'classification', 'superiorunit', 'foundingdate',
            'dissolutiondate']

    orgs_query = Organization.search(terms)

    paginator = Paginator(orgs_query, 15)
    try:
        orgs_page = paginator.page(page)
    except PageNotAnInteger:
        orgs_page = paginator.page(1)
        page = 1
    except EmptyPage:
        orgs_page = paginator.page(paginator.num_pages)
        page = paginator.num_pages

    orgs = [
        {
            "id": org.id,
            "name": org.name.get_value(),
            "alias": org.alias.get_value(),
            "classification": str(org.classification.get_value()),
            "superiorunit": "TODO",
            "foundingdate": str(org.foundingdate.get_value()),
            "dissolutiondate": str(org.dissolutiondate.get_value()),
        }
        for org in orgs_page
    ]

    html_paginator = render_to_string(
        'paginator.html',
        {'acutal': page, 'min': page - 5, 'max': page + 5,
         'paginator': orgs_page,
         'pages': range(1, paginator.num_pages + 1) }
    )

    return HttpResponse(json.dumps({
        'success': True,
        'keys': keys,
        'objects': orgs,
        'paginator': html_paginator,
        'result_number': len(orgs_query)
    }))


class OrganizationUpdate(TemplateView):
    template_name = 'organization/edit.html'

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.dict()['object'])

        try:
            organization = Organization.objects.get(pk=kwargs.get('pk'))
        except Organization.DoesNotExist:
            msg = "This orgnanization does not exist, it should be created " \
                  "before updating it."
            return HttpResponse(msg, status=400)

        (errors, data) = organization.validate(data)
        if len(errors):
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )

        organization.update(data)
        return HttpResponse(
            json.dumps({"success": True}),
            content_type="application/json"
        )

    def get_context_data(self, **kwargs):
        context = super(OrganizationUpdate, self).get_context_data(**kwargs)
        context['title'] = "Organization"
        context['organization'] = Organization.objects.get(pk=context.get('pk'))

        return context


class OrganizationCreate(TemplateView):
    template_name = 'organization/edit.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        data = json.loads(request.POST.dict()['object'])
        (errors, data) = Organization().validate(data)
        if len(errors):
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )

        org = Organization.create(data)

        return HttpResponse(json.dumps({"success": True, "id": org.id}),
                            content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super(OrganizationCreate, self).get_context_data(**kwargs)
        context['organization'] = Organization()

        return context


def organization_autocomplete(request):
    data = request.GET.dict()['term']

    organizations = Organization.objects.filter(
        organizationname__value__icontains=data
    )

    organizations = [
        {"value": org.id, "label": _(org.name.get_value())}
        for org in organizations
    ]

    return HttpResponse(json.dumps(organizations))

def classification_autocomplete(request):
    data = request.GET.dict()['term']

    classifications = Classification.objects.filter(
        value__icontains=data
    )

    classifications = [
        {"value": classif.id, "label":_(classif.value)}
        for classif in classifications
    ]

    return HttpResponse(json.dumps(classifications))
