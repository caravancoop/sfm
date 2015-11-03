from django.contrib.gis.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import get_language

from django_date_extensions.fields import ApproximateDateField

from complex_fields.model_decorators import (versioned, translated, sourced)
from complex_fields.models import ComplexField, ComplexFieldContainer, ComplexFieldListContainer
from complex_fields.base_models import BaseModel
from source.models import Source

CONFIDENCE_LEVELS = (
    ('1', _('Low')),
    ('2', _('Medium')),
    ('3', _('High')),
)

class Violation(models.Model, BaseModel):
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

        self.required_fields = []

        self.types = ComplexFieldListContainer(self, ViolationType)
        self.sources = models.ManyToManyField(Source)
        self.confidence = models.CharField(max_length=1, default=1,
                                           choices=CONFIDENCE_LEVELS)

    def validate(self, dict_values):
        errors = {}

        start = dict_values['Violation_ViolationStartDate']
        end = dict_values['Violation_ViolationEndDate']
        if (start and start.get('value') and end and end.get('value') and
                start.get('value') >= end.get('value')):
            errors['Violation_ViolationStartDate'] = _(
                "The start date must be before the end date"
            )

        (base_errors, values) = super().validate(dict_values)
        errors.update(base_errors)

        return (errors, values)


class ViolationStartDate(models.Model):
    object_ref = models.ForeignKey('Violation')
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("Start date")

class ViolationEndDate(models.Model):
    object_ref = models.ForeignKey('Violation')
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("End date")

@translated
class ViolationLocationDescription(ComplexField):
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
