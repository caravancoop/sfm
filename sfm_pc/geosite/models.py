import json

from django.contrib.gis.db import models

from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from django.contrib.gis.geos import Point

from complex_fields.model_decorators import (versioned, translated, sourced,
                                             sourced_optional)
from complex_fields.models import ComplexField, ComplexFieldContainer
from complex_fields.base_models import BaseModel
from source.models import Source

class Geosite(models.Model, BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ComplexFieldContainer(self, GeositeName)
        self.adminlevel1 = ComplexFieldContainer(self, GeositeAdminLevel1)
        self.adminlevel2 = ComplexFieldContainer(self, GeositeAdminLevel2)
        self.coordinates = ComplexFieldContainer(self, GeositeCoordinates)
        self.geoname = ComplexFieldContainer(self, GeositeGeoname)
        self.geonameid = ComplexFieldContainer(self, GeositeGeonameId)

        self.complex_fields = [self.name, self.adminlevel1, self.adminlevel2,
                               self.coordinates, self.geoname, self.geonameid]

        self.required_fields = ["Geosite_GeositeName"]

    def get_value(self):
        return self.name.get_value()

    def __str__(self):
        return self.name.get_value()

    def validate(self, dict_values):
        errors = {}

        coordinates = dict_values['Geosite_GeositeCoordinates'].get("value")
        if coordinates:
            coord = json.loads(coordinates).get("coordinates")
            if coord:
                try:
                    Point(coord)
                except TypeError:
                    errors["Geosite_GeositeCoordinates"] = (
                        "The coordinates must be a point, not a polygon"
                    )

        (base_errors, values) = super().validate(dict_values)
        errors.update(base_errors)

        return (errors, values)


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
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("GeoName ID")
