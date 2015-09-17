from django.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from source.models import Source

from complex_fields.model_decorators import versioned, translated, sourced
from complex_fields.models import (ComplexField, ComplexFieldContainer)


class Person(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ComplexFieldContainer(self, PersonName)
        self.alias = ComplexFieldContainer(self, PersonAlias)
        self.notes = ComplexFieldContainer(self, PersonNotes)
        self.complex_fields = [self.name, self.alias, self.notes]

    @classmethod
    def from_id(cls, id_):
        queryset = cls.objects.filter(id=id_)
        persons = list(queryset[:1])
        if persons:
            return persons[0]
        return None

    def validate(self, dict_values, lang):
        errors = {}
        for field in self.complex_fields:
            field_name = field.get_field_str_id()

            sources = dict_values[field_name].get('sources', [])
            error = field.validate(dict_values[field_name], lang, sources)
            if error is not None:
                errors[field_name] = error

        return errors

    def update(self, dict_values, lang=get_language()):
        errors = self.validate(dict_values, lang)
        if len(errors):
            return errors
        for field in self.complex_fields:
            field_name = field.get_field_str_id()

            sources = Source.create_sources(dict_values[field_name].get('sources', []))
            field.update(dict_values[field_name]['value'], lang, sources)

    @classmethod
    def create(cls, dict_values, lang=get_language()):
        person = cls()
        person.save()
        person.update(dict_values, lang)
        return person


@translated
@versioned
@sourced
class PersonName(ComplexField):
    object_ref = models.ForeignKey('Person')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Name")

@translated
@versioned
@sourced
class PersonAlias(ComplexField):
    object_ref = models.ForeignKey('Person')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Aliases")

@versioned
class PersonNotes(ComplexField):
    object_ref = models.ForeignKey('Person')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Notes")

