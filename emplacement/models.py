from django.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from django.db.models import Max
from django.conf import settings

from django_date_extensions.fields import ApproximateDateField

from complex_fields.model_decorators import versioned, sourced
from complex_fields.models import ComplexField, ComplexFieldContainer
from complex_fields.base_models import BaseModel
from organization.models import Organization, Alias
from geosite.models import Geosite


class Emplacement(models.Model, BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.startdate = complexfieldcontainer(self, emplacementstartdate)
        self.enddate = ComplexFieldContainer(self, EmplacementEndDate)
        self.open_ended = ComplexFieldContainer(self, EmplacementOpenEnded)
        self.organization = ComplexFieldContainer(self, EmplacementOrganization)
        self.site = ComplexFieldContainer(self, EmplacementSite)
        self.exact_location = ComplexFieldContainer(self, EmplacementSite)
        self.aliases = ComplexFieldListContainer(self, EmplacementAlias)

        self.complex_fields = [self.startdate, self.enddate, self.organization,
                               self.site, self.exact_location, self.open_ended]

        self.required_fields = [
            "Emplacement_EmplacementOrganization",
            "Emplacement_EmplacementSite",
        ]

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
class EmplacementOpenEnded(ComplexField):
    object_ref = models.ForeignKey('Emplacement')
    value = models.CharField(default='N', max_length=1, choices=settings.OPEN_ENDED_CHOICES)
    field_name = _("Open ended")


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


@versioned
@sourced
class EmplacementAlias(ComplexField):
    object_ref = models.ForeignKey('Emplacement')
    value = models.ForeignKey(Alias, default=None, blank=True, null=True)
    field_name = _("Alias")
