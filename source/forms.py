# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from .models import Source


class SourceForm(forms.Form):
    title = forms.CharField()
    publication = forms.ChoiceField()
    published_on = forms.DateField()
    source_url = forms.URLField()
    archive_url = forms.URLField()
    
    def clean(self):
        cleaned_data = super(SourceForm, self).clean()
        print(cleaned_data)
        
        return cleaned_data
