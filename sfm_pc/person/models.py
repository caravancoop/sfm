import reversion

from django.db import models
from utils import class_for_name
from source.models import Source

from complex_fields.model_decorators import versioned, translatable, sourced


class Person(models.Model):
    def get_name(self, lang='en'):
        return self.get_attribute(PersonName, lang)

    def get_alias(self, lang='en'):
        return self.get_attribute(PersonAlias, lang)

    def set_alias(self, value, lang='en'):
        self.set_attribute(PersonAlias, value, lang)

    def get_notes(self, lang='en'):
        return self.get_attribute(PersonNotes, lang)

    def get_attribute(self, object_type, lang='en'):
        queryset = object_type.objects.filter(person=self, lang=lang)
        values = list(queryset[:1])
        if values:
            return values[0].value
        return None

    def set_attribute(self, object_type, value, lang='en'):
        queryset = object_type.objects.filter(person=self, lang=lang)
        values = list(queryset[:1])
        if values:
            values[0].value = value

    def get_attribute_object(self, object_type, lang='en'):
        if isinstance(object_type, str):
            object_type = class_for_name(object_type)
        queryset = object_type.objects.filter(person=self, lang=lang)
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

@translatable
@versioned
@sourced
class PersonName(models.Model):
    object = models.ForeignKey('Person')
    lang = models.CharField(max_length=5, null=False)
    value = models.TextField()
    source = models.ManyToManyField(Source)


class PersonAlias(models.Model):
    person = models.ForeignKey('Person')
    lang = models.CharField(max_length=5, null=False)
    value = models.TextField()
    source = models.ManyToManyField(Source)

    class Meta:
        unique_together = ('person', 'lang')

# reversion.register(PersonAlias)

class PersonNotes(models.Model):
    person = models.ForeignKey('Person')
    lang = models.CharField(max_length=5, null=False)
    value = models.TextField()

    class Meta:
        unique_together = ('person', 'lang')

# reversion.register(PersonNotes)
