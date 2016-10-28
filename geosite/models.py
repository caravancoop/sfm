import json

from django.contrib.gis.db import models

from django.utils.translation import ugettext as _
from django.db.models import Max
from django.contrib.gis import geos

from complex_fields.model_decorators import versioned, translated, sourced
from complex_fields.models import ComplexField, ComplexFieldContainer
from complex_fields.base_models import BaseModel


class Geosite(models.Model, BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ComplexFieldContainer(self, GeositeName)
        self.adminlevel1 = ComplexFieldContainer(self, GeositeAdminLevel1)
        self.adminlevel2 = ComplexFieldContainer(self, GeositeAdminLevel2)
        self.coordinates = ComplexFieldContainer(self, GeositeCoordinates)
        self.geoname = ComplexFieldContainer(self, GeositeGeoname)
        self.geonameid = ComplexFieldContainer(self, GeositeGeonameId)
        self.division_id = ComplexFieldContainer(self, GeositeDivisionId)

        self.complex_fields = [self.name, self.adminlevel1, self.adminlevel2,
                               self.coordinates, self.geoname, self.geonameid, 
                               self.division_id]

        self.required_fields = ["Geosite_GeositeName"]

    def get_value(self):
        return self.name.get_value()

    def __str__(self):
        return str(self.name)


@translated
@versioned
@sourced
class GeositeName(ComplexField):
    object_ref = models.ForeignKey('Geosite')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Name")


@versioned
@sourced
class GeositeAdminLevel1(ComplexField):
    object_ref = models.ForeignKey('Geosite')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Admin level 1")


@versioned
@sourced
class GeositeAdminLevel2(ComplexField):
    object_ref = models.ForeignKey('Geosite')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Admin level 2")


@versioned
@sourced
class GeositeCoordinates(ComplexField):
    object_ref = models.ForeignKey('Geosite')
    value = models.PointField(default=None, blank=True, null=True)
    objects = models.GeoManager()
    field_name = _("Coordinates")


@versioned
@sourced
class GeositeGeoname(ComplexField):
    object_ref = models.ForeignKey('Geosite')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("GeoName name")


@versioned
@sourced
class GeositeGeonameId(ComplexField):
    object_ref = models.ForeignKey('Geosite')
    value = models.IntegerField(default=None, blank=True, null=True)
    field_name = _("GeoName ID")

@versioned
@sourced
class GeositeDivisionId(ComplexField):
    object_ref = models.ForeignKey('Geosite')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Division ID")
