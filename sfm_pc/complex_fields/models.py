import inspect

from django.db import models
from django.core.exceptions import ValidationError, FieldDoesNotExist
from source.models import Source


class ComplexField(models.Model):
    lang = models.CharField(max_length=5, null=False)
    sources = models.ManyToManyField(Source, related_name="%(app_label)s_%(class)s_related")

    class Meta:
        abstract = True
        unique_together = ('object', 'lang')


class ComplexFieldContainer(object):
    def __init__(self, table_model, field_model):
        self.table_model = table_model
        self.field_model = field_model

    def get_history(self):
        c_fields = self.field_model.objects.filter(object=self.table_model)
        history = {}

        for c_field in c_fields:
            field_history = reversion.get_for_object(c_field)
            history[c_field.lang] = [
                {'value': fh.field_dict['value'], 'sources': fh.field_dict['sources'] }
                for fh in field_history
            ]
        return history

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
