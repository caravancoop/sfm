# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from source.models import Source, Publication
from organization.models import Organization, OrganizationName, \
    Classification, Alias
from person.models import Person, PersonName
from person.models import Alias as Alias2
from django.utils.translation import ugettext as _

from django_date_extensions.fields import ApproximateDateFormField

class SourceForm(forms.Form):
    title = forms.CharField()
    publication = forms.ModelChoiceField(queryset=Publication.objects.all())
    published_on = forms.DateField()
    source_url = forms.URLField()
    archive_url = forms.URLField()

class OrgForm(forms.Form):
    name = forms.ModelChoiceField(queryset=OrganizationName.objects.all())
    classification = forms.ModelMultipleChoiceField(queryset=Classification.objects.all())
    alias = forms.ModelMultipleChoiceField(queryset=Alias.objects.all(), required=False)
    foundingdate = ApproximateDateFormField(required=False)
    realfounding = forms.BooleanField(required=False)
    dissolutiondate = ApproximateDateFormField(required=False)
    realdissolution = forms.BooleanField(required=False)
    

class PersonForm(forms.Form):
    name = forms.ModelChoiceField(queryset=PersonName.objects.all()) 
    alias = forms.ModelMultipleChoiceField(queryset=Alias2.objects.all(), required=False)
    deathdate = ApproximateDateFormField(required=False)

