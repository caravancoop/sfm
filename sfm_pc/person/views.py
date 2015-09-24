import json

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic.edit import UpdateView, DeleteView
from django.views.generic.base import TemplateView
from django.utils.translation import ugettext as _
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.db.models import Max
from .models import Person, PersonName

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

        persons = Person.objects.all()
        context['persons'] = persons

        order_by = self.request.GET.get('orderby')
        if not order_by:
            order_by = 'personname__value'

        direction = self.request.GET.get('direction')
        if not direction:
            direction = 'ASC'

        dirsym = ''
        if direction == 'DESC':
            dirsym = '-'

        person_query = (Person.objects
                        .annotate(Max(order_by))
                        .order_by(dirsym + order_by + "__max"))


        name = self.request.GET.get('Person_PersonName')
        if name:
            person_query = person_query.filter(personname__value__contains=name)

        alias_val = self.request.GET.get('Person_PersonAlias')
        if alias_val:
            person_query = person_query.filter(personalias__value__contains=alias_val)

        """death_date = self.request.GET.get('Person_PersonDeathDate')
        if death_date:
            person_query = person_query.filter(persondeathdate__value__contains=alias_val)
        """

        context['persons'] = person_query
        """
        currlist = [
            {
                'person_id': p.id,
                'name': p.get_name() or '',
                'alias': p.get_alias(),
                'notes': p.get_notes()
            }
            for p in person_query
        ]

        paginator = Paginator(currlist, 200)

        page = self.request.GET.get('page')
        try:
            person = paginator.page(page)
        except PageNotAnInteger:
            person = paginator.page(1)
        except EmptyPage:
            person = paginator.page(paginator.num_pages)

        context['person'] = person
        """
        context['orderby'] = order_by
        context['direction'] = direction

        return context

class PersonUpdate(TemplateView):
    template_name = 'person/edit.html'

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.dict()['person'])
        try:
            person = Person.objects.get(pk=kwargs.get('pk'))
        except Person.DoesNotExist:
            return HttpResponse(status=418)

        errors = person.update(data)
        if errors is None:
            return HttpResponse(
                json.dumps({"success": True}),
                content_type="application/json"
            )
        else:
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )

    def get_context_data(self, **kwargs):
        context = super(PersonUpdate, self).get_context_data(**kwargs)
        context['title'] = "Person"
        context['person'] = Person.objects.get(pk=context.get('pk'))

        return context

class FieldUpdate(TemplateView):
    template_name = 'field/popup/edit.html'

    def get_context_data(self, **kwargs):
        context = super(FieldUpdate, self).get_context_data(**kwargs)
        person = Person.from_id(context.get('person_id'))
        field = person.get_attribute_object(
            "Person"+context.get('field_type').capitalize()
        )
        context['field'] = field

        return context

class PersonCreate(TemplateView):
    template_name = 'person/edit.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        data = json.loads(request.POST.dict()['person'])
        person = Person.create(data)

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
            'value': str(name.object_ref_id) + ": " + name.object_ref.name.get_value()
        }
        for name in person_names
    ]

    return HttpResponse(json.dumps(persons))
