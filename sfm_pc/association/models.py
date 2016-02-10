from django.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from django.db.models import Max

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

        self.complex_fields = [self.startdate, self.enddate, self.organization,
                               self.area]

        self.required_fields = [
            "Association_AssociationOrganization",
            "Association_AssociationArea",
        ]

    def validate(self, dict_values, lang=get_language()):
        errors = {}

        start = dict_values.get("Association_AssociationStartDate")
        end = dict_values.get("Association_AssociationEndDate")
        if (start and start.get("value") != "" and
                end and end.get("value") != "" and
                start.get("value") >= end.get("value")):
            errors['Association_AssociationStartDate'] = (
                "The start date must be before the end date"
            )

        (base_errors, values) = super().validate(dict_values)
        errors.update(base_errors)

        return (errors, values)

    @classmethod
    def search(cls, terms):
        order_by = terms.get('orderby')
        if not order_by:
            order_by = 'associationstartdate__value'
        elif order_by in ['startdate']:
            order_by = 'association' + order_by + '__value'

        direction = terms.get('direction')
        if not direction:
            direction = 'ASC'

        dirsym = ''
        if direction == 'DESC':
            dirsym = '-'

        association_query = (Association.objects
                             .annotate(Max(order_by))
                             .order_by(dirsym + order_by + "__max"))


        startdate_year = terms.get('startdate_year')
        if startdate_year:
            association_query = association_query.filter(
                associationstartdate__value__startswith=startdate_year
            )

        startdate_month = terms.get('startdate_month')
        if startdate_month:
            association_query = association_query.filter(
                associationstartdate__value__contains="-" + startdate_month + "-"
            )

        startdate_day = terms.get('startdate_day')
        if startdate_day:
            association_query = association_query.filter(
                associationstartdate__value__endswith=startdate_day
            )

        enddate_year = terms.get('enddate_year')
        if enddate_year:
            association_query = association_query.filter(
                associationenddate__value__startswith=enddate_year
            )

        enddate_month = terms.get('enddate_month')
        if enddate_month:
            association_query = association_query.filter(
                associationenddate__value__contains="-" + enddate_month + "-"
            )

        enddate_day = terms.get('enddate_day')
        if enddate_day:
            association_query = association_query.filter(
                associationenddate__value__endswith=enddate_day
            )

        organization = terms.get('organization')
        if organization:
            association_query = association_query.filter(
                associationorganization__value__organizationname__value__icontains=organization
            )

        area = terms.get('area')
        if area:
            association_query = association_query.filter(
                associationarea__value__areaname__value__icontains=area
            )

        return association_query

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
