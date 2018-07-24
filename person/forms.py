# -*- coding: utf-8 -*-
import sys

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _

from django_date_extensions.fields import ApproximateDateFormField

from complex_fields.models import ComplexFieldContainer

from source.models import Source
from .models import Person, PersonName, PersonAlias


class PersonForm(forms.ModelForm):

    object_type = 'person'

    # field name on person model, field name used to update complex field,
    # and what the ForeignKey is if there are multiple values

    edit_fields = [
        ('name', PersonName, False),
        ('aliases', PersonAlias, True),
    ]

    name = forms.CharField()
    aliases = forms.CharField(required=False)

    class Meta:
        model = Person
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean(self):
        # Get the fields and see if they have new sources attached

        all_fields = [f[0] for f in self.edit_fields]

        for field in all_fields:
            try:
                self.request.POST['{}_source'.format(field)]
            except KeyError:
                error = forms.ValidationError(_('"%(field_name)s" requires a new source'),
                                              code='invalid',
                                              params={'field_name': field})
                self.add_error(field, error)

    def save(self, commit=True):

        update_info = {}

        for field_name, field_model, multiple_values in self.edit_fields:
            new_source_ids = self.request.POST.getlist('{}_source'.format(field_name))

            new_sources = Source.objects.filter(uuid__in=new_source_ids)

            field = ComplexFieldContainer.field_from_str_and_id(
                'person', self.instance.id, field_name
            )

            existing_sources = field.get_sources()

            if existing_sources:
                all_sources = new_sources | existing_sources

            confidence = field.get_confidence()

            for update_value in self.request.POST.getlist(field_name):
                update_key = '{0}_{1}'.format(self.instance._meta.object_name, field_model._meta.object_name)

                if multiple_values:
                    try:
                        update_info[update_key]['values'].append(update_value)
                    except KeyError:
                        update_info[update_key] = {
                            'values': [update_value],
                            'sources': all_sources,
                            'confidence': confidence,
                            'field_name': 'aliases'
                        }
                else:
                    update_info[update_key] = {
                        'sources': all_sources,
                        'confidence': confidence,
                        'value': update_value
                    }

        self.instance.update(update_info)
