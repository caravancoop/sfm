# -*- coding: utf-8 -*-
import sys

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _, get_language

from django_date_extensions.fields import ApproximateDateFormField

from complex_fields.models import ComplexFieldContainer

from source.models import Source
from .models import Person, PersonName, PersonAlias, PersonGender, \
    PersonDivisionId, PersonDateOfDeath, PersonDateOfBirth, PersonExternalLink, \
    PersonDeceased


class GetOrCreateChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self,
                 queryset,
                 required=True,
                 widget=None,
                 label=None,
                 initial=None,
                 help_text='',
                 *args,
                 **kwargs):

        self.object_ref_pk = kwargs.pop('object_ref_pk')
        self.object_ref_model = kwargs.pop('object_ref_model')

        super().__init__(queryset,
                         required=required,
                         widget=widget,
                         label=label,
                         initial=initial,
                         help_text=help_text,
                         *args,
                         **kwargs)


    def clean(self, value):

        pks = []

        for v in value:
            try:
                queryset = super().clean([v])
                pks.append(v)
            except forms.ValidationError as e:
                object_ref = self.object_ref_model.objects.get(uuid=self.object_ref_pk)
                instance = self.queryset.model.objects.create(value=e.params['pk'],
                                                              object_ref=object_ref,
                                                              lang=get_language())
                pks.append(instance.id)

        return self.queryset.model.objects.filter(pk__in=pks)


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
        ('deceased', PersonDeceased, False),
        ('external_links', PersonExternalLink, True),
    ]

    name = forms.CharField()
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
        self.post_data = kwargs.pop('post_data')
        object_ref_pk = kwargs.pop('object_ref_pk')
        super().__init__(*args, **kwargs)
        self.fields['aliases'] = GetOrCreateChoiceField(queryset=PersonAlias.objects.filter(object_ref__uuid=object_ref_pk),
                                                        required=False,
                                                        object_ref_pk=object_ref_pk,
                                                        object_ref_model=self._meta.model)

    def clean(self):

        # Get the fields and see if they have new sources attached
        modified_fields = self.post_data.getlist('modified_fields')

        for field in modified_fields:
            try:
                self.post_data['{}_source'.format(field)]
            except KeyError:
                error = forms.ValidationError(_('"%(field_name)s" requires a new source'),
                                              code='invalid',
                                              params={'field_name': field})
                self.add_error(field, error)

    def save(self, commit=True):

        update_info = {}

        for field_name, field_model, multiple_values in self.edit_fields:

            if field_name in self.post_data.getlist('modified_fields'):

                new_source_ids = self.post_data.getlist('{}_source'.format(field_name))

                sources = Source.objects.filter(uuid__in=new_source_ids)

                field = ComplexFieldContainer.field_from_str_and_id(
                    'person', self.instance.id, field_name
                )

                existing_sources = field.get_sources()

                if existing_sources:
                    sources = sources | existing_sources

                confidence = field.get_confidence()

                # TODO: It would appear that Django does not send anything for
                # a checkbox that is unchecked. So, checking for the absence of
                # something might be hard.

                for update_value in self.post_data.getlist(field_name):
                    update_key = '{0}_{1}'.format(self.instance._meta.object_name, field_model._meta.object_name)

                    update_value = self.cleaned_data[field_name]

                    if multiple_values:
                        try:
                            update_info[update_key]['values'] | update_value
                        except KeyError:
                            update_info[update_key] = {
                                'values': update_value,
                                'sources': sources,
                                'confidence': confidence,
                            }
                    else:
                        update_info[update_key] = {
                            'sources': sources,
                            'confidence': confidence,
                            'value': update_value
                        }

        if update_info:
            self.instance.update(update_info)
