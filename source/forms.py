# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import ModelForm
from .models import Source


class SourceForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(SourceForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Source
        fields = '__all__'
