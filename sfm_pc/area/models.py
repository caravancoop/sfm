from django.contrib.gis.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import get_language

from complex_fields.model_decorators import versioned, translated, sourced
from complex_fields.models import ComplexField, ComplexFieldContainer

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


@translated
@versioned
@sourced
class AreaName(ComplexField):
    object_ref = models.ForeignKey('Area')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Name")

class AreaGeometry(ComplexField):
    object_ref = models.ForeignKey('Area')
    value = models.MultiPolygonField()
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
