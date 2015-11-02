from django.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import get_language

from django_date_extensions.fields import ApproximateDateField

from source.models import Source
from organization.models import Organization, Classification
from complex_fields.model_decorators import versioned, translated, sourced
from complex_fields.models import ComplexField, ComplexFieldContainer
from complex_fields.base_models import BaseModel


class Composition(models.Model, BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = ComplexFieldContainer(self, CompositionParent)
        self.child = ComplexFieldContainer(self, CompositionChild)
        self.startdate = ComplexFieldContainer(self, CompositionStartDate)
        self.enddate = ComplexFieldContainer(self, CompositionEndDate)
        self.classification = ComplexFieldContainer(self, CompositionClassification)

        self.complex_fields = [self.parent, self.child, self.startdate,
                               self.enddate, self.classification]

        self.required_fields = [
            "Composition_CompositionParent", "Composition_CompositionChild"
        ]

    def validate(self, dict_values, lang=get_language()):
        errors = {}

        parent = dict_values.get("Composition_CompositionParent")
        child = dict_values.get("Composition_CompositionChild")
        if (parent and parent.get("value") and child and child.get("value") and
            parent.get("value") == child.get("value")):
            errors["Composition_CompositionParent"] = ("The parent and the child" +
                " organizations must be differents")

        start = dict_values.get("Composition_CompositionStartDate")
        end = dict_values.get("Composition_CompositionEndDate")
        if (start and start.get("value") != "" and end and
            end.get("value") != "" and start.get("value") >= end.get("value")):
            errors["Composition_CompositionStartDate"] = (
                "The start date must be before the end date"
            )

        (base_errors, values) = super().validate(dict_values)
        errors.update(base_errors)

        return (errors, values)

@versioned
@sourced
class CompositionParent(ComplexField):
    object_ref = models.ForeignKey(Composition)
    value = models.ForeignKey(Organization, related_name='child_organization')
    field_name = _("Parent organization")

@versioned
@sourced
class CompositionChild(ComplexField):
    object_ref = models.ForeignKey(Composition)
    value = models.ForeignKey(Organization, related_name='parent_organization')
    field_name = _("Child organization")

@versioned
@sourced
class CompositionStartDate(ComplexField):
    object_ref = models.ForeignKey(Composition)
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("Start date")

@versioned
@sourced
class CompositionEndDate(ComplexField):
    object_ref = models.ForeignKey(Composition)
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("End date")

@versioned
@sourced
class CompositionClassification(ComplexField):
    object_ref = models.ForeignKey(Composition)
    value = models.ForeignKey(Classification, default=None, blank=True,
                              null=True)
    field_name = _("Classification")
