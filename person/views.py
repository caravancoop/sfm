import json
from datetime import date
from collections import namedtuple
from itertools import chain

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse, reverse_lazy
from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import gettext as _

from person.models import Person
from person.forms import PersonBasicsForm, PersonCreateBasicsForm, \
    PersonPostingsForm, PersonCreatePostingForm
from membershipperson.models import MembershipPersonMember, MembershipPerson
from sfm_pc.base_views import BaseUpdateView, BaseCreateView, BaseDetailView, \
    BaseDeleteView, BaseDeleteRelationshipView
from source.models import Source


class PersonDetail(BaseDetailView):
    model = Person
    template_name = 'person/view.html'
    slug_field = 'uuid'

    def get_sources(self, context):
        sources = set()

        sources.update(list(context['person'].sources.values_list('uuid', flat=True)))

        for membership in context['memberships']:
            sources.update(
                list(membership.sources.values_list('uuid', flat=True))
            )

        for entity in chain(context['subordinates'], context['superiors']):
            sources.update(
                list(entity['commander'].sources.values_list('uuid', flat=True))
            )

        return Source.objects.filter(uuid__in=sources).order_by('source_url', '-accesspoint__accessed_on')\
                                                      .distinct('source_url')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        authenticated = self.request.user.is_authenticated

        if authenticated:
            affiliations = context['person'].memberships
        else:
            affiliations = context['person'].memberships.filter(object_ref__membershippersonorganization__value__published=True)

        memberships = tuple(mem.object_ref for mem in affiliations)

        # A person can have more than one membership in a particular
        # organization. Generate a unique list of organizations to which this
        # person belongs, in order to determine superiors and subordinates.
        member_organizations = MembershipPerson.objects.filter(
            id__in=context['person'].memberships.values_list('object_ref')
        ).distinct('membershippersonorganization__value')

        context['memberships'] = memberships
        context['subordinates'] = []
        context['superiors'] = []
        context['command_chain'] = []

        for membership in member_organizations:

            # Grab the org object
            org = membership.organization.get_value().value
            org_id = str(org.uuid)

            # Grab the other attributes of the membership so we're not
            # duplicating queries

            lastciteddate = membership.lastciteddate.get_value()
            firstciteddate = membership.firstciteddate.get_value()

            # Get info about chain of command
            mem_data = {}

            when = None
            if lastciteddate:
                # Make the query using the raw date string, to accomodate
                # fuzzy dates
                when = repr(lastciteddate.value)
                mem_data['when'] = when

                # Display a formatted date
                mem_data['display_date'] = str(lastciteddate)

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

            if authenticated:
                child_compositions = org.child_organization.all()
            else:
                child_compositions = org.child_organization.filter(value__published=True)

            if child_compositions:
                child_commanders = get_commanders(firstciteddate,
                                                  lastciteddate,
                                                  child_compositions,
                                                  person_id=context['person'].uuid,
                                                  relationship='child')
                if child_commanders:
                    context['subordinates'] += child_commanders

            if authenticated:
                parent_compositions = org.parent_organization.all()
            else:
                parent_compositions = org.parent_organization.filter(value__published=True)

            if parent_compositions:
                parent_commanders = get_commanders(firstciteddate,
                                                   lastciteddate,
                                                   parent_compositions,
                                                   person_id=context['person'].uuid,
                                                   relationship='parent')

                if parent_commanders:
                    context['superiors'] += parent_commanders

        context['subordinates'] = list(sort_commanders(context['subordinates']))
        context['superiors'] = list(sort_commanders(context['superiors']))

        context['command_chain'].reverse()
        context['events'] = []

        if authenticated:
            events = context['person'].violationperpetrator_set.all()
        else:
            events = context['person'].violationperpetrator_set.filter(value__published=True)

        for event in events:
            context['events'].append(event.object_ref)

        context['sources'] = list(self.get_sources(context))

        return context


def get_commanders(mem_start, mem_end, compositions, person_id=None, relationship='child'):

    assert relationship in ('parent', 'child')

    comms = []

    # Get start and end date for this membership, to determine
    # overlap
    no_start = False
    if mem_start is None:
        # Make a bogus date that everything will be greater than
        mem_start = date(1000, 1, 1)
        no_start = True
    else:
        mem_start = repr(mem_start.value)

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
            SELECT
                -- Consider two memberships identical if only title is different
                DISTINCT ON (
                    person.id, organization.id, rank.value_id, role.value_id,
                    first_cited.value, last_cited.value
                )
                membership.id
            FROM membershipperson_membershipperson AS membership
            JOIN membershipperson_membershippersonmember AS member
              ON membership.id = member.object_ref_id
            JOIN person_person AS person
              ON member.value_id = person.id
            JOIN membershipperson_membershippersonorganization AS member_org
              ON membership.id = member_org.object_ref_id
            JOIN organization_organization AS organization
              ON member_org.value_id = organization.id
            JOIN membershipperson_membershippersonrank AS rank
              ON membership.id = rank.object_ref_id
            JOIN membershipperson_membershippersonrole AS Role
              ON membership.id = role.object_ref_id
            JOIN membershipperson_membershippersonfirstciteddate AS first_cited
              ON membership.id = first_cited.object_ref_id
            JOIN membershipperson_membershippersonlastciteddate AS last_cited
              ON membership.id = last_cited.object_ref_id
            WHERE organization.uuid='{child_id}'
            AND (first_cited.value < '{mem_end}' or first_cited is NULL)
            AND (last_cited.value > '{mem_start}' or last_cited is NULL)
            AND person.uuid != '{person_id}'
            ORDER BY person.id, organization.id, rank.value_id, role.value_id, first_cited.value, last_cited.value
        '''.format(child_id=child_id,
                   mem_end=mem_end,
                   mem_start=mem_start,
                   person_id=person_id)

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

                fuzzy_date = any(dt == 0 for dt in all_dates)

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

    results = {
        'results': []
    }

    for person in people:
        results['results'].append({
            'id': person.id,
            'text': person.name.get_value().value
        })

    return HttpResponse(json.dumps(results), content_type='application/json')


class PersonEditView(BaseUpdateView):
    model = Person
    slug_field = 'uuid'
    slug_field_kwarg = 'slug'
    context_object_name = 'person'

    def get_success_url(self):
        person_id = self.kwargs[self.slug_field_kwarg]
        return reverse('view-person', kwargs={'slug': person_id})


class PersonDeleteView(BaseDeleteView):
    model = Person
    slug_field = 'uuid'
    slug_field_kwarg = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'person/delete.html'
    context_object_name = 'person'

    def get_cancel_url(self):
        return reverse_lazy('edit-person', args=[self.kwargs['slug']])

    def get_success_url(self):
        return reverse('search') + '?entity_type=Person'

    def get_related_entities(self):
        return self.object.related_entities


class PersonEditBasicsView(PersonEditView):
    template_name = 'person/edit-basics.html'
    form_class = PersonBasicsForm

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['person_id'] = self.kwargs['slug']
        return form_kwargs

    def get_success_url(self):
        person_id = self.kwargs[self.slug_field_kwarg]

        if self.request.POST.get('_continue'):
            return reverse('edit-person', kwargs={'slug': person_id})
        else:
            return super().get_success_url()


class PersonEditPostingsView(PersonEditView):
    model = MembershipPerson
    template_name = 'person/edit-postings.html'
    form_class = PersonPostingsForm
    context_object_name = 'current_membership'
    slug_field_kwarg = 'person_id'

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['person_id'] = self.kwargs['person_id']
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['person'] = Person.objects.get(uuid=self.kwargs['person_id'])

        affiliations = context['person'].memberships
        memberships = tuple(mem.object_ref for mem in affiliations)

        context['memberships'] = memberships

        return context

    def get_success_url(self):
        person_id = self.kwargs[self.slug_field_kwarg]

        if self.request.POST.get('_continue'):
            return reverse('edit-person-postings', kwargs={'person_id': person_id,
                                                           'pk': self.kwargs['pk']})
        else:
            return super().get_success_url()


class PersonCreateView(BaseCreateView):
    template_name = 'person/create-basics.html'
    form_class = PersonCreateBasicsForm
    context_object_name = 'person'
    slug_field_kwarg = 'slug'
    model = Person

    def form_valid(self, form):
        form.save(commit=True)
        return HttpResponseRedirect(reverse('view-person',
                                    kwargs={'slug': form.object_ref.uuid}))

    def get_success_url(self):
        # This method doesn't ever really get called but since Django does not
        # seem to recognize when we place a get_absolute_url method on the model
        # and some way of determining where to redirect after the form is saved
        # is required, here ya go. The redirect actually gets handled in the
        # form_valid method above.
        return '{}?entity_type=Person'.format(reverse_lazy('search'))


class PersonCreatePostingView(BaseCreateView):
    model = MembershipPerson
    template_name = 'person/create-posting.html'
    form_class = PersonCreatePostingForm
    context_object_name = 'current_membership'
    slug_field_kwarg = 'person_id'

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['person_id'] = self.kwargs['person_id']
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['person'] = Person.objects.get(uuid=self.kwargs['person_id'])

        affiliations = context['person'].memberships
        memberships = tuple(mem.object_ref for mem in affiliations)

        context['memberships'] = memberships

        return context

    def get_success_url(self):

        return reverse_lazy('view-person', kwargs={'slug': self.kwargs['person_id']})


class PersonDeletePostingView(BaseDeleteRelationshipView):
    model = MembershipPerson
    template_name = 'person/delete-posting.html'

    def get_cancel_url(self):
        return reverse_lazy(
            'edit-person-postings',
            kwargs={
                'person_id': self.kwargs['person_id'],
                'pk': self.kwargs['pk']
            }
        )

    def get_objects_to_update(self):
        membership = self.get_object()
        person = membership.member.get_value().value
        organization = membership.organization.get_value().value
        return person, organization

    def get_success_url(self):
        return reverse_lazy('view-person', kwargs={'slug': self.kwargs['person_id']})

    def delete(self, request, *args, **kwargs):
        person, organization = self.get_objects_to_update()

        response = super().delete(request, *args, **kwargs)

        person.object_ref_saved()
        organization.object_ref_saved()

        return response


class PersonSitemap(Sitemap):

    protocol = 'http' if settings.DEBUG else 'https'

    def items(self):
        return Person.objects.filter(published=True).order_by('id')

    def location(self, obj):
        return reverse('view-person', args=[obj.uuid])
