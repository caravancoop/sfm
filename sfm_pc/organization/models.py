from django.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from source.models import Source

from complex_fields.model_decorators import versioned, translated, sourced
from complex_fields.models import ComplexField, ComplexFieldContainer


class Organization(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ComplexFieldContainer(self, OrganizationName)
        self.alias = ComplexFieldContainer(self, OrganizationAlias)
        self.classification = ComplexFieldContainer(self, OrganizationClassification)
        self.founding_date = ComplexFieldContainer(self, OrganizationFoundingDate)
        self.dissolution_date = ComplexFieldContainer(self, OrganizationDissolutionDate)
        self.real_founding = ComplexFieldContainer(self, OrganizationRealFounding)
        self.real_dissolution = ComplexFieldContainer(self, OrganizationRealDissolution)

        self.complex_fields = [self.name, self.alias, self.classification,
                               self.founding_date, self.dissolution_date,
                               self.real_founding, self.real_dissolution]

    @classmethod
    def create(cls, dict_values, lang=get_language()):
        org = cls()
        org.save()
        org.update(dict_values, lang)
        return org


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
    value = models.DateField(default=None, blank=True, null=True)
    field_name = _("Date of creation")


@versioned
@sourced
class OrganizationDissolutionDate(ComplexField):
    object_ref = models.ForeignKey('Organization')
    value = models.DateField(default=None, blank=True, null=True)
    field_name = _("Date of disbandment")


@versioned
class OrganizationRealFounding(ComplexField):
    object_ref = models.ForeignKey('Organization')
    value = models.BooleanField(default=None)
    field_name = _("Real creation")


@versioned
class OrganizationRealDissolution(ComplexField):
    object_ref = models.ForeignKey('Organization')
    value = models.BooleanField(default=None)
    field_name = _("Real dissolution")


class Classification(models.Model):
    value = models.TextField()
