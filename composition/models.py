from django.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from django.db.models import Max

from django_date_extensions.fields import ApproximateDateField

from organization.models import Organization, Classification
from complex_fields.model_decorators import versioned, sourced
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

    @classmethod
    def search(cls, terms):
        order_by = terms.get('orderby')
        if not order_by:
            order_by = 'compositionstartdate__value'
        elif order_by in ['startdate']:
            order_by = 'composition' + order_by + '__value'

        direction = terms.get('direction')
        if not direction:
            direction = 'ASC'

        dirsym = ''
        if direction == 'DESC':
            dirsym = '-'

        composition_query = (Composition.objects
                             .annotate(Max(order_by))
                             .order_by(dirsym + order_by + "__max"))

        startdate_year = terms.get('startdate_year')
        if startdate_year:
            composition_query = composition_query.filter(
                compositionstartdate__value__startswith=startdate_year
            )

        startdate_month = terms.get('startdate_month')
        if startdate_month:
            composition_query = composition_query.filter(
                compositionstartdate__value__contains="-" + startdate_month + "-"
            )

        startdate_day = terms.get('startdate_day')
        if startdate_day:
            composition_query = composition_query.filter(
                compositionstartdate__value__endswith=startdate_day
            )

        enddate_year = terms.get('enddate_year')
        if enddate_year:
            composition_query = composition_query.filter(
                compositionenddate__value__startswith=enddate_year
            )

        enddate_month = terms.get('enddate_month')
        if enddate_month:
            composition_query = composition_query.filter(
                compositionenddate__value__contains="-" + enddate_month + "-"
            )

        enddate_day = terms.get('enddate_day')
        if enddate_day:
            composition_query = composition_query.filter(
                compositionenddate__value__endswith=enddate_day
            )

        classification = terms.get('classification')
        if classification:
            composition_query = composition_query.filter(
                compositionclassification__value_id=classification
            )

        parent = terms.get('parent')
        if parent:
            composition_query = composition_query.filter(
                compositionparent__value__organizationname__value__icontains=parent
            )

        child = terms.get('child')
        if child:
            composition_query = composition_query.filter(
                compositionchild__value__organizationname__value__icontains=child
            )

        return composition_query


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
