# -*- coding: utf-8 -*-
import sys

from django import forms
from django.conf import settings

from django_date_extensions.fields import ApproximateDateFormField

from sfm_pc.forms import BaseEditForm, GetOrCreateChoiceField

from membershipperson.models import MembershipPersonOrganization, \
    MembershipPerson, MembershipPersonRank, MembershipPersonRole, \
    MembershipPersonTitle, MembershipPersonFirstCitedDate, \
    MembershipPersonLastCitedDate, MembershipPersonRealStart, \
    MembershipPersonRealEnd, MembershipPersonStartContext, \
    MembershipPersonEndContext, Rank, Role

from organization.models import Organization

from .models import Person, PersonName, PersonAlias, PersonGender, \
    PersonDivisionId, PersonDateOfDeath, PersonDateOfBirth, PersonExternalLink, \
    PersonDeceased, PersonBiography, PersonNotes


class PersonBasicsForm(BaseEditForm):

    edit_fields = [
        ('name', PersonName, False),
        ('aliases', PersonAlias, True),
        ('gender', PersonGender, False),
        ('division_id', PersonDivisionId, False),
        ('date_of_birth', PersonDateOfBirth, False),
        ('date_of_death', PersonDateOfDeath, False),
        ('deceased', PersonDeceased, False),
        ('biography', PersonBiography, False),
        ('notes', PersonNotes, False),
        ('external_links', PersonExternalLink, True),
    ]

    name = forms.CharField()
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female')], required=False)
    division_id = forms.CharField(required=False)
    date_of_birth = ApproximateDateFormField(required=False)
    date_of_death = ApproximateDateFormField(required=False)
    deceased = forms.BooleanField()
    biography = forms.CharField(required=False)
    notes = forms.CharField(required=False)

    class Meta:
        model = Person
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['aliases'] = GetOrCreateChoiceField(queryset=PersonAlias.objects.filter(object_ref__uuid=self.object_ref_pk),
                                                        required=False,
                                                        object_ref_pk=self.object_ref_pk,
                                                        object_ref_model=self._meta.model)
        self.fields['external_links'] = GetOrCreateChoiceField(queryset=PersonExternalLink.objects.filter(object_ref__uuid=self.object_ref_pk),
                                                               required=False,
                                                               object_ref_pk=self.object_ref_pk,
                                                               object_ref_model=self._meta.model)


class PersonPostingsForm(BaseEditForm):
    edit_fields = [
        ('organization', MembershipPersonOrganization, False),
        ('rank', MembershipPersonRank, False),
        ('role', MembershipPersonRole, False),
        ('title', MembershipPersonTitle, False),
        ('firstciteddate', MembershipPersonFirstCitedDate, False),
        ('lastciteddate', MembershipPersonLastCitedDate, False),
        ('realstart', MembershipPersonRealStart, False),
        ('realend', MembershipPersonRealEnd, False),
        ('startcontext', MembershipPersonStartContext, False),
        ('endcontext', MembershipPersonEndContext, False),
    ]

    organization = forms.ModelChoiceField(queryset=Organization.objects.all())
    rank = forms.ModelChoiceField(queryset=Rank.objects.distinct('value'))
    role = forms.ModelChoiceField(queryset=Role.objects.distinct('value'))
    title = forms.CharField(required=False)
    firstciteddate = ApproximateDateFormField(required=False)
    lastciteddate = ApproximateDateFormField(required=False)
    realstart = forms.BooleanField()
    realend = forms.BooleanField()
    startcontext = forms.CharField(required=False)
    endcontext = forms.CharField(required=False)

    class Meta:
        model = MembershipPerson
        fields = '__all__'
