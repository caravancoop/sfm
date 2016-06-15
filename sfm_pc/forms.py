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

class PersonMembershipForm(forms.Form):
    membership = forms.ModelChoiceField(queryset=MembershipPerson.objects.all())
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=False)
    title = forms.CharField(required=False)
    rank = forms.ModelChoiceField(queryset=Rank.objects.all(), required=False)
    realstart = forms.BooleanField(required = False) 
    realend = forms.BooleanField(required = False)
    startcontext = forms.ModelChoiceField(queryset=Context.objects.all(), required=False)
    endcontext = forms.ModelChoiceField(queryset=Context.objects.all(), required=False)
    first = forms.BooleanField(required=False)

class OrganizationGeographyForm(forms.Form):
    geography_type = forms.ChoiceField(choices=(('Site', 'Site',), ('Area', 'Area',),))
    name = forms.CharField()
    geoname = forms.ModelChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        cities_by_country = City.objects.filter(country__code=kwargs['country_code'])
        self.fields['geoname'].queryset = cities_by_country
