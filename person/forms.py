# -*- coding: utf-8 -*-
import sys

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _

from django_date_extensions.fields import ApproximateDateFormField

from complex_fields.models import ComplexFieldContainer

from source.models import Source
from .models import Person, PersonName, PersonAlias, PersonGender, \
    PersonDivisionId, PersonDateOfDeath, PersonDateOfBirth, PersonExternalLink


class PersonForm(forms.ModelForm):

    object_type = 'person'

    # field name on person model, the ForeignKey model and if there are multiple
    # values

    edit_fields = [
        ('name', PersonName, False),
        ('aliases', PersonAlias, True),
        ('gender', PersonGender, False),
        ('division_id', PersonDivisionId, False),
        ('date_of_birth', PersonDateOfBirth, False),
        ('date_of_death', PersonDateOfDeath, False),
        ('external_links', PersonExternalLink, True),
    ]

    name = forms.CharField()
    aliases = forms.CharField(required=False)
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female')], required=False)
    division_id = forms.CharField(required=False)
    date_of_birth = ApproximateDateFormField(required=False)
    date_of_death = ApproximateDateFormField(required=False)
    deceased = forms.BooleanField(required=False)
    external_links = forms.CharField(required=False)

    class Meta:
        model = Person
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean(self):
        # Get the fields and see if they have new sources attached

        modified_fields = self.request.POST.getlist('modified_fields')

        for field in modified_fields:
            try:
                value = self.request.POST[field]
                if value:
                    try:
                        self.request.POST['{}_sources']
                    except KeyError:
                        error = forms.ValidationError(_('"%(field_name)s" requires a new source'),
                                                    code='invalid',
                                                    params={'field_name': field})
                        self.add_error(field, error)
            except KeyError:
                pass

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
                        update_info[update_key]['sources'] | all_sources
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
