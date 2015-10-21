import json

from datetime import date

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic.edit import UpdateView, DeleteView
from django.views.generic.base import TemplateView
from django.utils.translation import ugettext as _
from django.shortcuts import render, render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.http import HttpResponse
from django.db.models import Max
from .models import Person, PersonName
from membership.models import Membership

def ajax_request(function):
    def wrapper(request, *args, **kwargs):
        if not request.is_ajax():
            return render_to_response('person/errors.html', {},
                                      context_instance=RequestContext(request))
        else:
            return function(request, *args, **kwargs)
    return wrapper

class PersonView(TemplateView):
    template_name = 'person/search.html'

    def get_context_data(self, **kwargs):
        context = super(PersonView, self).get_context_data(**kwargs)

        context['year_range'] = range(1950, date.today().year + 1)
        context['day_range'] = range(1, 32)

        return context


def person_search(request):
    terms = request.GET.dict()

    persons = Person.objects.all()

    order_by = terms.get('orderby')
    if not order_by:
        order_by = 'personname__value'
    elif order_by in ['name']:
        order_by = 'person' + order_by + '__value'

    direction = terms.get('direction')
    if not direction:
        direction = 'ASC'

    dirsym = ''
    if direction == 'DESC':
        dirsym = '-'

    person_query = (Person.objects
                    .annotate(Max(order_by))
                    .order_by(dirsym + order_by + "__max"))

    page = int(terms.get('page', 1))

    name = terms.get('name')
    if name:
        person_query = person_query.filter(personname__value__contains=name)

    alias_val = terms.get('alias')
    if alias_val:
        person_query = person_query.filter(personalias__value__contains=alias_val)

    deathdate_year = terms.get('deathdate_year')
    if deathdate_year:
        person_query = person_query.filter(persondeathdate__value__startswith=deathdate_year)

    deathdate_month = terms.get('deathdate_month')
    if deathdate_month:
        person_query = person_query.filter(persondeathdate__value__contains="-" + deathdate_month + "-")

    deathdate_day = terms.get('deathdate_day')
    if deathdate_day:
        person_query = person_query.filter(persondeathdate__value__endswith=deathdate_day)

    column_names = [_('Name'), _('Alias'), _('Death date')]
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
        'column_names': column_names,
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

        (errors, data) = person.validate(data, get_language())
        if len(errors):
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )

        person.update(data)
        return HttpResponse(
            json.dumps({"success": True}),
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

        (errors, data) = Person().validate(data, get_language())

        if len(errors):
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )

        Person.create(data)

        return HttpResponse(json.dumps({"success": True}), content_type="application/json")

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
