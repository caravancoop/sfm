# -*- coding: utf-8 -*-
import sys

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _

from django_date_extensions.fields import ApproximateDateFormField

from sfm_pc.forms import BaseEditForm, GetOrCreateChoiceField, BasePostingsForm

from organization.models import Organization
from membershipperson.models import MembershipPersonOrganization

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

    name = forms.CharField(label=_("Name"))
    gender = forms.ChoiceField(label=_("Gender"),
                               choices=[('Male', _('Male')), ('Female', _('Female'))],
                               required=False)
    division_id = forms.CharField(label=_("Country"), required=False)
    date_of_birth = ApproximateDateFormField(label=_("Date of birth"), required=False)
    date_of_death = ApproximateDateFormField(label=_("Date of death"), required=False)
    deceased = forms.BooleanField(label=_("Deceased"))
    biography = forms.CharField(label=_("Biography"), required=False)
    notes = forms.CharField(label=_("Notes"), required=False)

    class Meta:
        model = Person
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['aliases'] = GetOrCreateChoiceField(label=_("Other names"),
                                                        queryset=PersonAlias.objects.filter(object_ref__uuid=self.object_ref_pk),
                                                        required=False,
                                                        object_ref_pk=self.object_ref_pk,
                                                        object_ref_model=self._meta.model,
                                                        form=self,
                                                        field_name='aliases')
        self.fields['external_links'] = GetOrCreateChoiceField(label=_("External links"),
                                                               queryset=PersonExternalLink.objects.filter(object_ref__uuid=self.object_ref_pk),
                                                               required=False,
                                                               object_ref_pk=self.object_ref_pk,
                                                               object_ref_model=self._meta.model,
                                                               form=self,
                                                               field_name='external_links')


class PersonPostingsForm(BasePostingsForm):
    edit_fields = BasePostingsForm.edit_fields + [('organization', MembershipPersonOrganization, False)]

    organization = forms.ModelChoiceField(label=_("Organization"), queryset=Organization.objects.all())
