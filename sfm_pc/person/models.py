from django.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import get_language

from django_date_extensions.fields import ApproximateDateField

from source.models import Source
from complex_fields.model_decorators import versioned, translated, sourced
from complex_fields.models import ComplexField, ComplexFieldContainer


class Person(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ComplexFieldContainer(self, PersonName)
        self.alias = ComplexFieldContainer(self, PersonAlias)
        self.deathdate = ComplexFieldContainer(self, PersonDeathDate)
        self.complex_fields = [self.name, self.alias, self.deathdate]

    def get_value(self):
        return self.name.get_value()

    @classmethod
    def from_id(cls, id_):
        try:
            person = cls.objects.get(id=id_)
            return person
        except cls.DoesNotExist:
            return None

    def validate(self, dict_values, lang):
        errors = {}
        for field in self.complex_fields:
            field_name = field.get_field_str_id()

            if field_name not in dict_values and field_name in self.required_fields:
                errors[field_name] = "This field is required"
            elif field_name in dict_values:
                sources = dict_values[field_name].get('sources', [])
                import ipdb; ipdb.set_trace()
                (error, value) = field.validate(dict_values[field_name]['value'], lang, sources)
                if error is not None:
                    errors[field_name] = error
                else:
                    dict_values[field_name]['value'] = value

        return (dict_values, errors)


    def update(self, dict_values, lang=get_language()):
        (dict_values, errors) = self.validate(dict_values, lang)
        if len(errors):
            return errors

        self.save()
        for field in self.complex_fields:
            field_name = field.get_field_str_id()

            if field_name in dict_values:
                sources = Source.create_sources(dict_values[field_name].get('sources', []))
                field.update(dict_values[field_name]['value'], lang, sources)

    @classmethod
    def create(cls, dict_values, lang=get_language()):
        person = cls()
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
@sourced
class PersonDeathDate(ComplexField):
    object_ref = models.ForeignKey('Person')
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("Death date")

