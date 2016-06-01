# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from .models import Source, Publication


class SourceForm(forms.Form):
    title = forms.CharField()
    publication = forms.ModelChoiceField(queryset=Publication.objects.all())
    published_on = forms.DateField()
    source_url = forms.URLField()
    archive_url = forms.URLField()
    
