import json
import csv

from datetime import date

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.admin.utils import NestedObjects
from django.contrib import messages
from django.views.generic.edit import DeleteView, FormView
from django.views.generic import TemplateView, DetailView
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db import DEFAULT_DB_ALIAS
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext as _
from django.utils.translation import get_language

from extra_views import FormSetView

from person.models import Person, PersonName, PersonAlias, Alias
from person.forms import PersonForm
from organization.models import Organization
from source.models import Source
from membershipperson.models import MembershipPerson, Role
from sfm_pc.utils import deleted_in_str
from sfm_pc.base_views import BaseFormSetView, BaseUpdateView

class PersonDetail(DetailView):
    model = Person
    template_name = 'person/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['memberships'] = []
        memberships = context['person'].membershippersonmember_set.all()
        for membership in memberships:
            context['memberships'].append(membership.object_ref)

        context['events'] = []

        return context

class PersonCreate(BaseFormSetView):
    template_name = 'person/create.html'
    form_class = PersonForm
    success_url = reverse_lazy('create-membership')
    extra = 1
    max_num = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['organizations'] = self.request.session['organizations']
        context['source'] = Source.objects.get(id=self.request.session['source_id'])
        return context
    
    def formset_invalid(self, formset):
        response = super().formset_invalid(formset)

        for index, form in enumerate(formset.forms):
            alias_ids = formset.data.get('form-{}-alias'.format(index))
            if alias_ids:
                for alias_id in alias_ids:
                    try:
                        person_alias = PersonAlias.objects.get(id=alias_id)
                    except ValueError:
                        person_alias = None
                    
                    if person_alias:
                        try:
                            form.aliases.append(org_alias)
                        except AttributeError:
                            form.aliases = [org_alias]
            else:
                form.aliases = None
        
        return response

    def formset_valid(self, formset):
        response = super().formset_valid(formset)
        num_forms = int(formset.data['form-TOTAL_FORMS'][0])
        
        self.people = []
        self.memberships = []

        self.source = Source.objects.get(id=self.request.session['source_id'])
        
        for i in range(0,num_forms):
            first = True

            form_prefix = 'form-{0}-'.format(i)
            
            form_keys = [k for k in formset.data.keys() \
                             if k.startswith(form_prefix)]
            
            name_id_key = 'form-{0}-name'.format(i)
            name_text_key = 'form-{0}-name_text'.format(i)
            division_id_key = 'form-{}-division_id'.format(i)
            
            name_id = formset.data[name_id_key]
            name_text = formset.data[name_text_key]
            division_id = formset.data[division_id_key]

            person_info = {
                'Person_PersonName': {
                    'value': name_text,
                    'confidence': 1,
                    'sources': [self.source],
                },
                'Person_PersonDivisionId': {
                    'value': division_id,
                    'confidence': 1,
                    'sources': [self.source],
                }
            }
           
            if name_id == 'None':
                return self.formset_invalid(formset)

            elif name_id == '-1':
                
                person = Person.create(person_info)      
            else:
                person = Person.objects.get(id=name_id)
                person_info['Person_PersonName']['sources'] = self.sourcesList(person, 'name')
                person.update(person_info)

            alias_id_key = 'form-{0}-alias'.format(i)
            alias_text_key = 'form-{0}-alias_text'.format(i)
            
            aliases = formset.data.getlist(alias_text_key)
            
            for alias in aliases:
                
                alias_obj, created = Alias.objects.get_or_create(value=alias)

                pa_obj, created = PersonAlias.objects.get_or_create(object_ref=person,
                                                                    value=alias_obj,
                                                                    lang=get_language())
                
                pa_obj.sources.add(self.source)
                pa_obj.save()

            self.people.append(person)
            
            orgs_key = 'form-{0}-orgs'.format(i)
            orgs = formset.data.getlist(orgs_key)

            for org in orgs:
                mem_data = {
                    'MembershipPerson_MembershipPersonMember': {
                        'value': person,
                        'confidence': 1,
                        'sources': [self.source],
                    },
                    'MembershipPerson_MembershipPersonOrganization': { 
                        'value': Organization.objects.get(id=org),
                        'confidence': 1,
                        'sources': [self.source],
                    }
                }
                membership = MembershipPerson.create(mem_data)
                self.memberships.append({
                    'person': str(person.name),
                    'organization': str(Organization.objects.get(id=org).name),
                    'membership': membership.id,
                    'first': first
                })
                first = False
        
        self.request.session['people'] = [{'id': p.id, 'name': p.name.get_value().value} \
                                                     for p in self.people]
        self.request.session['memberships'] = self.memberships
        return response

def person_autocomplete(request):
    term = request.GET.get('q')
    people = Person.objects.filter(personname__value__icontains=term).all()
    results = []
    for person in people:
        results.append({
            'text': str(person.name),
            'id': person.id,
        })
    return HttpResponse(json.dumps(results), content_type='application/json')

def alias_autocomplete(request):
    term = request.GET.get('q')
    alias_query = PersonAlias.objects.filter(value__value__icontains=term)
    results = []
    for alias in alias_query:
        results.append({
            'text': alias.value.value,
            'id': alias.value.id
        })
    return HttpResponse(json.dumps(results), content_type='application/json')

class PersonUpdate(BaseUpdateView):
    template_name = 'person/edit.html'
    form_class = PersonForm
    success_url = reverse_lazy('dashboard')
    sourced = True

    def post(self, request, *args, **kwargs):

        self.checkSource(request)
        
        self.aliases = request.POST.getlist('alias')

        self.validateForm()
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        person = Person.objects.get(pk=self.kwargs['pk'])
        
        person_info = {
            'Person_PersonName': {
                'value': form.cleaned_data['name_text'],
                'confidence': 1,
                'sources': self.sourcesList(person, 'name'),
            },
            'Person_PersonDivisionId': {
                'value': form.cleaned_data['division_id'],
                'confidence': 1,
                'sources': [self.sourcesList(person, 'division_id')]
            }
        }
        
        person.update(person_info)

        if self.aliases:
            for alias in self.aliases:
                
                alias_obj, created = Alias.objects.get_or_create(value=alias)

                pa_obj, created = PersonAlias.objects.get_or_create(object_ref=person,
                                                                    value=alias_obj,
                                                                    lang=get_language())
                
                pa_obj.sources.add(source)
                pa_obj.save()

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person = Person.objects.get(pk=self.kwargs['pk'])
        
        form_data = {
            'name': person.name.get_value(),
            'aliases': [i.get_value() for i in person.aliases.get_list()],
            'division_id': person.division_id.get_value(),
        }
        
        context['form_data'] = form_data
        context['title'] = _('Person')
        context['source_object'] = person
        context['memberships'] = MembershipPerson.objects.filter(
            membershippersonmember__value=person
        ).filter(membershippersonorganization__value__isnull=False)
        context['source'] = Source.objects.filter(id=self.request.GET.get('source_id')).first()

        if not self.sourced:
            context['source_error'] = 'Please include the source for your changes'


        return context

#############################################
###                                       ###
### Below here are currently unused views ###
### which we'll probably need eventually  ###
###                                       ###
#############################################

class PersonDelete(DeleteView):
    model = Person
    template_name = "delete_confirm.html"

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


