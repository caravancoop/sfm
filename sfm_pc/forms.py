# -*- coding: utf-8 -*-
from django import forms

class MergeForm(forms.Form):
    canonical_record = forms.CharField()
