import json
import csv
from datetime import date

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.admin.utils import NestedObjects
from django.views.generic.edit import DeleteView, FormView
from django.views.generic.base import TemplateView
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db import DEFAULT_DB_ALIAS

from .models import Organization, OrganizationName, \
    OrganizationAlias, Alias as OrganizationAliasObject, Classification
from sfm_pc.utils import deleted_in_str
from sfm_pc.forms import OrgForm
from source.models import Source


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
            organization.realfounding.get_value(),
        ])

    return response


def organization_search(request):
    terms = request.GET.dict()

    page = int(terms.get('page', 1))

    keys = ['name', 'alias', 'classification', 'superiorunit', 'foundingdate']

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
            "name": str(org.name.get_value()),
            "alias": str(org.alias.get_value()),
            "classification": str(org.classification.get_value()),
            "superiorunit": "TODO",
            "foundingdate": str(org.foundingdate.get_value()),
        }
        for org in orgs_page
    ]

    html_paginator = render_to_string(
        'paginator.html',
        {'acutal': page, 'min': page - 5, 'max': page + 5,
         'paginator': orgs_page,
         'pages': range(1, paginator.num_pages + 1)}
    )
    
    return HttpResponse(json.dumps({
        'success': True,
        'keys': keys,
        'objects': orgs,
        'paginator': html_paginator,
        'result_number': len(orgs_query)
    }))


class OrganizationUpdate(FormView):
    template_name = 'organization/edit.html'
    form_class = OrgForm
    success_url = '/'
    sourced = True

    def post(self, request, *args, **kwargs):
        
        form = OrgForm(request.POST)
        
        if not request.POST.get('source'):
            self.sourced = False
            return self.form_invalid(form)
        else:
            self.source = Source.objects.get(id=request.POST.get('source'))
        
        self.aliases = request.POST.getlist('alias')

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        organization = Organization.objects.get(pk=self.kwargs['pk'])
        
        org_info = {
            'Organization_OrganizationName': {
                'value': form.cleaned_data['name_text'],
                'confidence': 1,
                'source': list(set(list(organization.name.get_sources()) + [self.source]))
            },
            'Organization_OrganizationClassification': {
                'value': form.cleaned_data['classification'],
                'confidence': 1,
                'source': list(set(list(organization.classification.get_sources()) + [self.source])),
            },
            'Organization_OrganizationFoundingDate': {
                'value': form.cleaned_data['foundingdate'],
                'confidence': 1,
                'sources': list(set(list(organization.foundingdate.get_sources()) + [self.source])),
            },
            'Organization_OrganizationRealFounding': {
                'value': form.cleaned_data['realfounding'],
                'confidence': 1,
                'sources': list(set(list(organization.realfounding.get_sources()) + [self.source])),
            },
        }
        
        organization.update(org_info)
        
        if self.aliases:

            aliases = OrganizationAlias.objects.filter(id__in=self.aliases)
            organization.organizationalias_set = aliases
            organization.save()

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization = Organization.objects.get(pk=self.kwargs['pk'])
        
        form_data = {
            'name': organization.name.get_value(),
            'classification': organization.classification.get_value(),
            'alias': [i.get_value() for i in organization.aliases.get_list()],
            'foundingdate': organization.foundingdate.get_value(),
            'realfounding': organization.realfounding.get_value(),
        }

        context['form_data'] = form_data
        context['title'] = 'Organization'
        context['organization'] = organization
        context['classifications'] = Classification.objects.all()
        
        if not self.sourced:
            context['source_error'] = 'Please include the source for your changes'

        return context


class OrganizationCreate(TemplateView):
    template_name = 'organization/edit.html'

    def post(self, request, *args, **kwargs):
        
        context = self.get_context_data()
        data = json.loads(request.POST.dict()['object'])
        
        for field_name, field_data in data.items():
            data[field_name]['sources'] = [Source.objects.first()]
            data[field_name]['confidence'] = 'High'
        
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
        {"value": org.id, "label": str(org.name)}
        for org in organizations
    ]

    return HttpResponse(json.dumps(organizations))


def classification_autocomplete(request):
    data = request.GET.dict()['term']

    classifications = Classification.objects.filter(
        value__icontains=data
    )

    classifications = [
        {"value": classif.id, "label": _(classif.value)}
        for classif in classifications
    ]

    return HttpResponse(json.dumps(classifications))
