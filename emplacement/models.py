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
    
    def get_value(self):
        return '{0} ({1})'.format(self.organization.get_value(), 
                                  self.site.get_value())

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
@sourced
class EmplacementSite(ComplexField):
    object_ref = models.ForeignKey('Emplacement')
    value = models.ForeignKey(Geosite)
    field_name = _("Site")
