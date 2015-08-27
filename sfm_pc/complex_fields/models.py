import inspect
import reversion

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
    def __init__(self, table_model, field_model):
        self.table_model = table_model
        self.field_model = field_model

    def __repr__(self):
        value = self.get_value(get_language())
        if value is None:
            value = ""
        return value

    def get_value(self, lang=get_language()):
        c_fields = self.field_model.objects.filter(object=self.table_model)
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

    def get_history(self):
        c_fields = self.field_model.objects.filter(object=self.table_model)
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
        c_fields = self.field_model.objects.filter(object=self.table_model)
        for field in c_fields:
            if field.lang in lang_ids:
                field.revert(lang_ids[field.lang])

    def update(self, value, lang, sources=[]):
        c_fields = self.field_model.objects.filter(object=self.table_model)

        for field in c_fields:
            field.value = None
            if hasattr(field, 'sourced'):
                for source in sources:
                    field.sources.clear()
            field.save()
        c_field = c_fields.filter(lang=lang)
        c_field = list(c_field[:1])
        if not c_field:
            c_field = self.field_model(object=self.table_model, lang=lang)
        else:
            c_field = c_field[0]

        c_field.value = value
        c_field.save()

        if hasattr(c_field, 'sourced'):
            for src in sources:
                c_field.sources.add(src)

    def translate(self, value, lang):
        c_fields = self.field_model.objects.filter(object=self.table_model)

        if not c_fields.exists():
            raise FieldDoesNotExist("Can't translate a field that doesn't exist")

        c_field = c_fields.filter(lang=lang)
        c_field = list(c_field[:1])
        if not c_field:
            c_field = self.field_model(object=self.table_model, lang=lang)
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
