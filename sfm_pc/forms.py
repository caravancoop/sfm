# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext as _, get_language

from complex_fields.models import ComplexFieldContainer

from django_date_extensions.fields import ApproximateDateFormField

from source.models import Source
from organization.models import Organization
from membershipperson.models import \
    MembershipPerson, MembershipPersonRank, MembershipPersonRole, \
    MembershipPersonTitle, MembershipPersonFirstCitedDate, \
    MembershipPersonLastCitedDate, MembershipPersonRealStart, \
    MembershipPersonRealEnd, MembershipPersonStartContext, \
    MembershipPersonEndContext, Rank, Role


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
                super().clean([v])
                pks.append(v)
            except forms.ValidationError as e:
                object_ref_fields = [f.column for f in self.object_ref_model._meta.fields]
                if 'uuid' in object_ref_fields:
                    object_ref = self.object_ref_model.objects.get(uuid=self.object_ref_pk)
                else:
                    object_ref = self.object_ref_model.objects.get(id=self.object_ref_pk)
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

        try:
            del self.post_data['csrfmiddlewaretoken']
        except KeyError:
            pass

        self.object_ref_pk = kwargs.pop('object_ref_pk')
        self.update_fields = set()

        super().__init__(*args, **kwargs)

    @property
    def object_type(self):
        return self._meta.model._meta.model_name

    def _validate_boolean(self):
        boolean_fields = [f for f in self.fields if isinstance(self.fields[f], forms.BooleanField)]

        for field in boolean_fields:

            if field in self.changed_data:
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
            else:
                # The boolean fields are not actually required but Django
                # forces them to be.
                try:
                    self.errors.pop(field)
                except KeyError:
                    pass

    def _validate_complex_field(self, field_instance, field):
        if field_instance.get_value() and field_instance.get_value().value and \
                (field_instance.get_value().value != self.cleaned_data.get(field)):

            try:
                self.post_data['{}_source'.format(field)]
                self.update_fields.add(field)
            except KeyError:
                error = forms.ValidationError(_('"%(field_name)s" requires a new source'),
                                            code='invalid',
                                            params={'field_name': field})
                self.add_error(field, error)

    def _validate_complex_list(self, field_instance, field):
        old_values = {f.get_value() for f in field_instance.get_list()}
        new_values = set(self.cleaned_data.get(field))

        if new_values != old_values:
            try:
                self.post_data['{}_source'.format(field)]
                self.update_fields.add(field)
            except KeyError:
                error = forms.ValidationError(_('"%(field_name)s" requires a new source'),
                                            code='invalid',
                                            params={'field_name': field})
                self.add_error(field, error)

    def _validate_sources_present(self, sources_sent, values_sent):
        # If there were field values that were sent without sources, check to
        # see if the value changed and if so, we need sources

        values_without_sources = values_sent - sources_sent

        for field in values_without_sources:
            field_instance = getattr(self.instance, field)

            if field_instance in self.instance.complex_fields:
                self._validate_complex_field(field_instance, field)

            elif field_instance in self.instance.complex_lists:
                self._validate_complex_list(field_instance, field)

    def clean(self):

        # Need to validate booleans first cuz Django is being difficult

        self._validate_boolean()

        sources_sent = {k.replace('_source', '') for k in self.post_data.keys() if '_source' in k}
        values_sent = {f for f in self.post_data.keys() if not '_source' in f}

        self._validate_sources_present(sources_sent, values_sent)

        # If there were sources sent without values, that's OK we just need to
        # make sure that we save the sources

        sources_without_values = sources_sent - values_sent

        for field in sources_without_values:
            field_instance = getattr(self.instance, field)
            if field_instance in self.instance.complex_fields:
                field_value = field_instance.get_value().value

            elif field_instance in self.instance.complex_lists:
                field_value = [f.get_value().id for f in field_instance.get_list()]

            self.post_data[field] = field_value
            self.update_fields.add(field)

        self.update_fields = self.update_fields | sources_sent

        for field in self.update_fields:

            # If the posted value is empty but there are sources, that means
            # that the user cleared out the value and gave evidence as to
            # why that was the case. Unfortunately, if the value is empty,
            # Django removes it from the POST data altogether (I guess it's
            # trying to do us a favor?). Anyways, we need to add that back
            # in so we can clear out the value from the field.

            if not self.post_data.get(field) and self.post_data.get('{}_source'.format(field)) is not None:
                # If the field is a GetOrCreate field that means that we
                # should make the value an empty list. Otherwise it should
                # be None

                if isinstance(self.fields[field], GetOrCreateChoiceField):
                    self.post_data[field] = []

                else:
                    self.post_data[field] = None

    def save(self, commit=True):

        update_info = {}

        for field_name, field_model, multiple_values in self.edit_fields:

            if field_name in self.update_fields:

                new_source_ids = self.post_data['{}_source'.format(field_name)]

                sources = Source.objects.filter(uuid__in=new_source_ids)

                field = ComplexFieldContainer.field_from_str_and_id(
                    self.object_type, self.instance.id, field_name
                )

                existing_sources = field.get_sources()

                if existing_sources:
                    sources = sources | existing_sources

                confidence = field.get_confidence()

                update_value = self.cleaned_data[field_name]
                update_key = '{0}_{1}'.format(self.instance._meta.object_name, field_model._meta.object_name)

                update_info[update_key] = {
                    'sources': sources,
                    'confidence': confidence,
                }

                if multiple_values:
                    update_info[update_key]['values'] = update_value
                    # Sometimes the object that we want the values to normalize
                    # to are not the complex field containers. For instance, we
                    # want the violation perpetrators to normalize to a Person
                    # object, not a ViolationPerpetrator object so that we can
                    # search across all the people, not just the ones who have
                    # committed violations. So, if the values in update_value
                    # are not instances of the field_model, we need to get or
                    # create those and replace the values with the instances of
                    # the field_model so that the validation, etc works under
                    # the hood.

                    new_values = []

                    for value in update_value:
                        if not isinstance(value, field_model):
                            value, _ = field_model.objects.get_or_create(value=value,
                                                                         object_ref=self.instance,
                                                                         lang=get_language())
                            new_values.append(value)

                    if new_values:
                        update_info[update_key]['values'] = new_values
                else:
                    update_info[update_key]['value'] = update_value

        if update_info:
            self.instance.update(update_info)

        self.instance.object_ref_saved()


class BasePostingsForm(BaseEditForm):
    edit_fields = [
        ('rank', MembershipPersonRank, False),
        ('role', MembershipPersonRole, False),
        ('title', MembershipPersonTitle, False),
        ('firstciteddate', MembershipPersonFirstCitedDate, False),
        ('lastciteddate', MembershipPersonLastCitedDate, False),
        ('realstart', MembershipPersonRealStart, False),
        ('realend', MembershipPersonRealEnd, False),
        ('startcontext', MembershipPersonStartContext, False),
        ('endcontext', MembershipPersonEndContext, False),
    ]

    organization = forms.ModelChoiceField(queryset=Organization.objects.all())
    rank = forms.ModelChoiceField(queryset=Rank.objects.distinct('value'))
    role = forms.ModelChoiceField(queryset=Role.objects.distinct('value'))
    title = forms.CharField(required=False)
    firstciteddate = ApproximateDateFormField(required=False)
    lastciteddate = ApproximateDateFormField(required=False)
    realstart = forms.BooleanField()
    realend = forms.BooleanField()
    startcontext = forms.CharField(required=False)
    endcontext = forms.CharField(required=False)

    class Meta:
        model = MembershipPerson
        fields = '__all__'
