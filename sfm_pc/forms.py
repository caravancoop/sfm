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
    title = forms.CharField(error_messages={'required': _('Title is required')})
    publication = forms.CharField(error_messages={'required': _('Publication is required')})
    published_on = forms.DateField(error_messages={'required': _('Date published is required')})
    source_url = forms.URLField(error_messages={'required': _('Source URL is required'), 'invalid': _('Source URL is invalid')})
    archive_url = forms.URLField(error_messages={'required': _('Archive URL is required'), 'invalid': _('Archive URL is invalid')})

class OrgForm(forms.Form):
    name = forms.CharField(error_messages={'required': _('Name is required')})
    name_text = forms.CharField()
    classification = forms.ModelChoiceField(queryset=Classification.objects.all())
    alias = forms.CharField(required=False)
    foundingdate = ApproximateDateFormField(required=False)
    realfounding = forms.BooleanField(required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.empty_permitted = False

class PersonForm(forms.Form):
    name = forms.CharField(error_messages={'required': _('Name is required')})
    name_text = forms.CharField()
    alias = forms.CharField(required=False)
    deathdate = ApproximateDateFormField(required=False)
    orgs = forms.CharField() 
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.empty_permitted = False

class PersonMembershipForm(forms.Form):
    membership = forms.ModelChoiceField(queryset=MembershipPerson.objects.all())
    role = forms.CharField(required=False)
    title = forms.CharField(error_messages={'required': _('Title is required')})
    rank = forms.CharField(required=False)
    realstart = forms.BooleanField(required=False) 
    realend = forms.BooleanField(required=False)
    startcontext = forms.CharField(required=False)
    endcontext = forms.CharField(required=False)
    firstciteddate = ApproximateDateFormField(required=False)
    lastciteddate = ApproximateDateFormField(required=False)
    first = forms.BooleanField(required=False)

class OrganizationGeographyForm(forms.Form):
    geography_type = forms.ChoiceField(choices=(('Site','Site'),('Area','Area'),), error_messages={'required': _('Geography type is required')})
    name = forms.CharField(error_messages={'required': _('Name is required')})
    geoname = forms.CharField(error_messages={'required': _('Geoname is required')})
    geoname_text = forms.CharField()
    startdate = ApproximateDateFormField(required=False)
    enddate = ApproximateDateFormField(required=False)
    org = forms.CharField()
    geotype = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.empty_permitted = False

class ViolationForm(forms.Form):
    startdate = ApproximateDateFormField(required=False)
    enddate = ApproximateDateFormField(required=False)
    locationdescription = forms.CharField(required=False)
    geoname = forms.CharField(required=False)
    geoname_text = forms.CharField(required=False)
    description = forms.CharField(required=True)
    perpetrators = forms.CharField(required=False)
    orgs = forms.CharField(required=False)
    vtype = forms.CharField(required=False)
    geotype = forms.CharField(required=False)
    # also has source and confidence
