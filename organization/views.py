import json

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin

from emplacement.models import Emplacement

from association.models import Association

from composition.models import Composition

from organization.forms import OrganizationBasicsForm, \
    OrganizationCompositionForm, OrganizationPersonnelForm, \
    OrganizationEmplacementForm, OrganizationAssociationForm, \
    OrganizationCreateBasicsForm, OrganizationCreateCompositionForm, \
    OrganizationCreatePersonnelForm, OrganizationCreateEmplacementForm, \
    OrganizationCreateAssociationForm, OrganizationMembershipForm, \
    OrganizationCreateMembershipForm
from organization.models import Organization

from membershipperson.models import MembershipPerson

from membershiporganization.models import MembershipOrganization

from sfm_pc.templatetags.countries import country_name
from sfm_pc.base_views import BaseUpdateView, BaseCreateView, BaseDetailView, \
    BaseDeleteRelationshipView


class EditButtonsMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_{}_active'.format(self.button)] = True
        return context


class OrganizationDetail(BaseDetailView):
    model = Organization
    template_name = 'organization/view.html'
    slug_field = 'uuid'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Determine if the user is logged in
        authenticated = self.request.user.is_authenticated()

        # Generate link to download a CSV of this record
        params = '?download_etype=Organization&entity_id={0}'.format(str(context['organization'].uuid))

        context['download_url'] = reverse('download') + params

        # Commanders of this unit
        context['person_members'] = []

        if authenticated:
            person_members = context['organization'].membershippersonorganization_set.all()
        else:
            person_members = context['organization'].membershippersonorganization_set.filter(object_ref__membershippersonmember__value__published=True)

        for membership in person_members:
            context['person_members'].append(membership.object_ref)

        # Organizational members of this unit
        context['org_members'] = []

        if authenticated:
            org_members = context['organization'].membershiporganizationorganization_set.all()
        else:
            org_members = context['organization'].membershiporganizationorganization_set.filter(value__published=True)

        if org_members:
            org_members = (mem.object_ref for mem in org_members)
            context['org_members'] = org_members

        # Other units that this unit is a member of
        context['memberships'] = []

        if authenticated:
            memberships = context['organization'].membershiporganizationmember_set.all()
        else:
            memberships = context['organization'].membershiporganizationmember_set.filter(object_ref__membershiporganizationorganization__value__published=True)

        if memberships:
            memberships = (mem.object_ref for mem in memberships)
            context['memberships'] = memberships

        # Child units
        context['subsidiaries'] = []

        if authenticated:
            children = context['organization'].child_organization.all()
        else:
            children = context['organization'].child_organization.filter(object_ref__compositionchild__value__published=True)

        for child in children:
            context['subsidiaries'].append(child.object_ref)

        # Incidents that this unit perpetrated
        context['events'] = []

        if authenticated:
            events = context['organization'].violationperpetratororganization_set.all()
        else:
            events = context['organization'].violationperpetratororganization_set.filter(object_ref__published=True)

        for event in events:
            context['events'].append(event.object_ref)

        context['sites'] = []
        emplacements = tuple(context['organization'].emplacements)
        context['emplacements'] = (em.object_ref for em in emplacements)
        for emplacement in emplacements:
            context['sites'].append(emplacement.object_ref.site.get_value().value)

        context['areas'] = []
        associations = tuple(context['organization'].associations)
        context['associations'] = (ass.object_ref for ass in associations)
        for association in associations:
            geom = association.object_ref.area.get_value().value.geometry
            area_obj = {
                'geom': geom,
                'name': association.object_ref.area.get_value().value.name
            }
            context['areas'].append(area_obj)

        context['parents'] = []
        context['parents_list'] = []

        if authenticated:
            parents = context['organization'].parent_organization.all()
        else:
            parents = context['organization'].parent_organization.filter(object_ref__compositionparent__value__published=True)

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

        return context


class OrganizationEditView(EditButtonsMixin, BaseUpdateView):
    model = Organization
    slug_field = 'uuid'
    slug_field_kwarg = 'slug'
    context_object_name = 'organization'
    button = 'basics'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['organization'] = self.get_reference_organization()

        return context

    def get_success_url(self):
        uuid = self.kwargs[self.slug_field_kwarg]
        return reverse('view-organization', kwargs={'slug': uuid})


class OrganizationEditBasicsView(OrganizationEditView):
    template_name = 'organization/edit-basics.html'
    form_class = OrganizationBasicsForm
    button = 'basics'

    def get_reference_organization(self):
        return Organization.objects.get(uuid=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        organization_id = self.kwargs[self.slug_field_kwarg]

        if self.request.POST.get('_continue'):
            return reverse('edit-organization', kwargs={'slug': organization_id})
        else:
            return super().get_success_url()

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['organization_id'] = self.kwargs['slug']
        return form_kwargs


class OrganizationCreateBasicsView(BaseCreateView):
    model = Organization
    slug_field = 'uuid'
    slug_field_kwarg = 'slug'
    context_object_name = 'organization'
    template_name = 'organization/create-basics.html'
    form_class = OrganizationCreateBasicsForm

    def form_valid(self, form):
        form.save(commit=True)
        return HttpResponseRedirect(reverse('view-organization',
                                    kwargs={'slug': form.object_ref.uuid}))

    def get_success_url(self):
        # This method doesn't ever really get called but since Django does not
        # seem to recognize when we place a get_absolute_url method on the model
        # and some way of determining where to redirect after the form is saved
        # is required, here ya go. The redirect actually gets handled in the
        # form_valid method above.
        return '{}?entity_type=Organization'.format(reverse('search'))


class OrganizationEditCompositionView(OrganizationEditView):
    template_name = 'organization/edit-composition.html'
    form_class = OrganizationCompositionForm
    model = Composition
    context_object_name = 'current_composition'
    slug_field_kwarg = 'pk'
    button = 'relationships'

    def get_reference_organization(self):
        return Organization.objects.get(uuid=self.kwargs['organization_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        parents = Q(compositionparent__value=context['organization'])
        children = Q(compositionchild__value=context['organization'])

        context['compositions'] = Composition.objects.filter(parents | children)
        context['memberships'] = MembershipOrganization.objects.filter(membershiporganizationmember__value=context['organization'])

        return context

    def get_success_url(self):
        organization_id = self.kwargs['organization_id']
        pk = self.kwargs['pk']

        if self.request.POST.get('_continue'):
            return reverse('edit-organization-composition',
                           kwargs={'organization_id': organization_id,
                                   'pk': pk})
        else:
            return reverse('view-organization', kwargs={'slug': organization_id})


class OrganizationCreateCompositionView(EditButtonsMixin, BaseCreateView):
    template_name = 'organization/create-composition.html'
    form_class = OrganizationCreateCompositionForm
    model = Composition
    context_object_name = 'current_composition'
    slug_field_kwarg = 'pk'
    button = 'relationships'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization'] = Organization.objects.get(uuid=self.kwargs['organization_id'])

        parents = Q(compositionparent__value=context['organization'])
        children = Q(compositionchild__value=context['organization'])

        context['compositions'] = Composition.objects.filter(parents | children)
        context['memberships'] = MembershipOrganization.objects.filter(membershiporganizationmember__value=context['organization'])

        return context

    def get_success_url(self):
        return reverse('edit-organization', kwargs={'slug': self.kwargs['organization_id']})


class OrganizationDeleteCompositionView(LoginRequiredMixin, BaseDeleteRelationshipView):
    model = Composition
    template_name = 'organization/delete-composition.html'

    def get_cancel_link(self):
        return reverse_lazy(
            'edit-organization-composition',
            kwargs={
                'organization_id': self.kwargs['organization_id'],
                'pk': self.kwargs['pk']
            }
        )

    def get_objects_to_update(self):
        composition = self.get_object()
        parent = composition.parent.get_value().value
        child = composition.child.get_value().value
        return parent, child

    def get_success_url(self):
        return reverse('view-organization', kwargs={'slug': self.kwargs['organization_id']})

    def delete(self, request, *args, **kwargs):
        parent, child = self.get_objects_to_update()

        response = super().delete(request, *args, **kwargs)

        parent.object_ref_saved()
        child.object_ref_saved()

        return response


class OrganizationEditMembershipView(EditButtonsMixin, BaseUpdateView):
    template_name = 'organization/edit-membership.html'
    form_class = OrganizationMembershipForm
    model = MembershipOrganization
    context_object_name = 'current_membership'
    slug_field_kwarg = 'pk'
    button = 'relationships'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization'] = Organization.objects.get(uuid=self.kwargs['organization_id'])

        parents = Q(compositionparent__value=context['organization'])
        children = Q(compositionchild__value=context['organization'])

        context['compositions'] = Composition.objects.filter(parents | children)
        context['memberships'] = MembershipOrganization.objects.filter(membershiporganizationmember__value=context['organization'])

        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['organization_id'] = self.kwargs['organization_id']
        return form_kwargs

    def get_success_url(self):
        organization_id = self.kwargs['organization_id']
        pk = self.kwargs['pk']

        if self.request.POST.get('_continue'):
            return reverse('edit-organization-membership',
                           kwargs={'organization_id': organization_id,
                                   'pk': pk})
        else:
            return reverse('view-organization', kwargs={'slug': organization_id})


class OrganizationCreateMembershipView(EditButtonsMixin, BaseCreateView):
    template_name = 'organization/create-membership.html'
    form_class = OrganizationCreateMembershipForm
    model = MembershipOrganization
    context_object_name = 'current_membership'
    slug_field_kwarg = 'pk'
    button = 'relationships'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization'] = Organization.objects.get(uuid=self.kwargs['organization_id'])

        parents = Q(compositionparent__value=context['organization'])
        children = Q(compositionchild__value=context['organization'])

        context['compositions'] = Composition.objects.filter(parents | children)
        context['memberships'] = MembershipOrganization.objects.filter(membershiporganizationmember__value=context['organization'])

        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['organization_id'] = self.kwargs['organization_id']
        return form_kwargs

    def get_success_url(self):
        return reverse('edit-organization', kwargs={'slug': self.kwargs['organization_id']})


class OrganizationDeleteMembershipView(LoginRequiredMixin, BaseDeleteRelationshipView):
    model = MembershipOrganization
    template_name = 'organization/delete-membership.html'

    def get_cancel_link(self):
        return reverse_lazy(
            'edit-organization-membership',
            kwargs={
                'organization_id': self.kwargs['organization_id'],
                'pk': self.kwargs['pk']
            }
        )

    def get_objects_to_update(self):
        membership = self.get_object()
        member = membership.member.get_value().value
        organization = membership.organization.get_value().value
        return member, organization

    def get_success_url(self):
        return reverse('view-organization', kwargs={'slug': self.kwargs['organization_id']})

    def delete(self, request, *args, **kwargs):
        member, organization = self.get_objects_to_update()

        response = super().delete(request, *args, **kwargs)

        member.object_ref_saved()
        organization.object_ref_saved()

        return response


class OrganizationEditPersonnelView(OrganizationEditView):
    model = MembershipPerson
    template_name = 'organization/edit-personnel.html'
    form_class = OrganizationPersonnelForm
    context_object_name = 'current_membership'
    slug_field_kwarg = 'organization_id'
    button = 'personnel'

    def get_reference_organization(self):
        return Organization.objects.get(uuid=self.kwargs['organization_id'])

    def get_success_url(self):
        organization_id = self.kwargs['organization_id']
        pk = self.kwargs['pk']

        if self.request.POST.get('_continue'):
            return reverse('edit-organization-personnel',
                           kwargs={'organization_id': organization_id,
                                   'pk': pk})
        else:
            return reverse('view-organization', kwargs={'slug': organization_id})

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['organization_id'] = self.kwargs['organization_id']
        return form_kwargs


class OrganizationCreatePersonnelView(EditButtonsMixin, BaseCreateView):
    model = MembershipPerson
    template_name = 'organization/create-personnel.html'
    form_class = OrganizationCreatePersonnelForm
    context_object_name = 'current_membership'
    slug_field_kwarg = 'organization_id'
    button = 'personnel'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization'] = Organization.objects.get(uuid=self.kwargs['organization_id'])
        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['organization_id'] = self.kwargs['organization_id']
        return form_kwargs

    def get_success_url(self):
        return reverse('edit-organization', kwargs={'slug': self.kwargs['organization_id']})


class OrganizationDeletePersonnelView(LoginRequiredMixin, BaseDeleteRelationshipView):
    model = MembershipPerson
    template_name = 'organization/delete-personnel.html'

    def get_cancel_link(self):
        return reverse_lazy(
            'edit-organization-personnel',
            kwargs={
                'organization_id': self.kwargs['organization_id'],
                'pk': self.kwargs['pk']
            }
        )

    def get_objects_to_update(self):
        membership = self.get_object()
        person = membership.member.get_value().value
        organization = membership.organization.get_value().value
        return person, organization

    def get_success_url(self):
        return reverse('view-organization', kwargs={'slug': self.kwargs['organization_id']})

    def delete(self, request, *args, **kwargs):
        person, organization = self.get_objects_to_update()

        response = super().delete(request, *args, **kwargs)

        person.object_ref_saved()
        organization.object_ref_saved()

        return response


class OrganizationEditEmplacementView(OrganizationEditView):
    model = Emplacement
    template_name = 'organization/edit-emplacement.html'
    form_class = OrganizationEmplacementForm
    context_object_name = 'current_emplacement'
    slug_field_kwarg = 'pk'
    button = 'location'

    def get_reference_organization(self):
        return Organization.objects.get(uuid=self.kwargs['organization_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['emplacements'] = [e.object_ref for e in context['organization'].emplacements]
        context['associations'] = [e.object_ref for e in context['organization'].associations]

        return context

    def get_success_url(self):
        organization_id = self.kwargs['organization_id']
        pk = self.kwargs['pk']

        if self.request.POST.get('_continue'):
            return reverse('edit-organization-emplacement',
                           kwargs={'organization_id': organization_id,
                                   'pk': pk})
        else:
            return reverse('view-organization', kwargs={'slug': organization_id})

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['organization_id'] = self.kwargs['organization_id']
        return form_kwargs


class OrganizationCreateEmplacementView(EditButtonsMixin, BaseCreateView):
    model = Emplacement
    template_name = 'organization/create-emplacement.html'
    form_class = OrganizationCreateEmplacementForm
    slug_field_kwarg = 'pk'
    button = 'location'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization'] = Organization.objects.get(uuid=self.kwargs['organization_id'])
        context['emplacements'] = [e.object_ref for e in context['organization'].emplacements]
        context['associations'] = [e.object_ref for e in context['organization'].associations]

        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['organization_id'] = self.kwargs['organization_id']
        return form_kwargs

    def get_success_url(self):
        return reverse('edit-organization', kwargs={'slug': self.kwargs['organization_id']})


class OrganizationDeleteEmplacementView(LoginRequiredMixin, BaseDeleteRelationshipView):
    model = Emplacement
    template_name = 'organization/delete-emplacement.html'

    def get_cancel_link(self):
        return reverse_lazy(
            'edit-organization-emplacement',
            kwargs={
                'organization_id': self.kwargs['organization_id'],
                'pk': self.kwargs['pk']
            }
        )

    def get_objects_to_update(self):
        emplacement = self.get_object()
        organization = emplacement.organization.get_value().value
        site = emplacement.site.get_value().value
        return organization, site

    def get_success_url(self):
        return reverse('view-organization', kwargs={'slug': self.kwargs['organization_id']})

    def delete(self, request, *args, **kwargs):
        organization, _ = self.get_objects_to_update()

        response = super().delete(request, *args, **kwargs)

        organization.object_ref_saved()

        return response


class OrganizationEditAssociationView(OrganizationEditView):
    model = Association
    template_name = 'organization/edit-association.html'
    form_class = OrganizationAssociationForm
    context_object_name = 'current_association'
    slug_field_kwarg = 'pk'
    button = 'location'

    def get_reference_organization(self):
        return Organization.objects.get(uuid=self.kwargs['organization_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['emplacements'] = [e.object_ref for e in context['organization'].emplacements]
        context['associations'] = [e.object_ref for e in context['organization'].associations]

        return context

    def get_success_url(self):
        organization_id = self.kwargs['organization_id']
        pk = self.kwargs['pk']

        if self.request.POST.get('_continue'):
            return reverse('edit-organization-association',
                           kwargs={'organization_id': organization_id,
                                   'pk': pk})
        else:
            return reverse('view-organization', kwargs={'slug': organization_id})


class OrganizationCreateAssociationView(EditButtonsMixin, BaseCreateView):
    model = Association
    template_name = 'organization/create-association.html'
    form_class = OrganizationCreateAssociationForm
    slug_field_kwarg = 'pk'
    button = 'location'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization'] = Organization.objects.get(uuid=self.kwargs['organization_id'])
        context['emplacements'] = [e.object_ref for e in context['organization'].emplacements]
        context['associations'] = [e.object_ref for e in context['organization'].associations]

        return context

    def get_success_url(self):
        return reverse('edit-organization', kwargs={'slug': self.kwargs['organization_id']})


class OrganizationDeleteAssociationView(LoginRequiredMixin, BaseDeleteRelationshipView):
    model = Association
    template_name = 'organization/delete-association.html'

    def get_cancel_link(self):
        return reverse_lazy(
            'edit-organization-association',
            kwargs={
                'organization_id': self.kwargs['organization_id'],
                'pk': self.kwargs['pk']
            }
        )

    def get_objects_to_update(self):
        association = self.get_object()
        organization = association.organization.get_value().value
        area = association.area.get_value().value
        return organization, area

    def get_success_url(self):
        return reverse('view-organization', kwargs={'slug': self.kwargs['organization_id']})

    def delete(self, request, *args, **kwargs):
        organization, _ = self.get_objects_to_update()

        response = super().delete(request, *args, **kwargs)

        organization.object_ref_saved()

        return response


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
