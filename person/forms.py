# -*- coding: utf-8 -*-
import sys

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _

from django_date_extensions.fields import ApproximateDateFormField

from complex_fields.models import ComplexFieldContainer

from source.models import Source
from .models import Person, PersonName, PersonAlias, Alias


class PersonForm(forms.ModelForm):

    object_type = 'person'

    # field name on person model, field name used to update complex field,
    # and what the ForeignKey is if there are multiple values

    edit_fields = [
        ('name', PersonName, None),
        ('aliases', PersonAlias, Alias)
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

        for field_name, field_model, foreign_key in self.edit_fields:
            new_source_ids = self.request.POST.getlist('{}_source'.format(field_name))

            new_sources = Source.objects.filter(uuid__in=new_source_ids)

            field = ComplexFieldContainer.field_from_str_and_id(
                'person', self.instance.id, field_name
            )

            existing_sources = field.get_sources()

            if existing_sources:
                all_sources = new_sources | existing_sources

            confidence = field.get_confidence()

            relation_set = getattr(self.instance, '{}_set'.format(field_model._meta.model_name.lower()))

            update_info = {}

            for update_value in self.request.POST.getlist(field_name):

                if foreign_key is not None:
                    try:
                        field_object = field_model.objects.get(id=update_value)
                        update_value = field_object.value.value
                        field_object.delete()
                    except ValueError:
                        pass

                    update_value, _ = foreign_key.objects.get_or_create(value=update_value)
                    field_object, created = field_model.objects.get_or_create(value=update_value,
                                                                              object_ref=self.instance,
                                                                              lang='en',
                                                                              confidence=confidence)
                    field_object.sources = all_sources
                    field_object.save()
                else:
                    update_info.update(**{
                        '{0}_{1}'.format(self.instance._meta.object_name, field_model._meta.object_name): {
                            'sources': all_sources,
                            'confidence': confidence,
                            'value': update_value
                        }
                    })

            self.instance.update(update_info)
