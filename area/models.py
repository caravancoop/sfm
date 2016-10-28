from django.contrib.gis.db import models
from django.utils.translation import ugettext as _
from django.contrib.gis import geos
from django.db.models import Max

from complex_fields.model_decorators import (versioned, translated, sourced,
                                             sourced_optional)
from complex_fields.models import ComplexField, ComplexFieldContainer
from complex_fields.base_models import BaseModel


class Area(models.Model, BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ComplexFieldContainer(self, AreaName)
        self.code = ComplexFieldContainer(self, AreaCode)
        self.geoname = ComplexFieldContainer(self, AreaGeoname)
        self.geonameid = ComplexFieldContainer(self, AreaGeonameId)
        self.geometry = ComplexFieldContainer(self, AreaGeometry)
        self.division_id = ComplexFieldContainer(self, AreaDivisionId)

        self.complex_fields = [self.name, self.code, self.geoname, 
                               self.geometry, self.division_id]

        self.required_fields = [
            "Area_AreaName",
        ]

    def get_value(self):
        return self.name.get_value()

    def __str__(self):
        return str(self.name)

    @classmethod
    def from_id(cls, id_):
        try:
            area = cls.objects.get(id=id_)
            return area
        except cls.DoesNotExist:
            return None


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
class AreaGeoname(ComplexField):
    object_ref = models.ForeignKey('Area')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Geoname name")

@versioned
@sourced
class AreaGeonameId(ComplexField):
    object_ref = models.ForeignKey('Area')
    value = models.IntegerField(default=None, blank=True, null=True)
    field_name = _("Geoname id")

class Code(models.Model):
    value = models.TextField()

    @classmethod
    def from_id(cls, id_):
        try:
            code = cls.objects.get(id=id_)
            return code
        except cls.DoesNotExist:
            return None

    def __str__(self):
        return self.value

@versioned
@sourced
class AreaDivisionId(ComplexField):
    object_ref = models.ForeignKey('Area')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Division ID")
