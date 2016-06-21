# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms

from cities.models import City

from source.models import Source, Publication
from organization.models import Organization, OrganizationName, \
    Classification, Alias
from person.models import Person, PersonName
from person.models import Alias as Alias2
from membershipperson.models import Role, Rank, Context, MembershipPerson
from django.utils.translation import ugettext as _

from django_date_extensions.fields import ApproximateDateFormField

class SourceForm(forms.Form):
    title = forms.CharField()
    publication = forms.CharField()
    published_on = forms.DateField()
    source_url = forms.URLField()
    archive_url = forms.URLField()

class OrgForm(forms.Form):
    name = forms.CharField()
    name_text = forms.CharField()
    classification = forms.ModelChoiceField(queryset=Classification.objects.all())
    alias = forms.CharField(required=False)
    foundingdate = ApproximateDateFormField(required=False)
    realfounding = forms.BooleanField(required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.empty_permitted = False

class PersonForm(forms.Form):
    name = forms.CharField()
    name_text = forms.CharField()
    alias = forms.CharField(required=False)
    deathdate = ApproximateDateFormField(required=False)
    orgs = forms.CharField() 

class PersonMembershipForm(forms.Form):
    membership = forms.ModelChoiceField(queryset=MembershipPerson.objects.all())
    role = forms.CharField(required=False)
    title = forms.CharField(required=False)
    rank = forms.CharField(required=False)
    realstart = forms.BooleanField(required = False) 
    realend = forms.BooleanField(required = False)
    startcontext = forms.CharField(required=False)
    endcontext = forms.CharField(required=False)
    firstciteddate = ApproximateDateFormField(required=False)
    lastciteddate = ApproximateDateFormField(required=False)
    first = forms.BooleanField(required=False)

class OrganizationGeographyForm(forms.Form):
    geography_type = forms.ChoiceField(choices=(('Site','Site'),('Area','Area'),))
    name = forms.CharField()
    geoname = forms.CharField()
    geoname_text = forms.CharField()
    startdate = ApproximateDateFormField(required=False)
    enddate = ApproximateDateFormField(required=False)
    org = forms.CharField()
    geotype = forms.CharField()
