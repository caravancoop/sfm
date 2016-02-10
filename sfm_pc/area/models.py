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
        self.geoname = ComplexFieldContainer(self, AreaGeoName)
        self.geometry = ComplexFieldContainer(self, AreaGeometry)

        self.complex_fields = [self.name, self.code, self.geoname, self.geometry]

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

    @classmethod
    def search(cls, terms):
        order_by = terms.get('orderby')
        if not order_by:
            order_by = 'areaname__value'
        elif order_by in ['name']:
            order_by = 'area' + order_by + '__value'

        direction = terms.get('direction')
        if not direction:
            direction = 'ASC'

        dirsym = ''
        if direction == 'DESC':
            dirsym = '-'

        area_query = (Area.objects
                      .annotate(Max(order_by))
                      .order_by(dirsym + order_by + "__max"))


        name = terms.get('name')
        if name:
            area_query = area_query.filter(areaname__value__icontains=name)

        code = terms.get('classification')
        if code:
            area_query = area_query.filter(areacode__value=code)

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
                area_query = area_query.filter(
                    areageometry__value__dwithin=(point, radius)
                )
            else:
                area_query = area_query.filter(
                   areageometry__value__bbcontains=point
                )

        return area_query


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

    def __str__(self):
        return self.value
