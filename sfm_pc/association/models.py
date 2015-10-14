from django.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import get_language

from django_date_extensions.fields import ApproximateDateField

from complex_fields.model_decorators import versioned, sourced
from complex_fields.models import ComplexField, ComplexFieldContainer
from source.models import Source
from organization.models import Organization
from area.models import Area

class Association(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.startdate = ComplexFieldContainer(self, AssociationStartDate)
        self.enddate = ComplexFieldContainer(self, AssociationEndDate)
        self.organization = ComplexFieldContainer(self, AssociationOrganization)
        self.area = ComplexFieldContainer(self, AssociationArea)

        self.complex_fields = [self.startdate, self.enddate, self.organization,
                               self.area]

        self.required_fields = [
            "Association_AssociationOrganization",
            "Association_AssociationArea",
        ]

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

@versioned
class AssociationArea(ComplexField):
    object_ref = models.ForeignKey('Association')
    value = models.ForeignKey(Area)
    field_name = _("Area")

