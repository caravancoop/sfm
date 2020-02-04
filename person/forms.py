# -*- coding: utf-8 -*-
import sys

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _

from django_date_extensions.fields import ApproximateDateFormField

from sfm_pc.forms import BaseUpdateForm, BaseCreateForm, GetOrCreateChoiceField

from organization.models import Organization

from membershipperson.models import \
    MembershipPerson, MembershipPersonRank, MembershipPersonRole, \
    MembershipPersonTitle, MembershipPersonFirstCitedDate, \
    MembershipPersonLastCitedDate, MembershipPersonRealStart, \
    MembershipPersonRealEnd, MembershipPersonStartContext, \
    MembershipPersonEndContext, Rank, Role, MembershipPersonOrganization, \
    MembershipPersonMember

from .models import Person, PersonName, PersonAlias, PersonDivisionId, \
    PersonNotes


class PersonBasicsForm(BaseUpdateForm):

    edit_fields = [
        ('name', PersonName, False),
        ('aliases', PersonAlias, True),
        ('division_id', PersonDivisionId, False),
        ('notes', PersonNotes, False),
    ]

    name = forms.CharField(label=_("Name"))
    division_id = forms.CharField(label=_("Country"), required=False)
    notes = forms.CharField(label=_("Notes"), required=False)

    class Meta:
        model = Person
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        person_id = kwargs.pop('person_id', None)

        super().__init__(*args, **kwargs)

        self.fields['aliases'] = GetOrCreateChoiceField(label=_("Other names"),
                                                        queryset=PersonAlias.objects.filter(object_ref__uuid=person_id),
                                                        required=False,
                                                        object_ref_model=self._meta.model,
                                                        form=self,
                                                        field_name='aliases',
                                                        object_ref_pk=person_id)


class PersonCreateBasicsForm(BaseCreateForm, PersonBasicsForm):
    pass


class PersonPostingsForm(BaseUpdateForm):
    edit_fields = [
        ('rank', MembershipPersonRank, False),
        ('role', MembershipPersonRole, False),
        ('title', MembershipPersonTitle, False),
        ('firstciteddate', MembershipPersonFirstCitedDate, False),
        ('lastciteddate', MembershipPersonLastCitedDate, False),
        ('realstart', MembershipPersonRealStart, False),
        ('realend', MembershipPersonRealEnd, False),
        ('startcontext', MembershipPersonStartContext, False),
        ('endcontext', MembershipPersonEndContext, False),
        ('organization', MembershipPersonOrganization, False),
        ('member', MembershipPersonMember, False),
    ]

    clone_sources = {
        'member': 'organization',
    }

    organization = forms.ModelChoiceField(label=_("Organization"), queryset=Organization.objects.all())
    rank = forms.ModelChoiceField(label=_("Rank"), queryset=Rank.objects.distinct('value'), required=False)
    role = forms.ModelChoiceField(label=_("Role"), queryset=Role.objects.distinct('value'), required=False)
    title = forms.CharField(label=_("Title"), required=False)
    firstciteddate = ApproximateDateFormField(label=_("Date first cited"), required=False)
    lastciteddate = ApproximateDateFormField(label=_("Date last cited"), required=False)
    realstart = forms.BooleanField(label=_("Start date?"))
    realend = forms.BooleanField(label=_("End date?"))
    startcontext = forms.CharField(label=_("Context for start date"), required=False)
    endcontext = forms.CharField(label=_("Context for end date"), required=False)

    def __init__(self, *args, **kwargs):
        person_id = kwargs.pop('person_id')

        super().__init__(*args, **kwargs)

        self.fields['member'] = forms.ModelChoiceField(queryset=Person.objects.filter(uuid=person_id))

    class Meta:
        model = MembershipPerson
        fields = '__all__'


class PersonCreatePostingForm(BaseCreateForm, PersonPostingsForm):
    pass
