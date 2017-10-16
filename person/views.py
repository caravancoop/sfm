import json
import csv

from datetime import date
from collections import namedtuple

from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.admin.utils import NestedObjects
from django.contrib import messages
from django.views.generic.edit import DeleteView, FormView
from django.views.generic import TemplateView, DetailView
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db import DEFAULT_DB_ALIAS
from django.db.models import Q
from django.db import connection
from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from django.contrib.auth.mixins import LoginRequiredMixin

from extra_views import FormSetView

from person.models import Person, PersonName, PersonAlias, Alias
from person.forms import PersonForm
from organization.models import Organization
from source.models import Source
from membershipperson.models import MembershipPerson, MembershipPersonMember, Role
from sfm_pc.utils import (deleted_in_str, get_org_hierarchy_by_id,
                          get_command_edges, get_command_nodes, Autofill)
from sfm_pc.base_views import BaseFormSetView, BaseUpdateView, PaginatedList


class PersonDetail(DetailView):
    model = Person
    template_name = 'person/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Generate link to download a CSV of this record
        params = '?download_etype=Person&entity_id={0}'.format(str(context['person'].uuid))

        context['download_url'] = reverse('download') + params

        affiliations = context['person'].memberships
        memberships = tuple(mem.object_ref for mem in affiliations)

        context['memberships'] = memberships
        context['subordinates'] = []
        context['superiors'] = []
        context['command_chain'] = []

        for membership in memberships:

            # Grab the org object
            org = membership.organization.get_value().value
            org_id = str(org.uuid)

            # Get info about chain of command
            mem_data = {}

            when = None
            if membership.lastciteddate.get_value():
                when = repr(membership.lastciteddate.get_value().value)
                mem_data['when'] = when

            kwargs = {'org_id': org_id}
            ajax_route = 'command-chain'
            if when:
                kwargs['when'] = when
                ajax_route = 'command-chain-bounded'

            command_chain_url = reverse(ajax_route, kwargs=kwargs)

            mem_data['url'] = command_chain_url
            context['command_chain'].append(mem_data)

            # Next, get some info about subordinates
            # Start by getting all child organizations for the member org
            child_compositions = org.child_organization.all()

            if child_compositions:
                child_commanders = get_commanders(membership,
                                                  child_compositions,
                                                  relationship='child')
                if child_commanders:
                    context['subordinates'] += child_commanders

            parent_compositions = org.parent_organization.all()

            if parent_compositions:
                parent_commanders = get_commanders(membership,
                                                   parent_compositions,
                                                   relationship='parent')

                if parent_commanders:
                    context['superiors'] += parent_commanders

        context['subordinates'] = sort_commanders(context['subordinates'])
        context['superiors'] = sort_commanders(context['superiors'])

        context['command_chain'].reverse()
        context['events'] = []
        events = context['person'].violationperpetrator_set.all()
        for event in events:
            context['events'].append(event.object_ref)

        return context


def get_commanders(membership, compositions, relationship='child'):

    assert relationship in ('parent', 'child')

    comms = []

    # Get start and end date for this membership, to determine
    # overlap
    mem_start = membership.firstciteddate.get_value()
    no_start = False
    if mem_start is None:
        # Make a bogus date that everything will be greater than
        mem_start = date(1000, 1, 1)
        no_start = True
    else:
        mem_start = repr(mem_start.value)

    mem_end = membership.lastciteddate.get_value()
    no_end = False
    if mem_end is None:
        mem_end = date.today()
        no_end = True
    else:
        mem_end = repr(mem_end.value)

    for composition in compositions:
        # Start and end date attributes for filtering:
        # We want only the personnel who were commanders of child
        # organizations during this membership
        # (also allowing for null dates)
        child = getattr(composition.object_ref, relationship)
        child = child.get_value()
        child_id = child.value.uuid

        child_commanders_query = '''
            SELECT * FROM membershipperson
            WHERE organization_id='{child_id}'
            AND (first_cited <= '{mem_end}' or first_cited is Null)
            AND (last_cited >= '{mem_start}' or last_cited is Null)
        '''.format(child_id=child_id,
                    mem_end=mem_end,
                    mem_start=mem_start)

        cursor = connection.cursor()
        cursor.execute(child_commanders_query)

        columns = [c[0] for c in cursor.description]
        results_tuple = namedtuple('Commander', columns)

        commanders = [results_tuple(*r) for r in cursor]

        for commander_tuple in commanders:
            # We need to calculate time overlap, so use a dict to
            # stash information about this commander
            commander = MembershipPersonMember.objects.get(object_ref__id=commander_tuple.id)
            info = {}
            info['commander'] = commander.object_ref
            info['organization'] = child

            # Get start of the overlap between these two people,
            # being sensitive to nulls

            # First, try to get the commander of the child unit's
            # start/end dates
            c_start = commander.object_ref.firstciteddate.get_value()
            c_end = commander.object_ref.lastciteddate.get_value()

            if c_start and not no_end:
                overlap_start = c_start
            else:
                # Once we have "ongoing" attributes, we'll be able to
                # determine ongoing overlap; for now, mark it as "unknown"
                overlap_start = _('Unknown')

            if c_end and not no_start:
                overlap_end = c_end
            else:
                # Ditto about "ongoing" attributes above
                overlap_end = _('Unknown')

            if overlap_start != _('Unknown') and overlap_end != _('Unknown'):

                # Convert to date objects to calculate delta
                start_year = overlap_start.value.year
                start_month = overlap_start.value.month
                start_day = overlap_start.value.day

                end_year = overlap_end.value.year
                end_month = overlap_end.value.month
                end_day = overlap_end.value.day

                # Account for fuzzy dates
                all_dates = [start_year, start_month, start_day,
                                end_year, end_month, end_day]

                fuzzy_date =  any(dt == 0 for dt in all_dates)

                if fuzzy_date:
                    # Start the overlap string with a "roughly" symbol
                    overlap_duration = '~'

                    # Find spots where the dates are fuzzy
                    if start_month == 0:
                        start_month = 1
                    if start_day == 0:
                        start_day = 1
                    if end_month == 0:
                        end_month = 1
                    if end_day == 0:
                        end_day = 1
                else:
                    overlap_duration = ''

                start = date(start_year,
                                start_month,
                                start_day)

                end = date(end_year,
                            end_month,
                            end_day)

                overlap_duration += (str((end - start).days) + ' ' + _('days'))
            else:
                overlap_duration = _('Unknown')

            info['overlap_start'] = overlap_start
            info['overlap_end'] = overlap_end
            info['overlap_duration'] = overlap_duration

            comms.append(info)

    return comms


def sort_commanders(commanders):

    if commanders:
        return sorted(commanders,
                    key=lambda m: (m['overlap_end'].value if m['overlap_end'] != _('Unknown')
                                    else date(1, 1, 1)),
                    reverse=True)
    else:
        return commanders


class PersonList(PaginatedList):
    model = Person
    template_name = 'person/list.html'
    orderby_lookup = {
        'name': 'personname__value',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Highlight the correct nav tab in the template
        context['person_tab'] = 'selected-tab'
        context['search_term'] = 'a person'
        return context

class PersonCreate(LoginRequiredMixin, BaseFormSetView):
    template_name = 'person/create.html'
    form_class = PersonForm
    success_url = reverse_lazy('create-membership')
    extra = 1
    max_num = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['confidence_levels'] = settings.CONFIDENCE_LEVELS

        context['organizations'] = self.request.session.get('organizations')
        context['source'] = Source.objects.get(id=self.request.session['source_id'])

        if context['organizations']:
            if len(context['organizations']) > 1:
                back_url = reverse_lazy('create-organization-membership')
            else:
                back_url = reverse_lazy('create-organization')
        else:
            back_url = reverse_lazy('create-organization')

        context['back_url'] = back_url
        context['skip_url'] = reverse_lazy('create-geography')

        existing_forms = self.request.session.get('forms', {})

        if existing_forms and existing_forms.get('people') and not getattr(self, 'formset', False):

            form_data = existing_forms.get('people')
            self.initFormset(form_data)

            context['formset'] = self.get_formset_context(self.formset)
            context['browsing'] = True

        return context

    def get_formset_context(self, formset):

        for index, form in enumerate(formset.forms):

            alias_ids = form.data.get('form-{}-alias'.format(index))
            org_ids = form.data.get('form-{}-orgs'.format(index))

            form.aliases = []
            form.organizations = []

            if alias_ids:

                for alias_id in alias_ids:
                    try:
                        alias_id = int(alias_id)
                        alias = Alias.objects.get(id=alias_id)
                    except ValueError:
                        alias = {'id': alias_id, 'value': alias_id}
                    form.aliases.append(alias)

            if org_ids:

                for org_id in org_ids:
                    org_id = int(org_id)
                    org = Organization.objects.get(id=org_id)
                    form.organizations.append(org)

        return formset

    def post(self, request, *args, **kwargs):

        form_data = {}

        for key, value in request.POST.items():
            if ('alias' in key or 'orgs' in key) and 'confidence' not in key:
                form_data[key] = request.POST.getlist(key)
            else:
                form_data[key] = request.POST.get(key)

        self.initFormset(form_data)

        return self.validateFormSet()

    def formset_invalid(self, formset):

        formset = self.get_formset_context(formset)

        response = super().formset_invalid(formset)
        return response

    def formset_valid(self, formset):
        num_forms = int(formset.data['form-TOTAL_FORMS'][0])

        self.people = []
        self.memberships = []

        self.source = Source.objects.get(id=self.request.session['source_id'])

        for i in range(0,num_forms):
            first = True

            form_prefix = 'form-{0}-'.format(i)

            name_id_key = 'form-{0}-name'.format(i)
            name_text_key = 'form-{0}-name_text'.format(i)
            division_id_key = 'form-{}-division_id'.format(i)

            name_id = formset.data[name_id_key]
            name_text = formset.data[name_text_key]
            division_id = formset.data[division_id_key]

            name_confidence = int(formset.data.get(form_prefix +
                                                   'name_confidence', 1))
            division_confidence = int(formset.data.get(form_prefix +
                                                       'division_confidence', 1))

            person_info = {
                'Person_PersonName': {
                    'value': name_text,
                    'confidence': name_confidence,
                    'sources': [self.source],
                },
                'Person_PersonDivisionId': {
                    'value': division_id,
                    'confidence': division_confidence,
                    'sources': [self.source],
                }
            }

            if name_id == 'None':
                return self.formset_invalid(formset)

            elif name_id == '-1':
                person = Person.create(person_info)
                formset.data[name_id_key] = person.id

            else:
                person = Person.objects.get(id=name_id)
                person_info['Person_PersonName']['sources'] = self.sourcesList(person, 'name')
                person.update(person_info)

            alias_id_key = 'form-{0}-alias'.format(i)
            alias_text_key = 'form-{0}-alias_text'.format(i)
            alias_confidence = int(formset.data.get(form_prefix +
                                                    'alias_confidence', 1))

            aliases = formset.data.get(alias_text_key)

            if aliases:

                for alias in aliases:

                    alias_obj, created = Alias.objects.get_or_create(value=alias)

                    pa_obj, created = PersonAlias.objects.get_or_create(object_ref=person,
                                                                        value=alias_obj,
                                                                        lang=get_language(),
                                                                        confidence=alias_confidence)

                    pa_obj.sources.add(self.source)
                    pa_obj.save()

            self.people.append(person)

            orgs_key = 'form-{0}-orgs'.format(i)
            orgs = formset.data.get(orgs_key)
            orgs_confidence = int(formset.data.get(form_prefix +
                                                   'orgs_confidence', 1))

            for org in orgs:

                organization = Organization.objects.get(id=org)

                mem_data = {
                    'MembershipPerson_MembershipPersonMember': {
                        'value': person,
                        'confidence': orgs_confidence,
                        'sources': [self.source],
                    },
                    'MembershipPerson_MembershipPersonOrganization': {
                        'value': Organization.objects.get(id=org),
                        'confidence': orgs_confidence,
                        'sources': [self.source],
                    }
                }

                membership, created = MembershipPerson.objects.get_or_create(membershippersonmember__value=person,
                                                                             membershippersonorganization__value=organization)

                # We only care about updating new memberships, since we show
                # the user old memberships that weren't necessarily part of this
                # source
                if created:

                    membership.update(mem_data)

                    self.memberships.append({
                        'person': str(person.name),
                        'organization': str(organization.name),
                        'membership': membership.id,
                        'first': first
                    })

                first = False

            # Queue up to be added to search index
            to_index = self.request.session.get('index')

            if not to_index:
                self.request.session['index'] = {}

            self.request.session['index'][str(person.uuid)] = 'people'

        self.request.session['people'] = [{'id': p.id, 'name': p.name.get_value().value} \
                                                     for p in self.people]
        self.request.session['memberships'] = self.memberships

        response = super().formset_valid(formset)

        if not self.request.session.get('forms'):
            self.request.session['forms'] = {}

        self.request.session['forms']['people'] = formset.data
        self.request.session.modified = True

        return response

def person_autocomplete(request):
    term = request.GET.get('q')
    people = Person.objects.filter(personname__value__icontains=term).all()

    complex_attrs = ['division_id']

    list_attrs = ['aliases', 'classification']

    set_attrs = {'membershippersonmember_set': 'organization'}

    autofill = Autofill(objects=people,
                        set_attrs=set_attrs,
                        complex_attrs=complex_attrs,
                        list_attrs=list_attrs)

    attrs = autofill.attrs

    return HttpResponse(json.dumps(attrs), content_type='application/json')

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

class PersonUpdate(LoginRequiredMixin, BaseUpdateView):
    template_name = 'person/edit.html'
    form_class = PersonForm
    success_url = reverse_lazy('dashboard')
    sourced = True

    def post(self, request, *args, **kwargs):

        self.checkSource(request)
        
        self.aliases = request.POST.getlist('alias')

        return self.validateForm()
    
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
                'sources': self.sourcesList(person, 'division_id')
            }
        }
        
        person.update(person_info)

        if self.aliases:
            for alias in self.aliases:
                
                alias_obj, created = Alias.objects.get_or_create(value=alias)

                pa_obj, created = PersonAlias.objects.get_or_create(object_ref=person,
                                                                    value=alias_obj,
                                                                    lang=get_language())
                
                pa_obj.sources.add(self.source)
                pa_obj.save()
        
        messages.add_message(self.request, 
                             messages.INFO, 
                             'Person {} saved!'.format(form.cleaned_data['name_text']))

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

class PersonDelete(LoginRequiredMixin, DeleteView):
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


