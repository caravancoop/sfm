from django.db import models
from django.utils.translation import ugettext as _

from django_date_extensions.fields import ApproximateDateField

from complex_fields.model_decorators import versioned, sourced
from complex_fields.models import ComplexField, ComplexFieldContainer
from complex_fields.base_models import BaseModel
from organization.models import Organization
from area.models import Area


class Association(models.Model, BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.startdate = ComplexFieldContainer(self, AssociationStartDate)
        self.enddate = ComplexFieldContainer(self, AssociationEndDate)
        self.organization = ComplexFieldContainer(self, AssociationOrganization)
        self.area = ComplexFieldContainer(self, AssociationArea)
        
        self.open_ended = ComplexFieldContainer(self, AssociationOpenEnded)

        self.complex_fields = [self.startdate, self.enddate, self.organization,
                               self.area, self.open_ended]

        self.required_fields = [
            "Association_AssociationOrganization",
            "Association_AssociationArea",
        ]

    def get_value(self):
        return '{0} {1}'.format(self.area, self.organization)

    def __str__(self):
        return self.get_value()


@versioned
@sourced
class AssociationStartDate(ComplexField):
    object_ref = models.ForeignKey('Association')
    value = ApproximateDateField()
    field_name = _("Start date")


@versioned
@sourced
class AssociationEndDate(ComplexField):
    object_ref = models.ForeignKey('Association')
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("End date")


@versioned
@sourced
class AssociationOrganization(ComplexField):
    object_ref = models.ForeignKey('Association')
    value = models.ForeignKey(Organization)
    field_name = _("Organization")

    def __str__(self):
        return str(self.value)


@versioned
@sourced
class AssociationArea(ComplexField):
    object_ref = models.ForeignKey('Association')
    value = models.ForeignKey(Area)
    field_name = _("Area")

    def __str__(self):
        return str(self.value)

@versioned
class AssociationOpenEnded(ComplexField):
    object_ref = models.ForeignKey('Association')
    value = models.NullBooleanField(default=None, blank=True, null=True)
    field_name = _("Open ended")
