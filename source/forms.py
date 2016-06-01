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
    
    def clean_publication(self):
        data = self.cleaned_data['publication']
        
        return data

    def clean(self):
        print('before clean')
        cleaned_data = super(SourceForm, self).clean()
        print('after clean')

        return cleaned_data
