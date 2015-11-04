import json
from datetime import date

from django.views.generic.edit import UpdateView
from django.views.generic.base import TemplateView
from django.utils.translation import ugettext as _
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Max
from django.contrib.gis import geos

from .models import Organization, Classification


class OrganizationView(TemplateView):
    template_name = 'organization/search.html'

    def get_context_data(self, **kwargs):
        context = super(OrganizationView, self).get_context_data(**kwargs)

        context['year_range'] = range(1950, date.today().year + 1)
        context['day_range'] = range(1, 32)
        context['classifications'] = Classification.objects.all()

        return context

def organization_search(request):
    terms = request.GET.dict()

    order_by = terms.get('orderby')
    if not order_by:
        order_by = 'organizationname__value'

    direction = terms.get('direction')
    if not direction:
        direction = 'ASC'

    dirsym = ''
    if direction == 'DESC':
        dirsym = '-'

    orgs_query = (Organization.objects
                  .annotate(Max(order_by))
                  .order_by(dirsym + order_by + "__max"))


    name = terms.get('name')
    if name:
        orgs_query = orgs_query.filter(organizationname__value__icontains=name)

    alias_val = terms.get('alias')
    if alias_val:
        orgs_query = orgs_query.filter(organizationalias__value__icontains=alias_val)

    foundingdate_year = terms.get('founding_year')
    if foundingdate_year:
        orgs_query = orgs_query.filter(
            organizationfoundingdate__value__startswith=foundingdate_year
        )

    foundingdate_month = terms.get('founding_month')
    if foundingdate_month:
        orgs_query = orgs_query.filter(
            organizationfoundingdate__value__contains="-" + foundingdate_month + "-"
        )

    foundingdate_day = terms.get('founding_day')
    if foundingdate_day:
        orgs_query = orgs_query.filter(
            organizationfoundingdate__value__endswith=foundingdate_day
        )

    dissolutiondate_year = terms.get('dissolution_year')
    if dissolutiondate_year:
        orgs_query = orgs_query.filter(
            organizationdissolutiondate__value__startswith=dissolutiondate_year
        )

    dissolutiondate_month = terms.get('dissolution_month')
    if dissolutiondate_month:
        orgs_query = orgs_query.filter(
            organizationdissolutiondate__value__contains="-" + dissolutiondate_month + "-"
        )

    dissolutiondate_day = terms.get('dissolution_day')
    if dissolutiondate_day:
        orgs_query = orgs_query.filter(
            organizationdissolutiondate__value__endswith=dissolutiondate_day
        )

    classification = terms.get('classification')
    if classification:
        orgs_query = orgs_query.filter(organizationclassification__value_id=classification)

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
            orgs_query = orgs_query.filter(
                associationorganization__object_ref__associationarea__value__areageometry__value__dwithin=(point, radius)
            )
        else:
            orgs_query = orgs_query.filter(
                associationorganization__object_ref__associationarea__value__areageometry__value__bbcontains=point
            )

    keys = ['name', 'alias', 'classification', 'superiorunit', 'foundingdate',
            'dissolutiondate']
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
        for org in orgs_query
    ]

    return HttpResponse(json.dumps({
        'success': True,
        'keys': keys,
        'objects': orgs,
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
