import json

from django.views.generic.edit import UpdateView
from django.views.generic.base import TemplateView
from django.utils.translation import ugettext as _
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Max

from .models import Organization, Classification


class OrganizationView(TemplateView):
    template_name = 'organization/search.html'

    def get_context_data(self, **kwargs):
        context = super(OrganizationView, self).get_context_data(**kwargs)

        order_by = self.request.GET.get('orderby')
        if not order_by:
            order_by = 'organizationname__value'

        direction = self.request.GET.get('direction')
        if not direction:
            direction = 'ASC'

        dirsym = ''
        if direction == 'DESC':
            dirsym = '-'

        org_query = (Organization.objects
                        .annotate(Max(order_by))
                        .order_by(dirsym + order_by + "__max"))

        name = self.request.GET.get('name')
        if name:
            org_query = org_query.filter(organizationname__value__contains=name)

        alias_val = self.request.GET.get('alias')
        if name:
            org_query = org_query.filter(
                organizationalias__value__contains=alias_val
            )

        context['organizations'] = org_query

        return context


class OrganizationCreate(TemplateView):
    template_name = 'organization/edit.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        data = json.loads(request.POST.dict()['organization'])
        organization = Organization.create(data)

        return HttpResponse(json.dumps({"success": True}),
                            content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super(OrganizationCreate, self).get_context_data(**kwargs)
        context['organization'] = Organization()

        return context


def classification_autocomplete(request):
    data = request.GET.dict()['term']

    classifications = Classification.objects.filter(
        value__icontains=data
    )

    classifications = [
        _(classif.value)
        for classif in classifications
    ]

    return HttpResponse(json.dumps(classifications))
