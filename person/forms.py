# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _

from django_date_extensions.fields import ApproximateDateFormField

from source.models import Source
from .models import Person, PersonName, PersonAlias, Alias


class PersonForm(forms.ModelForm):

    object_type = 'person'

    # field name on person model, field name used to update complex field,
    # and what the ForeignKey is if there are multiple values

    edit_fields = [
        ('name', 'Person_PersonName', None),
        ('aliases', 'Person_PersonAlias', Alias)
    ]

    name = forms.ModelChoiceField(queryset=PersonName.objects.all())
    aliases = forms.ModelMultipleChoiceField(queryset=PersonAlias.objects.all())

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
                error = forms.ValidationError(_('The field %(field_name) requires another source'),
                                              code='invalid',
                                              params={'field_name': field})
                self.add_error(field, error)


    def save(self, commit=True):
        for field_name, update_name, foreign_key in self.edit_fields:
            session_key = '{0}-{1}-{2}'.format(self.object_type, field_name, person.id)

            # If there are no new sources, we need to return an error. I guess
            # maybe RedirectView isn't the best choice ...
            print('session keys', self.request.session.keys())
            new_source_ids = self.request.session.get(session_key)
            new_sources = Source.objects.filter(uuid__in=new_source_ids)

            field = ComplexFieldContainer.field_from_str_and_id(
                'person', self.instance.id, field_name
            )

            existing_sources = field.get_sources()

            all_sources = new_sources | existing_sources

            confidence = field.get_confidence()

            for update_value in self.request.POST.getlist(field_name):

                if foreign_key is not None:

                    relation_name = update_name.rsplit('_', 1)[1]
                    relation = getattr(sys.modules[__name__], relation_name)

                    try:
                        update_value = relation.objects.get(id=update_value).value
                    except ValueError:
                        update_value = foreign_key.objects.create(value=update_value)

                update_info = {
                    update_name: {
                        'sources': [s for s in all_sources],
                        'confidence': confidence,
                        'value': update_value
                    },
                }
                self.instance.update(update_info)
                self.instance.save()
