from django.contrib.gis.db import models

from django.utils.translation import ugettext as _
from django.utils.translation import get_language

from complex_fields.model_decorators import (versioned, translated, sourced,
                                             sourced_optional)
from complex_fields.models import ComplexField, ComplexFieldContainer
from source.models import Source

class Site(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ComplexFieldContainer(self, SiteName)
        self.adminlevel1 = ComplexFieldContainer(self, SiteAdminLevel1)
        self.adminlevel2 = ComplexFieldContainer(self, SiteAdminLevel2)
        self.coordinates = ComplexFieldContainer(self, SiteCoordinates)
        self.geoname = ComplexFieldContainer(self, SiteGeoname)
        self.geonameid = ComplexFieldContainer(self, SiteGeonameId)


@translated
@versioned
@sourced
class SiteName(ComplexField):
    object_ref = models.ForeignKey('Site')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Name")

@versioned
@sourced
class SiteAdminLevel1(ComplexField):
    object_ref = models.ForeignKey('Site')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Admin level 1")

@versioned
@sourced
class SiteAdminLevel2(ComplexField):
    object_ref = models.ForeignKey('Site')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Admin level 2")

@versioned
@sourced
class SiteCoordinates(ComplexField):
    object_ref = models.ForeignKey('Site')
    value = models.PointField(default=None, blank=True, null=True)
    field_name = _("Coordinates")

@versioned
@sourced
class SiteGeoname(ComplexField):
    object_ref = models.ForeignKey('Site')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("GeoName name")

@versioned
@sourced
class SiteGeonameId(ComplexField):
    object_ref = models.ForeignKey('Site')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("GeoName ID")
