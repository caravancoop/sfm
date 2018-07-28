# -*- coding: utf-8 -*-
from django import forms

class MergeForm(forms.Form):
    canonical_record = forms.CharField()


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


class BaseEditForm(forms.ModelForm):

    # Subclasses need to define Meta like so:
    #
    # class Meta:
    #     model = Person
    #     fields = '__all__'
    #
    # And static properties:
    #
    # edit_fields: 3 tuple of field_name on main entity model, reference to the
    # field model, and whether it expects mutiple values like so:
    #
    # edit_fields = [
    #     ('name', PersonName, False),
    #     ('aliases', PersonAlias, True),
    #     ('gender', PersonGender, False),
    #     ('division_id', PersonDivisionId, False),
    #     ('date_of_birth', PersonDateOfBirth, False),
    #     ('date_of_death', PersonDateOfDeath, False),
    #     ('deceased', PersonDeceased, False),
    #     ('biography', PersonBiography, False),
    #     ('notes', PersonNotes, False),
    #     ('external_links', PersonExternalLink, True),
    # ]

    def __init__(self, *args, **kwargs):
        self.post_data = dict(kwargs.pop('post_data'))
        self.object_ref_pk = kwargs.pop('object_ref_pk')
        super().__init__(*args, **kwargs)

    @property
    def object_type(self):
        return self._meta.model._meta.model_name

    def clean(self):

        # Get the fields and see if they have new sources attached
        modified_fields = self.post_data.get('modified_fields')

        for field in modified_fields:
            # Check if a field is a boolean field. If so, and there are sources
            # that were sent, that means that the user unchecked the box and we
            # need to change the value from True to False.

            if isinstance(self.fields[field], forms.BooleanField):
                if self.post_data.get('{}_source'.format(field)):
                    value = True

                    # Clear out "field is required" validation error that
                    # happens when you toggle from True to False. If there is an
                    # error, we also know that the value should be False
                    try:
                        self.errors.pop(field)
                        value = False
                    except KeyError:
                        pass

                    self.cleaned_data[field] = value
                    self.post_data[field] = [value]

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

            if field_name in self.post_data.get('modified_fields'):

                new_source_ids = self.post_data.get('{}_source'.format(field_name))

                sources = Source.objects.filter(uuid__in=new_source_ids)

                field = ComplexFieldContainer.field_from_str_and_id(
                    self.object_type, self.instance.id, field_name
                )

                existing_sources = field.get_sources()

                if existing_sources:
                    sources = sources | existing_sources

                confidence = field.get_confidence()

                for update_value in self.post_data.get(field_name):
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
