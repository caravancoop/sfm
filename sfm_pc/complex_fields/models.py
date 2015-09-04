import inspect
import reversion
import re

from django.db import models
from django.core.exceptions import ValidationError, FieldDoesNotExist
from django.utils.translation import get_language
from source.models import Source


class ComplexField(models.Model):
    lang = models.CharField(max_length=5, null=False)
    sources = models.ManyToManyField(Source, related_name="%(app_label)s_%(class)s_related")

    class Meta:
        abstract = True
        unique_together = ('object', 'lang')

    def revert(self, id):
        if hasattr(self, 'versioned'):
            version = reversion.get_for_object(self).get(id=id)
            version.revert()

class ComplexFieldContainer(object):
    def __init__(self, table_object, field_model):
        self.table_object = table_object
        self.field_model = field_model
        if hasattr(field_model(), 'field_name'):
            self.field_name = field_model().field_name
        self.sourced = hasattr(field_model(), 'sourced')
        self.translated = hasattr(field_model(), 'translated')
        self.versioned = hasattr(field_model(), 'versioned')

    def __str__(self):
        value = self.get_value(get_language())
        if value is None:
            value = ""
        return value

    def get_attr_name(self):
        table_name = self.table_object.__class__.__name__
        return re.sub(table_name, '', self.field_model.__name__).lower()

    def get_object_name(self):
        return self.table_object.__class__.__name__.lower()

    def get_field_str_id(self):
        table_name = self.table_object.__class__.__name__
        field_name = self.field_model.__name__
        return table_name + "_" + field_name

    def get_value(self, lang=get_language()):
        c_fields = self.field_model.objects.filter(object=self.table_object)
        if hasattr(self.field_model, 'translated'):
            c_fields_lang = c_fields.filter(lang=lang)
            c_field = list(c_fields_lang[:1])

            if not c_field:
                c_fields = c_fields.filter(lang='en')
                c_field = list(c_fields[:1])
        else:
            c_field = list(c_fields[:1])

        if c_field:
            return c_field[0].value
        return None

    def set_value(self, value, lang=get_language()):
        c_fields = self.field_model.objects.filter(object=self.table_object)
        if hasattr(self.field_model, 'translated'):
            c_fields = c_fields.filter(lang=lang)
        field = list(c_fields[:1])
        if field:
            field[0].value = value
            field[0].save()
        else:
            new_field = self.field_model()
            if hasattr(self.field_model, 'translated'):
                new_field.lang = lang
            new_field.value = value
            new_field.save()

    def get_history(self):
        c_fields = self.field_model.objects.filter(object=self.table_object)
        history = {}
        for c_field in c_fields:
            field_history = reversion.get_for_object(c_field)
            history[c_field.lang] = [
                {
                    'value': fh.field_dict['value'],
                    'sources': fh.field_dict['sources'],
                    'id': fh.id
                }
                for fh in field_history
            ]
        return history

    def revert_field(self, lang_ids):
        c_fields = self.field_model.objects.filter(object=self.table_object)
        for field in c_fields:
            if field.lang in lang_ids:
                field.revert(lang_ids[field.lang])

    def get_sources(self):
        sources = []
        if not hasattr(self.field_model, 'sourced'):
            return sources

        c_fields = self.field_model.objects.filter(object=self.table_object)
        field = list(c_fields[:1])
        if field:
            sources = field[0].sources.all()

        return sources

    def update(self, value, lang, sources=[]):
        c_fields = self.field_model.objects.filter(object=self.table_object)

        for field in c_fields:
            field.value = None
            if hasattr(field, 'sourced'):
                for source in sources:
                    field.sources.clear()
            field.save()
        c_field = c_fields.filter(lang=lang)
        c_field = list(c_field[:1])
        if not c_field:
            if self.translated:
                c_field = self.field_model(object=self.table_object, lang=lang)
            else:
                c_field = self.field_model(object=self.table_object)
        else:
            c_field = c_field[0]

        c_field.value = value
        c_field.save()

        if hasattr(c_field, 'sourced'):
            for src in sources:
                c_field.sources.add(src)

    def translate(self, value, lang):
        c_fields = self.field_model.objects.filter(object=self.table_object)

        if not c_fields.exists():
            raise FieldDoesNotExist("Can't translate a field that doesn't exist")

        c_field = c_fields.filter(lang=lang)
        c_field = list(c_field[:1])
        if not c_field:
            c_field = self.field_model(object=self.table_object, lang=lang)
        else:
            c_field = c_field[0]
            if c_field.value != None:
                raise ValidationError("Can't translate an already translated field")

        c_field.value = value
        c_field.save()

        if hasattr(c_field, 'sourced'):
            with_sources = self.field_model.objects.exclude(sources=None)
            sources = with_sources[0].sources.all()
            for src in sources:
                c_field.sources.add(src)

        c_field.save()
