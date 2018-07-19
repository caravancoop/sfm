# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _

from django_date_extensions.fields import ApproximateDateFormField

from .models import Person, PersonName, PersonAlias

class PersonForm(forms.ModelForm):

    name = forms.ModelChoiceField(queryset=PersonName.objects.all())
    aliases = forms.ModelMultipleChoiceField(queryset=PersonAlias.objects.all())

    class Meta:
        model = Person
        fields = '__all__'

    def clean_aliases(self):
        data = self.cleaned_data['aliases']

        return data

    def clean_name(self):
        data = self.cleaned_data['name']

        return data

    def save(self, commit=True):
        print(self.instance)
        return super().save(commit=commit)

