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

