from django.db import models
from django.contrib.gis import geos
from django.utils.translation import ugettext as _
from django.db.models import Max

from django_date_extensions.fields import ApproximateDateField

from complex_fields.model_decorators import versioned, translated, sourced, sourced_optional
from complex_fields.models import ComplexField, ComplexFieldContainer
from complex_fields.base_models import BaseModel


class Organization(models.Model, BaseModel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ComplexFieldContainer(self, OrganizationName)
        self.alias = ComplexFieldContainer(self, OrganizationAlias)
        self.classification = ComplexFieldContainer(self, OrganizationClassification)
        self.foundingdate = ComplexFieldContainer(self, OrganizationFoundingDate)
        self.dissolutiondate = ComplexFieldContainer(self, OrganizationDissolutionDate)
        self.realfounding = ComplexFieldContainer(self, OrganizationRealFounding)
        self.realdissolution = ComplexFieldContainer(self, OrganizationRealDissolution)

        self.complex_fields = [self.name, self.alias, self.classification,
                               self.foundingdate, self.dissolutiondate,
                               self.realfounding, self.realdissolution]

        self.required_fields = [
            "Organization_OrganizationName",
        ]

    def get_value(self):
        return self.name.get_value()

    def __str__(self):
        return str(self.name)

    @classmethod
    def search(cls, terms):
        order_by = terms.get('orderby')
        if not order_by:
            order_by = 'organizationname__value'

        direction = terms.get('direction')
        if not direction:
            direction = 'ASC'

        dirsym = ''
        if direction == 'DESC':
            dirsym = '-'

        orgs_query = (Organization.objects
                      .annotate(Max(order_by))
                      .order_by(dirsym + order_by + "__max"))

        name = terms.get('name')
        if name:
            orgs_query = orgs_query.filter(organizationname__value__icontains=name)

        alias_val = terms.get('alias')
        if alias_val:
            orgs_query = orgs_query.filter(organizationalias__value__icontains=alias_val)

        foundingdate_year = terms.get('founding_year')
        if foundingdate_year:
            orgs_query = orgs_query.filter(
                organizationfoundingdate__value__startswith=foundingdate_year
            )

        foundingdate_month = terms.get('founding_month')
        if foundingdate_month:
            orgs_query = orgs_query.filter(
                organizationfoundingdate__value__contains="-" + foundingdate_month + "-"
            )

        foundingdate_day = terms.get('founding_day')
        if foundingdate_day:
            orgs_query = orgs_query.filter(
                organizationfoundingdate__value__endswith=foundingdate_day
            )

        dissolutiondate_year = terms.get('dissolution_year')
        if dissolutiondate_year:
            orgs_query = orgs_query.filter(
                organizationdissolutiondate__value__startswith=dissolutiondate_year
            )

        dissolutiondate_month = terms.get('dissolution_month')
        if dissolutiondate_month:
            orgs_query = orgs_query.filter(
                organizationdissolutiondate__value__contains="-" + dissolutiondate_month + "-"
            )

        dissolutiondate_day = terms.get('dissolution_day')
        if dissolutiondate_day:
            orgs_query = orgs_query.filter(
                organizationdissolutiondate__value__endswith=dissolutiondate_day
            )

        classification = terms.get('classification')
        if classification:
            orgs_query = orgs_query.filter(organizationclassification__value_id=classification)

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
                orgs_query = orgs_query.filter(
                    associationorganization__object_ref__associationarea__value__areageometry__value__dwithin=(point, radius)
                )
            else:
                orgs_query = orgs_query.filter(
                    associationorganization__object_ref__associationarea__value__areageometry__value__bbcontains=point
                )

        return orgs_query


@translated
@versioned
@sourced
class OrganizationName(ComplexField):
    object_ref = models.ForeignKey('Organization')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Name")


@translated
@versioned
@sourced
class OrganizationAlias(ComplexField):
    object_ref = models.ForeignKey('Organization')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Alias")


@versioned
@sourced
class OrganizationClassification(ComplexField):
    object_ref = models.ForeignKey('Organization')
    value = models.ForeignKey('Classification', default=None, blank=True,
                              null=True)
    field_name = _("Classification")


@versioned
@sourced
class OrganizationFoundingDate(ComplexField):
    object_ref = models.ForeignKey('Organization')
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("Date of creation")


@versioned
@sourced
class OrganizationDissolutionDate(ComplexField):
    object_ref = models.ForeignKey('Organization')
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("Date of disbandment")


@versioned
@sourced_optional
class OrganizationRealFounding(ComplexField):
    object_ref = models.ForeignKey('Organization')
    value = models.BooleanField(default=False)
    field_name = _("Real creation")


@versioned
@sourced_optional
class OrganizationRealDissolution(ComplexField):
    object_ref = models.ForeignKey('Organization')
    value = models.BooleanField(default=False)
    field_name = _("Real dissolution")


class Classification(models.Model):
    value = models.TextField()

    def __str__(self):
        return self.value
