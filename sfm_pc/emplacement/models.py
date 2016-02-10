from django.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from django.db.models import Max

from django_date_extensions.fields import ApproximateDateField

from complex_fields.model_decorators import versioned, sourced
from complex_fields.models import ComplexField, ComplexFieldContainer
from complex_fields.base_models import BaseModel
from organization.models import Organization
from geosite.models import Geosite

class Emplacement(models.Model, BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.startdate = ComplexFieldContainer(self, EmplacementStartDate)
        self.enddate = ComplexFieldContainer(self, EmplacementEndDate)
        self.organization = ComplexFieldContainer(self, EmplacementOrganization)
        self.site = ComplexFieldContainer(self, EmplacementSite)

        self.complex_fields = [self.startdate, self.enddate, self.organization,
                               self.site]

        self.required_fields = [
            "Emplacement_EmplacementOrganization",
            "Emplacement_EmplacementSite",
        ]

    def validate(self, dict_values, lang=get_language()):
        errors = {}

        start = dict_values.get("Emplacement_EmplacementStartDate")
        end = dict_values.get("Emplacement_EmplacementEndDate")
        if (start and start.get("value") != "" and
                end and end.get("value") != "" and
                start.get("value") >= end.get("value")):
            errors['Emplacement_EmplacementStartDate'] = _(
                "The start date must be before the end date"
            )

        (base_errors, values) = super().validate(dict_values)
        errors.update(base_errors)

        return (errors, values)


    @classmethod
    def search(cls, terms):
        order_by = terms.get('orderby')
        if not order_by:
            order_by = 'emplacementstartdate__value'
        elif order_by in ['startdate']:
            order_by = 'person' + order_by + '__value'

        direction = terms.get('direction')
        if not direction:
            direction = 'ASC'

        dirsym = ''
        if direction == 'DESC':
            dirsym = '-'

        emplacement_query = (Emplacement.objects
                             .annotate(Max(order_by))
                             .order_by(dirsym + order_by + "__max"))

        startdate_year = terms.get('startdate_year')
        if startdate_year:
            emplacement_query = emplacement_query.filter(
                emplacementstartdate__value__startswith=startdate_year
            )

        startdate_month = terms.get('startdate_month')
        if startdate_month:
            emplacement_query = emplacement_query.filter(
                emplacementstartdate__value__contains="-" + startdate_month + "-"
            )

        startdate_day = terms.get('startdate_day')
        if startdate_day:
            emplacement_query = emplacement_query.filter(
                emplacementstartdate__value__endswith=startdate_day
            )

        enddate_year = terms.get('enddate_year')
        if enddate_year:
            emplacement_query = emplacement_query.filter(
                emplacementenddate__value__startswith=enddate_year
            )

        enddate_month = terms.get('enddate_month')
        if enddate_month:
            emplacement_query = emplacement_query.filter(
                emplacementenddate__value__contains="-" + enddate_month + "-"
            )

        enddate_day = terms.get('enddate_day')
        if enddate_day:
            emplacement_query = emplacement_query.filter(
                emplacementenddate__value__endswith=enddate_day
            )

        organization = terms.get('organization')
        if organization:
            emplacement_query = emplacement_query.filter(
                emplacementorganization__value__organizationname__value__icontains=organization
            )

        site = terms.get('site')
        if site:
            emplacement_query = emplacement_query.filter(
                emplacementsite__value__geositename__value__icontains=site
            )

        return emplacement_query

@versioned
@sourced
class EmplacementStartDate(ComplexField):
    object_ref = models.ForeignKey('Emplacement')
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("Start date")


@versioned
@sourced
class EmplacementEndDate(ComplexField):
    object_ref = models.ForeignKey('Emplacement')
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("End date")


@versioned
@sourced
class EmplacementOrganization(ComplexField):
    object_ref = models.ForeignKey('Emplacement')
    value = models.ForeignKey(Organization)
    field_name = _("Organization")

@versioned
class EmplacementSite(ComplexField):
    object_ref = models.ForeignKey('Emplacement')
    value = models.ForeignKey(Geosite)
    field_name = _("Site")
