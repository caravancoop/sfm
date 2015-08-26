from django.db import models
from utils import class_for_name
from source.models import Source

from complex_fields.model_decorators import versioned, translated, sourced
from complex_fields.models import (ComplexField, ComplexModel,
                                   ComplexFieldContainer)


class Person(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ComplexFieldContainer(self, PersonName)
        self.alias = ComplexFieldContainer(self, PersonAlias)
        self.notes = ComplexFieldContainer(self, PersonNotes)
    def get_name(self, lang='EN'):
        return self.get_attribute(PersonName, lang)

    def get_alias(self, lang='EN'):
        return self.get_attribute(PersonAlias, lang)

    def set_alias(self, value, lang='EN'):
        self.set_attribute(PersonAlias, value, lang)

    def get_notes(self, lang='EN'):
        return self.get_attribute(PersonNotes, lang)

    def get_attribute(self, object_type, lang='EN'):
        queryset = object_type.objects.filter(object=self, lang=lang)
        values = list(queryset[:1])
        if values:
            return values[0].value
        return None

    def set_attribute(self, object_type, value, lang='EN'):
        queryset = object_type.objects.filter(object=self, lang=lang)
        values = list(queryset[:1])
        if values:
            values[0].value = value

    def get_attribute_object(self, object_type, lang='EN'):
        if isinstance(object_type, str):
            object_type = class_for_name(object_type)
        queryset = object_type.objects.filter(object=self, lang=lang)
        values = list(queryset[:1])
        if values:
            return values[0]
        return None

    @classmethod
    def from_id(cls, id_):
        queryset = cls.objects.filter(id=id_)
        persons = list(queryset[:1])
        if persons:
            return persons[0]
        return None


@translated
@versioned
@sourced
class PersonName(ComplexField):
    object = models.ForeignKey('Person')
    value = models.TextField(default=None, blank=True, null=True)

@translated
@versioned
@sourced
class PersonAlias(ComplexField):
    object = models.ForeignKey('Person')
    value = models.TextField(default=None, blank=True, null=True)

@versioned
class PersonNotes(ComplexField):
    object = models.ForeignKey('Person')
    value = models.TextField(default=None, blank=True, null=True)

