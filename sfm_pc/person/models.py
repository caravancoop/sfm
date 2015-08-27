from django.db import models
from django.utils.translation import get_language
from utils import class_for_name
from source.models import Source

from complex_fields.model_decorators import versioned, translated, sourced
from complex_fields.models import (ComplexField, ComplexModel,
                                   ComplexFieldContainer)


class Person(ComplexModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ComplexFieldContainer(self, PersonName)
        self.alias = ComplexFieldContainer(self, PersonAlias)
        self.notes = ComplexFieldContainer(self, PersonNotes)
        self.complex_fields = ['name', 'alias', 'notes']

    @classmethod
    def from_id(cls, id_):
        queryset = cls.objects.filter(id=id_)
        persons = list(queryset[:1])
        if persons:
            return persons[0]
        return None

    def update(self, dict_values, dict_sources, lang=get_language()):
        for c_field in self.complex_fields:
            field = getattr(self, c_field)

            if 'sources' in dict_values[c_field]:
                sources = Source.create_sources(dict_values[c_field]['sources'])
                field.update(dict_values[c_field]['value'], lang=lang, sources=sources)
            else:
                field.update(dict_values[c_field]['value'], lang=lang)

    @classmethod
    def create(cls, dict_values, dict_sources, lang=get_language()):
        person = cls()
        person.save()
        person.update(dict_values, dict_sources, lang)
        return person


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

