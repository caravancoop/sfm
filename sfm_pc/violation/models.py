from django.contrib.gis.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import get_language

from django_date_extensions.fields import ApproximateDateField

from complex_fields.model_decorators import (versioned, translated, sourced)
from complex_fields.models import ComplexField, ComplexFieldContainer, ComplexFieldListContainer
from source.models import Source

class Violation(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.startdate = ComplexFieldContainer(self, ViolationStartDate)
        self.enddate = ComplexFieldContainer(self, ViolationEndDate)
        self.locationdescription = ComplexFieldContainer(
            self, ViolationLocationDescription
        )
        self.adminlevel1 = ComplexFieldContainer(self, ViolationAdminLevel1)
        self.adminlevel2 = ComplexFieldContainer(self, ViolationAdminLevel1)
        self.geoname = ComplexFieldContainer(self, ViolationGeoname)
        self.geonameid = ComplexFieldContainer(self, ViolationGeonameId)
        self.location = ComplexFieldContainer(self, ViolationLocation)
        self.description = ComplexFieldContainer(self, ViolationDescription)
        self.perpetrator = ComplexFieldContainer(self, ViolationPerpetrator)
        self.perpetratororganization = ComplexFieldContainer(
            self, ViolationPerpetratorOrganization
        )

        self.complex_fields = [self.startdate, self.enddate, self.locationdescription,
                               self.adminlevel1, self.adminlevel2, self.geoname,
                               self.geonameid, self.location, self.description,
                               self.perpetrator, self.perpetratororganization]

        self.types = ComplexFieldListContainer(self, ViolationType)

    @classmethod
    def create(cls, dict_values, lang=get_language()):
        violation = cls()
        return violation

class ViolationStartDate(models.Model):
    object_ref = models.ForeignKey('Violation')
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("Start date")

class ViolationEndDate(models.Model):
    object_ref = models.ForeignKey('Violation')
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("End date")

@translated
class ViolationLocationDescription(models.Model):
    object_ref = models.ForeignKey('Violation')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Location description")

class ViolationAdminLevel1(models.Model):
    object_ref = models.ForeignKey('Violation')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Admin level 1")

class ViolationAdminLevel2(models.Model):
    object_ref = models.ForeignKey('Violation')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Admin level 2")

class ViolationGeoname(models.Model):
    object_ref = models.ForeignKey('Violation')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("GeoName name")

class ViolationGeonameId(models.Model):
    object_ref = models.ForeignKey('Violation')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("GeoName ID")

class ViolationLocation(models.Model):
    object_ref = models.ForeignKey('Violation')
    value = models.PointField(default=None, blank=True, null=True)
    field_name = _("Location")

class ViolationDescription(models.Model):
    object_ref = models.ForeignKey('Violation')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Description")

class ViolationPerpetrator(models.Model):
    object_ref = models.ForeignKey('Violation')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Perpetrator")

class ViolationPerpetratorOrganization(models.Model):
    object_ref = models.ForeignKey('Violation')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Perpetrator Organization")

class ViolationSource(models.Model):
    violation = models.ForeignKey('Violation')
    source = models.ForeignKey(Source)

class ViolationType(models.Model):
    object_ref = models.ForeignKey('Violation')
    value = models.ForeignKey('Type', default=None, blank=True, null=True)

class Type(models.Model):
    code = models.TextField()
