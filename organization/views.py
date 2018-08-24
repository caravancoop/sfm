import json

from django.contrib import messages
from django.views.generic import DetailView
from django.http import HttpResponse
from django.db import connection
from django.utils.translation import get_language
from django.core.urlresolvers import reverse_lazy, reverse
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from source.models import Source

from geosite.models import Geosite

from emplacement.models import Emplacement

from area.models import Area

from association.models import Association

from composition.models import Composition

from organization.forms import OrganizationBasicsForm, \
    OrganizationRelationshipsForm
from organization.models import Organization, OrganizationAlias, \
    OrganizationClassification

from sfm_pc.utils import (get_osm_by_id, get_hierarchy_by_id,
                          get_org_hierarchy_by_id,  get_command_edges,
                          get_command_nodes, Autofill)
from sfm_pc.templatetags.countries import country_name
from sfm_pc.base_views import BaseFormSetView, BaseUpdateView, PaginatedList, \
    BaseEditView


class OrganizationDetail(DetailView):
    model = Organization
    template_name = 'organization/view.html'
    slug_field = 'uuid'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Generate link to download a CSV of this record
        params = '?download_etype=Organization&entity_id={0}'.format(str(context['organization'].uuid))

        context['download_url'] = reverse('download') + params

        # Commanders of this unit
        context['person_members'] = []
        person_members = context['organization'].membershippersonorganization_set.all()
        for membership in person_members:
            context['person_members'].append(membership.object_ref)

        # Organizational members of this unit
        context['org_members'] = []
        org_members = context['organization'].membershiporganizationorganization_set.all()
        if org_members:
            org_members = (mem.object_ref for mem in org_members)
            context['org_members'] = org_members

        # Other units that this unit is a member of
        context['memberships'] = []
        memberships = context['organization'].membershiporganizationmember_set.all()
        if memberships:
            memberships = (mem.object_ref for mem in memberships)
            context['memberships'] = memberships

        # Child units
        context['subsidiaries'] = []
        children = context['organization'].child_organization.all()
        for child in children:
            context['subsidiaries'].append(child.object_ref)

        # Incidents that this unit perpetrated
        context['events'] = []
        events = context['organization'].violationperpetratororganization_set.all()
        for event in events:
            context['events'].append(event.object_ref)

        context['sites'] = []
        emplacements = tuple(context['organization'].emplacements)
        context['emplacements'] = (em.object_ref for em in emplacements)
        for emplacement in emplacements:
            if emplacement.object_ref.site.get_value().value.admin_id.get_value():
                context['sites'].append(emplacement.object_ref.site.get_value().value)

        context['areas'] = []
        associations = tuple(context['organization'].associations)
        context['associations'] = (ass.object_ref for ass in associations)
        for association in associations:
            if association.object_ref.area.get_value().value.osmid.get_value():
                geom = association.object_ref.area.get_value().value.geometry
                area = geom.get_value().value.simplify(tolerance=0.01)
                area_obj = {
                    'geom': area,
                    'name': association.object_ref.area.get_value().value.osmname.get_value()
                }
                context['areas'].append(area_obj)

        context['parents'] = []
        context['parents_list'] = []
        parents = context['organization'].parent_organization.all()
        # "parent" is a CompositionChild
        for parent in parents:

            context['parents'].append(parent.object_ref.parent.get_value().value)

            org_data = {'when': '', 'url': ''}

            when = None
            if parent.object_ref.enddate.get_value():
                # Make the query using the raw date string, to accomodate
                # fuzzy dates
                when = repr(parent.object_ref.enddate.get_value().value)
                org_data['when'] = when

                # Display a formatted date
                org_data['display_date'] = str(parent.object_ref.enddate.get_value())

            kwargs = {'org_id': str(context['organization'].uuid)}
            ajax_route = 'command-chain'
            if when:
                kwargs['when'] = when
                ajax_route = 'command-chain-bounded'

            command_chain_url = reverse(ajax_route, kwargs=kwargs)

            org_data['url'] = command_chain_url

            context['parents_list'].append(org_data)

        context['versions'] = context['organization'].getVersions()

        return context


class OrganizationEditView(BaseEditView):
    model = Organization
    slug_field = 'uuid'
    slug_field_kwarg = 'slug'
    context_object_name = 'organization'

    def get_success_url(self):
        uuid = self.kwargs[self.slug_field_kwarg]
        return reverse('view-organization', kwargs={'slug': uuid})


class OrganizationEditBasicsView(OrganizationEditView):
    template_name = 'organization/edit-basics.html'
    form_class = OrganizationBasicsForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        first_composition = context['organization'].child_organization.first()

        if not first_composition:
            first_composition.parent_organization.first()

        context['first_composition'] = first_composition

        return context

class OrganizationEditRelationshipsView(OrganizationEditView):
    template_name = 'organization/edit-relationships.html'
    form_class = OrganizationRelationshipsForm
    model = Composition
    context_object_name = 'current_composition'
    slug_field_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        organization = Organization.objects.get(uuid=self.kwargs['organization_id'])
        context['organization'] = organization
        context['compositions'] = Composition.objects.filter(Q(compositionparent__value=organization) | Q(compositionchild__value=organization))

        first_composition = context['current_composition'].child.get_value()

        if not first_composition:
            first_composition = context['current_composition'].parent.get_value()

        context['first_composition'] = first_composition

        return context

    def get_success_url(self):
        return reverse_lazy('view-organization',
                            kwargs={'slug': self.kwargs['organization_id']})


def organization_autocomplete(request):
    term = request.GET.get('q')

    response = {
        'results': []
    }

    if term:
        organizations = Organization.objects.filter(organizationname__value__icontains=term)[:10]

        for organization in organizations:
            result = {
                'id': organization.id,
                'text': organization.name.get_value().value,
                'aliases': organization.alias_list,
                'country': None,
            }

            if organization.division_id.get_value():
                result['country'] = country_name(organization.division_id.get_value().value)

            response['results'].append(result)

    return HttpResponse(json.dumps(response), content_type='application/json')


################################################################
## The views below here are probably ready to be factored out ##
################################################################


def classification_autocomplete(request):
    term = request.GET.get('q')

    classifications = '''
        SELECT DISTINCT TRIM(value) AS value
    '''

    classifications = Classification.objects.filter(value__icontains=term).all()

    results = []
    for classification in classifications:
        results.append({
            'text': classification.value,
            'id': classification.id,
        })

    return HttpResponse(json.dumps(results), content_type='application/json')


def alias_autocomplete(request):
    term = request.GET.get('q')
    alias_query = OrganizationAlias.objects.filter(value__value__icontains=term)
    results = []
    for alias in alias_query:
        results.append({
            'text': alias.value.value,
            'id': alias.id
        })
    return HttpResponse(json.dumps(results), content_type='application/json')
