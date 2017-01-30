from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect

from sfm_pc.base_views import BaseFormSetView

from source.models import Source
from membershiporganization.forms import MembershipOrganizationForm
from organization.models import Organization
from membershiporganization.models import MembershipOrganization

class MembershipOrganizationCreate(BaseFormSetView):
    template_name = 'membershiporganization/create.html'
    form_class = MembershipOrganizationForm
    success_url = reverse_lazy('create-person')
    extra = 0
    max_num = None

    def get_initial(self):
        data = []
        for i in self.request.session['organizations']:
            data.append({})
        return data

    def get(self, request, *args, **kwargs):
        if len(request.session['organizations']) == 1:
            return redirect(reverse_lazy('create-person'))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['source'] = Source.objects.get(id=self.request.session['source_id'])
        context['organizations'] = self.request.session['organizations']

        return context

    def formset_valid(self, formset):
        source = Source.objects.get(id=self.request.session['source_id'])
        num_forms = int(formset.data['form-TOTAL_FORMS'][0])

        for i in range(0, num_forms):
            form_prefix = 'form-{0}-'.format(i)

            member_id = formset.data[form_prefix + 'member']
            member_organization = Organization.objects.get(id=member_id)

            organization_id = formset.data[form_prefix + 'organization']
            organization = Organization.objects.get(id=organization_id)

            membership_info = {
                'MembershipOrganization_MembershipOrganizationMember': {
                    'value': member_organization,
                    'confidence': 1,
                    'sources': [source],
                },
                'MembershipOrganization_MembershipOrganizationOrganization': {
                    'value': organization,
                    'confidence': 1,
                    'sources': [source]
                },
            }

            if formset.data.get(form_prefix + 'firstciteddate'):
                membership_info['MembershipOrganization_MembershipOrganizationFirstCitedDate'] = {
                    'value': formset.data[form_prefix + 'firstciteddate'],
                    'confidence': 1,
                    'sources': [source]
                }

            if formset.data.get(form_prefix + 'lastciteddate'):
                membership_info['MembershipOrganization_MembershipOrganizationLastCitedDate'] = {
                    'value': formset.data[form_prefix + 'lastciteddate'],
                    'confidence': 1,
                    'sources': [source]
                }


            try:
                membership = MembershipOrganization.objects.get(membershiporganizationmember__value=member_organization,
                                                                membershiporganizationorganization__value=organization)
                sources = set(self.sourcesList(membership, 'member') + \
                              self.sourcesList(membership, 'organization'))
                membership_info['MembershipOrganization_MembershipOrganizationMember']['sources'] += sources
                membership.update(membership_info)

            except MembershipOrganization.DoesNotExist:
                membership = MembershipOrganization.create(membership_info)

        response = super().formset_valid(formset)
        return response
