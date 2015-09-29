from django.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import get_language

from django_date_extensions.fields import ApproximateDateField

from source.models import Source
from organization.models import Organization, Classification
from complex_fields.model_decorators import versioned, translated, sourced
from complex_fields.models import ComplexField, ComplexFieldContainer


class Composition(models.Model):
    def __init__(self, *args, **kwargs):
        self.parent = ComplexFieldContainer(self, OrganizationCompositionParent)
        self.child = ComplexFieldContainer(self, OrganizationCompositionChild)
        self.startdate = ComplexFieldContainer(self, OrganizationCompositionStartDate)
        self.enddate = ComplexFieldContainer(self, OrganizationCompositionEndDate)
        self.classification = ComplexFieldContainer(self, OrganizationCompositionClassification)


@versioned
@sourced
class CompositionParent(ComplexField):
    object_ref = models.ForeignKey(Organization)
    value = models.ForeignKey(Organization, related_name='child_organization')
    field_name = _("Child organization")

@versioned
@sourced
class CompositionChild(ComplexField):
    object_ref = models.ForeignKey(Organization)
    value = models.ForeignKey(Organization, related_name='parent_organization')
    field_name = _("Parent organization")

@versioned
@sourced
class CompositionStartDate(ComplexField):
    object_ref = models.ForeignKey(Organization)
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("Start date")

@versioned
@sourced
class CompositionEndDate(ComplexField):
    object_ref = models.ForeignKey(Organization)
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("End date")

@versioned
@sourced
class CompositionClassification(ComplexField):
    object_ref = models.ForeignKey(Organization)
    value = models.ForeignKey(Classification, default=None, blank=True,
                              null=True)
    field_name = _("Classification")
