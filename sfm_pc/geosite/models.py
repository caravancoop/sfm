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

        self.complex_fields = [self.name, self.adminlevel1, self.adminlevel2,
                               self.coordinates, self.geoname, self.geonameid]

        self.required_fields = ["Geosite_GeositeName"]

    def get_value(self):
        return self.name.get_value()

    def __str__(self):
        return str(self.name)

    def validate(self, dict_values):
        errors = {}

        coordinates = dict_values['Geosite_GeositeCoordinates'].get("value")
        if coordinates:
            coord = json.loads(coordinates).get("coordinates")
            if coord:
                try:
                    geos.Point(coord)
                except TypeError:
                    errors["Geosite_GeositeCoordinates"] = (
                        "The coordinates must be a point, not a polygon"
                    )

        (base_errors, values) = super().validate(dict_values)
        errors.update(base_errors)

        return (errors, values)

    @classmethod
    def search(cls, terms):
        order_by = terms.get('orderby')
        if not order_by:
            order_by = 'geositename__value'
        elif order_by in ['name']:
            order_by = 'geosite' + order_by + '__value'

        direction = terms.get('direction')
        if not direction:
            direction = 'ASC'

        dirsym = ''
        if direction == 'DESC':
            dirsym = '-'

        geosite_query = (Geosite.objects
                         .annotate(Max(order_by))
                         .order_by(dirsym + order_by + "__max"))

        name = terms.get('name')
        if name:
            geosite_query = geosite_query.filter(geositename__value__icontains=name)

        admin1 = terms.get('adminlevel1')
        if admin1:
            geosite_query = geosite_query.filter(geositeadminlevel1__value__icontains=admin1)

        admin2 = terms.get('adminlevel2')
        if admin2:
            geosite_query = geosite_query.filter(geositeadminlevel2__value__icontains=admin2)

        latitude = terms.get('latitude')
        longitude = terms.get('longitude')
        if latitude and longitude:
            try:
                latitude = float(latitude)
                longitude = float(longitude)
            except ValueError:
                latitude = 0
                longitude = 0

            point = geos.Point(latitude, longitude)
            radius = terms.get('radius')
            if radius:
                try:
                    radius = float(radius)
                except ValueError:
                    radius = 0
                geosite_query = geosite_query.filter(
                    geositecoordinates__value__dwithin=(point, radius)
                )
            else:
                geosite_query = geosite_query.filter(
                    geositecoordinates__value__bbcontains=point
                )

        geoname = terms.get('geoname')
        if geoname:
            geosite_query = geosite_query.filter(geositegeoname__value__icontains=geoname)

        geonameid = terms.get('geonameid')
        if geonameid:
            geosite_query = geosite_query.filter(geositegeonameid__value=geonameid)

        return geosite_query


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
