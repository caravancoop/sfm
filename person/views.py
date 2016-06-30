import json
import csv

from datetime import date

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.admin.utils import NestedObjects
from django.contrib import messages
from django.views.generic.edit import DeleteView, FormView
from django.views.generic.base import TemplateView
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db import DEFAULT_DB_ALIAS
from django.core.urlresolvers import reverse_lazy

from extra_views import FormSetView

from person.models import Person, PersonName, PersonAlias, Alias
from person.forms import PersonForm
from organization.models import Organization
from source.models import Source
from membershipperson.models import MembershipPerson, Role
from sfm_pc.utils import deleted_in_str

class PersonCreate(FormSetView):
    template_name = 'person/create.html'
    form_class = PersonForm
    success_url = reverse_lazy('create-membership')
    extra = 1
    max_num = None

    def dispatch(self, *args, **kwargs):
        # Redirect to source creation page if no source in session
        if not self.request.session.get('source_id'):
            messages.add_message(self.request, 
                                 messages.INFO, 
                                 "Before adding a person, please tell us about your source.",
                                 extra_tags='alert alert-info')
            return redirect(reverse_lazy('create-source'))
        else:
            return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['organizations'] = self.request.session['organizations']
        context['source'] = Source.objects.get(id=self.request.session['source_id'])
        return context

    def post(self, request, *args, **kwargs):
        PersonFormSet = self.get_formset()
        formset = PersonFormSet(request.POST)       
        if formset.is_valid():
            return self.formset_valid(formset)
        else:
            return self.formset_invalid(formset)

    def formset_valid(self, formset):
        response = super().formset_valid(formset)
        num_forms = int(formset.data['form-TOTAL_FORMS'][0])
        
        self.people = []
        self.memberships = []

        source = Source.objects.get(id=self.request.session['source_id'])

        for i in range(0,num_forms):
            first = True

            form_prefix = 'form-{0}-'.format(i)
            
            form_keys = [k for k in formset.data.keys() \
                             if k.startswith(form_prefix)]
            
            name_id_key = 'form-{0}-name'.format(i)
            name_text_key = 'form-{0}-name_text'.format(i)
            
            name_id = formset.data[name_id_key]
            name_text = formset.data[name_text_key]
           
            if name_id == 'None':
                return self.formset_invalid(formset)

            elif name_id == '-1':
                person_info = {
                    'Person_PersonName': {
                        'value': name_text, 
                        'confidence': 1,
                        'sources': [source],
                    },
                }
                
                person = Person.create(person_info)      
            else:
                person = Person.objects.get(id=name_id)
            
            alias_id_key = 'form-{0}-alias'.format(i)
            alias_text_key = 'form-{0}-alias_text'.format(i)
            
            aliases = formset.data.getlist(alias_text_key)
            
            for alias in aliases:
                
                alias_obj, created = Alias.objects.get_or_create(value=alias)

                pa_obj, created = PersonAlias.objects.get_or_create(object_ref=person,
                                                                    value=alias_obj)
                
                pa_obj.sources.add(source)
                pa_obj.save()

            self.people.append(person)
            
            orgs_key = 'form-{0}-orgs'.format(i)
            orgs = formset.data.getlist(orgs_key)

            for org in orgs:
                mem_data = {
                    'MembershipPerson_MembershipPersonMember': {
                        'value': person,
                        'confidence': 1,
                        'sources': [source],
                    },
                    'MembershipPerson_MembershipPersonOrganization': { 
                        'value': Organization.objects.get(id=org),
                        'confidence': 1,
                        'sources': [source],
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

class PersonUpdate(FormView):
    template_name = 'person/edit.html'
    form_class = PersonForm
    success_url = reverse_lazy('dashboard')
    sourced = True

    def post(self, request, *args, **kwargs):

        form = PersonForm(request.POST)

        if not request.POST.get('source'):
            self.sourced = False
            return self.form_invalid(form)
        
        self.aliases = request.POST.getlist('alias')

        if form.is_valid():
            return self.form_valid()
        else:
            return self.form_invalid()
    
    def sources_list(self, obj, attribute):
        sources = [s for s in getattr(obj, attribute).get_sources()] \
                      + [self.source]
        return list(set(s for s in sources))

    def form_valid(self, form):
        response = super().form_valid(form)
        
        person = Person.objects.get(pk=self.kwargs['pk'])

        person_info = {
            'Person_PersonName': {
                'value': form.cleaned_data['name_text'],
                'confidence': 1,
                'sources': self.sources_list(person, 'name'),
            }
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person = Person.objects.get(pk=self.kwargs['pk'])
        
        form_data = {
            'name': person.name.get_value(),
            'alias': [i.get_value() for i in person.alias.get_list()],
        }

        context['form_data'] = form_data
        context['title'] = _('Person')
        context['person'] = person
        
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


