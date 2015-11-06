import json
import csv

from datetime import date

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.gis.geos import Point
from django.contrib.admin.util import NestedObjects
from django.views.generic.edit import UpdateView, DeleteView
from django.views.generic.base import TemplateView
from django.utils.translation import ugettext as _
from django.shortcuts import render, render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.http import HttpResponse
from django.db import DEFAULT_DB_ALIAS

from .models import Person, PersonName
from membership.models import Membership, Role
from sfm_pc.utils import deleted_in_str


class PersonDelete(DeleteView):
    model = Person

    def get_context_data(self, **kwargs):
        context = super(PersonDelete, self).get_context_data(**kwargs)
        collector = NestedObjects(using=DEFAULT_DB_ALIAS)
        collector.collect([context['object']])
        deleted_elements = collector.nested()
        context['deleted_elements'] = deleted_in_str(deleted_elements)
        return context


    def get_object(self, queryset=None):
        obj = super(PersonDelete, self).get_object()

        return obj

class PersonView(TemplateView):
    template_name = 'person/search.html'

    def get_context_data(self, **kwargs):
        context = super(PersonView, self).get_context_data(**kwargs)

        context['year_range'] = range(1950, date.today().year + 1)
        context['day_range'] = range(1, 32)
        context['roles'] = Role.get_role_list()

        return context

def person_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="persons.csv"'

    terms = request.GET.dict()
    person_query = Person.search(terms)

    writer = csv.writer(response)
    for person in person_query:
        writer.writerow([
            person.id,
            person.name.get_value(),
            person.alias.get_value(),
            repr(person.deathdate.get_value())
        ])

    return response



def person_search(request):
    terms = request.GET.dict()

    page = int(terms.get('page', 1))

    person_query = Person.search(terms)

    keys = ['name', 'alias', 'deathdate']

    paginator = Paginator(person_query, 15)
    try:
        person_page = paginator.page(page)
    except PageNotAnInteger:
        person_page = paginator.page(1)
        page = 1
    except EmptyPage:
        person_page = paginator.page(paginator.num_pages)
        page = paginator.num_pages

    persons = [
        {
            "id": person.id,
            "name": person.name.get_value(),
            "alias": person.alias.get_value(),
            "deathdate": str(person.deathdate.get_value()),
        }
        for person in person_page
    ]

    html_paginator = render_to_string(
        'paginator.html',
        {'actual': page, 'min': page - 5, 'max': page + 5,
         'paginator': person_page,
         'pages': range(1, paginator.num_pages + 1) }
    )

    return HttpResponse(json.dumps({
        'success': True,
        'keys': keys,
        'objects': persons,
        'paginator': html_paginator,
        'result_number': len(person_query)
    }))


class PersonUpdate(TemplateView):
    template_name = 'person/edit.html'

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.dict()['object'])
        try:
            person = Person.objects.get(pk=kwargs.get('pk'))
        except Person.DoesNotExist:
            msg = "This person does not exist, it should be created " \
                  "before updating it."
            return HttpResponse(msg, status=400)

        (errors, data) = person.validate(data)
        if len(errors):
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )

        person.update(data)
        return HttpResponse(
            json.dumps({"success": True, "id": person.id}),
            content_type="application/json"
        )

    def get_context_data(self, **kwargs):
        context = super(PersonUpdate, self).get_context_data(**kwargs)
        context['title'] = "Person"
        context['person'] = Person.objects.get(pk=context.get('pk'))
        context['memberships'] = Membership.objects.filter(
            membershippersonmember__value=context['person']
        ).filter(membershiporganization__value__isnull=False)

        return context


class PersonCreate(TemplateView):
    template_name = 'person/edit.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        data = json.loads(request.POST.dict()['object'])

        (errors, data) = Person().validate(data)

        if len(errors):
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )

        person = Person.create(data)

        return HttpResponse(
            json.dumps({"success": True, "id": person.id}),
            content_type="application/json"
        )

    def get_context_data(self, **kwargs):
        context = super(PersonCreate, self).get_context_data(**kwargs)
        context['person'] = Person()

        return context


def person_autocomplete(request):
    term = request.GET.dict()['term']

    person_names = PersonName.objects.filter(value__icontains=term)

    persons = [
        {
            'label': _(name.object_ref.name.get_value()),
            'value': str(name.object_ref_id)
        }
        for name in person_names
    ]

    return HttpResponse(json.dumps(persons))
