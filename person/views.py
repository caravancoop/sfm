import json
import csv
import sys

from datetime import date
from collections import namedtuple

from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.admin.utils import NestedObjects
from django.contrib import messages
from django.views.generic.edit import DeleteView, FormView, CreateView, UpdateView
from django.views.generic import TemplateView, DetailView, RedirectView
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db import DEFAULT_DB_ALIAS
from django.db.models import Q
from django.db import connection
from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from django.contrib.auth.mixins import LoginRequiredMixin

from complex_fields.models import ComplexFieldContainer

from extra_views import FormSetView

from api.base_views import JSONResponseMixin

from person.models import Person, PersonName, PersonAlias, Alias
from person.forms import PersonForm
from organization.models import Organization
from source.models import Source
from membershipperson.models import MembershipPerson, MembershipPersonMember, Role
from sfm_pc.utils import (deleted_in_str, get_org_hierarchy_by_id,
                          get_command_edges, get_command_nodes, Autofill)
from sfm_pc.base_views import BaseFormSetView, BaseUpdateView, PaginatedList, NeverCacheMixin


class PersonDetail(DetailView):
    model = Person
    template_name = 'person/view.html'
    slug_field = 'uuid'

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
                # Make the query using the raw date string, to accomodate
                # fuzzy dates
                when = repr(membership.lastciteddate.get_value().value)
                mem_data['when'] = when

                # Display a formatted date
                mem_data['display_date'] = str(membership.lastciteddate.get_value())

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

        context['versions'] = context['person'].getVersions()

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
            SELECT DISTINCT(id) FROM membershipperson
            WHERE organization_id='{child_id}'
            AND (first_cited < '{mem_end}' or first_cited is Null)
            AND (last_cited > '{mem_start}' or last_cited is Null)
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

            if c_start and not no_start:
                overlap_start = c_start
            else:
                # Once we have "ongoing" attributes, we'll be able to
                # determine ongoing overlap; for now, mark it as "unknown"
                overlap_start = _('Unknown')

            if c_end and not no_end:
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


class PersonEditView(UpdateView, NeverCacheMixin, LoginRequiredMixin):
    template_name = 'person/edit.html'
    model = Person
    slug_field = 'uuid'
    form_class = PersonForm

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['request'] = self.request
        return form_kwargs

    def get_success_url(self):
        return reverse('view-person', kwargs=self.kwargs)


class PersonCreateView(PersonEditView, CreateView):
    pass
