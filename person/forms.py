# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import ModelForm
from .models import Person


class PersonForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Person
        fields = '__all__'
