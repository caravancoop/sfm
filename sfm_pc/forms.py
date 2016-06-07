# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from source.models import Source, Publication
from organization.models import Organization
from django.utils.translation import ugettext as _

class SourceForm(forms.Form):
    title = forms.CharField()
    publication = forms.ModelChoiceField(queryset=Publication.objects.all())
    published_on = forms.DateField()
    source_url = forms.URLField()
    archive_url = forms.URLField()

class OrgForm(forms.Form):
    name = forms.ModelChoiceField(queryset=Organization.objects.all())
    alias = forms.ModelMultipleChoiceField(queryset=Organization.objects.order_by().values('organizationalias__value').distinct(), required=False)
    classification = forms.ChoiceField(choices = (('Administrative', _('Administrative')), 
                                                  ('Command', _('Command')), 
                                                  ('Informal', _('Informal')), 
                                                  ('Organization', _('Organization')), ))
    foundingdate = forms.DateField(required=False)
    realfounding = forms.BooleanField(required=False)
    dissolutiondate = forms.DateField(required=False)
    realdissolution = forms.BooleanField(required=False)
    


