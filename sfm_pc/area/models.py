from django.contrib.gis.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from django.contrib.gis import geos

from complex_fields.model_decorators import (versioned, translated, sourced,
                                             sourced_optional)
from complex_fields.models import ComplexField, ComplexFieldContainer
from complex_fields.base_models import BaseModel
from source.models import Source

class Area(models.Model, BaseModel):
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

    def get_value(self):
        return self.name.get_value()

    def __str__(self):
        return self.name.get_value()

    @classmethod
    def from_id(cls, id_):
        try:
            area = cls.objects.get(id=id_)
            return area
        except cls.DoesNotExist:
            return None

    def validate(self, dict_values):
        errors = {}

        coordinates = dict_values['Area_AreaGeometry'].get("value")
        if coordinates:
            try:
                poly = geos.fromstr(coordinates)
                if not isinstance(poly, geos.Polygon):
                    errors["Area_AreaGeometry"] = (
                        "The geometry must be a polygon, not a point"
                    )
            except TypeError:
                errors["Area_AreaGeometry"] = (
                    "Invalid data for a polygon"
                )

        (base_errors, values) = super().validate(dict_values)
        errors.update(base_errors)

        return (errors, values)


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

    @classmethod
    def from_id(cls, id_):
        try:
            code = cls.objects.get(id=id_)
            return code
        except cls.DoesNotExist:
            return None
