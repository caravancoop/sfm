from django.contrib.gis.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import get_language

from complex_fields.model_decorators import (versioned, translated, sourced,
                                             sourced_optional)
from complex_fields.models import ComplexField, ComplexFieldContainer
from source.models import Source

class Area(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ComplexFieldContainer(self, AreaName)
        self.code = ComplexFieldContainer(self, AreaCode)
        self.geoname = ComplexFieldContainer(self, AreaGeoName)
        self.geometry = ComplexFieldContainer(self, AreaGeometry)

        self.complex_fields = [self.name, self.code, self.geoname, self.geometry]

        self.required_fields = [
            "Area_AreaName",
        ]

    @classmethod
    def from_id(cls, id_):
        try:
            area = cls.objects.get(id=id_)
            return area
        except cls.DoesNotExist:
            return None

    def validate(self, dict_values, lang):
        errors = {}
        for field in self.complex_fields:
            field_name = field.get_field_str_id()

            if ((field_name not in dict_values or
                    dict_values[field_name]['value'] == ""
                    ) and field_name in self.required_fields):
                errors[field_name] = "This field is required"
            elif field_name in dict_values and dict:
                sources = dict_values[field_name].get('sources', [])

                (error, value) = field.validate(dict_values[field_name]['value'],
                                                lang, sources)
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
        area = cls()
        errors = area.update(dict_values, lang)

        return errors


@translated
@versioned
@sourced
class AreaName(ComplexField):
    object_ref = models.ForeignKey('Area')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Name")

@versioned
@sourced_optional
class AreaGeometry(ComplexField):
    object_ref = models.ForeignKey('Area')
    value = models.PolygonField(default=None, blank=True, null=True)
    objects = models.GeoManager()
    field_name = _("Location geometry")

@versioned
@sourced
class AreaCode(ComplexField):
    object_ref = models.ForeignKey('Area')
    value = models.ForeignKey('Code', default=None, blank=True, null=True)
    field_name = _("Classification")

@versioned
@sourced
class AreaGeoName(ComplexField):
    object_ref = models.ForeignKey('Area')
    value = models.IntegerField(default=None, blank=True, null=True)
    field_name = _("GeoName ID")

class Code(models.Model):
    value = models.TextField()
