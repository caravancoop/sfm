# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext as _

from django_date_extensions.fields import ApproximateDateFormField


class PersonForm(forms.Form):
    name = forms.CharField(error_messages={'required': _('Name is required')})
    name_text = forms.CharField()
    alias = forms.CharField(required=False)
    deathdate = ApproximateDateFormField(required=False)
    orgs = forms.CharField() 
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.empty_permitted = False
