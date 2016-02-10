from django.contrib.gis.db import models
from django.utils.translation import ugettext as _
from django.db.models import Max
from django.contrib.gis import geos

from django_date_extensions.fields import ApproximateDateField

from complex_fields.model_decorators import translated
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
        self.adminlevel2 = ComplexFieldContainer(self, ViolationAdminLevel2)
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

    @classmethod
    def search(cls, terms):
        order_by = terms.get('orderby')
        if not order_by:
            order_by = 'violationstartdate__value'
        elif order_by in ['startdate']:
            order_by = 'violation' + order_by + '__value'

        direction = terms.get('direction')
        if not direction:
            direction = 'ASC'

        dirsym = ''
        if direction == 'DESC':
            dirsym = '-'

        violation_query = (Violation.objects
                        .annotate(Max(order_by))
                        .order_by(dirsym + order_by + "__max"))

        startdate_year = terms.get('startdate_year')
        if startdate_year:
            violation_query = violation_query.filter(
                violationstartdate__value__startswith=startdate_year
            )

        startdate_month = terms.get('startdate_month')
        if startdate_month:
            violation_query = violation_query.filter(
                violationstartdate__value__contains="-" + startdate_month + "-"
            )

        startdate_day = terms.get('startdate_day')
        if startdate_day:
            violation_query = violation_query.filter(
                violationstartdate__value__endswith=startdate_day
            )

        enddate_year = terms.get('enddate_year')
        if enddate_year:
            violation_query = violation_query.filter(
                violationenddate__value__startswith=enddate_year
            )

        enddate_month = terms.get('enddate_month')
        if enddate_month:
            violation_query = violation_query.filter(
                violationenddate__value__contains="-" + enddate_month + "-"
            )

        enddate_day = terms.get('enddate_day')
        if enddate_day:
            violation_query = violation_query.filter(
                violationenddate__value__endswith=enddate_day
            )

        admin1 = terms.get('adminlevel1')
        if admin1:
            violation_query = violation_query.filter(
                violationadminlevel1__value__icontains=admin1
            )

        admin2 = terms.get('adminlevel2')
        if admin2:
            violation_query = violation_query.filter(
                violationadminlevel2__value__icontains=admin2
            )

        loc_desc = terms.get('locationdescription')
        if loc_desc:
            violation_query = violation_query.filter(
                violationlocationdescription__value__icontains=loc_desc
            )

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
                violation_query = violation_query.filter(
                    violationlocation__value__dwithin=(point, radius)
                )
            else:
                violation_query = violation_query.filter(
                   violationlocation__value__bbcontains=point
                )

        geoname = terms.get('geoname')
        if geoname:
            violation_query = violation_query.filter(
                violationgeoname__value__icontains=geoname
            )

        geonameid = terms.get('geonameid')
        if geonameid:
            violation_query = violation_query.filter(violationgeonameid__value=geonameid)

        source = terms.get('source')
        if source:
            violation_query = violation_query.filter(
                violationsource__source__source__icontains=source
            )

        v_type = terms.get('v_type')
        if v_type:
            violation_query = violation_query.filter(
                violationtype__value__code__icontains=v_type
            )

        viol_descr = terms.get('description')
        if viol_descr:
            violation_query = violation_query.filter(
                violationdescription__value__icontains=viol_descr
            )

        perpetrator = terms.get('perpetrator')
        if perpetrator:
            violation_query = violation_query.filter(
                violationperpetrator__value__icontains=perpetrator
            )

        perpetratororganization = terms.get('perpetratororganization')
        if perpetratororganization:
            violation_query = violation_query.filter(
                violationperpetratororganization__value__icontains=perpetratororganization
            )

        return violation_query

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
