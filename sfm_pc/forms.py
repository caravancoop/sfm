# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from source.models import Source, Publication
from organization.models import Organization

class SourceForm(forms.Form):
    title = forms.CharField()
    publication = forms.ModelChoiceField(queryset=Publication.objects.all())
    published_on = forms.DateField()
    source_url = forms.URLField()
    archive_url = forms.URLField()

class OrgForm(forms.ModelForm):
     
    class Meta:
        model = Organization
        fields = '__all__'
 
