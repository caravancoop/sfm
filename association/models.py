from django.db import models
from django.utils.translation import ugettext as _
from django.conf import settings

from django_date_extensions.fields import ApproximateDateField

from complex_fields.model_decorators import versioned, sourced, sourced_optional
from complex_fields.models import ComplexField, ComplexFieldContainer
from complex_fields.base_models import BaseModel
from organization.models import Organization
from location.models import Location
from sfm_pc.models import GetComplexFieldNameMixin, SuperlativeDateMixin
from source.mixins import SourcesMixin


class Association(models.Model, BaseModel, SourcesMixin, SuperlativeDateMixin, GetComplexFieldNameMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.startdate = ComplexFieldContainer(self, AssociationStartDate)
        self.realstart = ComplexFieldContainer(self, AssociationRealStart)

        self.enddate = ComplexFieldContainer(self, AssociationEndDate)
        self.open_ended = ComplexFieldContainer(self, AssociationOpenEnded)

        self.organization = ComplexFieldContainer(self, AssociationOrganization)
        self.area = ComplexFieldContainer(self, AssociationArea)


        self.complex_fields = [self.startdate, self.realstart, self.enddate,
                               self.open_ended, self.organization, self.area]

        self.complex_lists = []

        self.required_fields = [
            "Association_AssociationOrganization",
            "Association_AssociationArea",
        ]

    def get_value(self):
        return '{0} {1}'.format(self.area, self.organization)

    def __str__(self):
        return self.get_value()


class AssociationTenure(models.Model):
    association = models.ForeignKey('Association', on_delete=models.CASCADE)
    startdate = models.ForeignKey('AssociationStartDate', blank=True, null=True, on_delete=models.CASCADE)
    enddate = models.ForeignKey('AssociationEndDate', blank=True, null=True, on_delete=models.CASCADE)


@versioned
@sourced
class AssociationStartDate(ComplexField):
    object_ref = models.ForeignKey('Association', on_delete=models.CASCADE)
    value = ApproximateDateField()
    field_name = _("First Cited Date")
    shortcode = 'u_locfcd'
    spreadsheet_field_name = 'unit:location_first_cited_date'


@versioned
@sourced_optional
class AssociationRealStart(ComplexField):
    object_ref = models.ForeignKey('Association', on_delete=models.CASCADE)
    value = models.NullBooleanField(default=None)
    field_name = _("Is Foundation Date?")
    shortcode = 'u_locfcd_f'
    spreadsheet_field_name = 'unit:location_first_cited_date_founding'


@versioned
@sourced
class AssociationEndDate(ComplexField):
    object_ref = models.ForeignKey('Association', on_delete=models.CASCADE)
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("Last Cited Date")
    shortcode = 'u_loclcd'
    spreadsheet_field_name = 'unit:location_last_cited_date'


@versioned
@sourced
class AssociationOrganization(ComplexField):
    object_ref = models.ForeignKey('Association', on_delete=models.CASCADE)
    value = models.ForeignKey(Organization, on_delete=models.CASCADE)
    field_name = _("Unit")

    def __str__(self):
        return str(self.value)


@versioned
@sourced
class AssociationArea(ComplexField):
    object_ref = models.ForeignKey('Association', on_delete=models.CASCADE)
    value = models.ForeignKey(Location, on_delete=models.CASCADE)
    field_name = _("Area of Operation")

    def __str__(self):
        return str(self.value)


@versioned
@sourced_optional
class AssociationOpenEnded(ComplexField):
    object_ref = models.ForeignKey('Association', on_delete=models.CASCADE)
    value = models.CharField(default='N', max_length=1, choices=settings.OPEN_ENDED_CHOICES)
    field_name = _("Open-Ended?")
    shortcode = 'u_loclcd_o'
    spreadsheet_field_name = 'unit:location_open'
