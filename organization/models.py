import uuid

from django.db import models
from django.contrib.gis import geos
from django.utils.translation import ugettext as _
from django.db.models import Max

from django_date_extensions.fields import ApproximateDateField

from complex_fields.model_decorators import versioned, translated, sourced, sourced_optional
from complex_fields.models import ComplexField, ComplexFieldContainer, ComplexFieldListContainer
from complex_fields.base_models import BaseModel


class Organization(models.Model, BaseModel):
    
    uuid = models.UUIDField(default=uuid.uuid4, 
                            editable=False, 
                            db_index=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ComplexFieldContainer(self, OrganizationName)
        self.aliases = ComplexFieldListContainer(self, OrganizationAlias)
        self.classification = ComplexFieldListContainer(self, OrganizationClassification)
        self.division_id = ComplexFieldContainer(self, OrganizationDivisionId)

        self.complex_fields = [self.name, self.division_id]

        self.required_fields = [
            "Organization_OrganizationName",
        ]

    def get_value(self):
        return self.name.get_value()

    def __str__(self):
        return str(self.name)

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
    value = models.ForeignKey('Alias', default=None, blank=True, null=True)
    
    field_name = _("Alias")

class Alias(models.Model):
    value = models.TextField()
    
    def __str__(self):
        return self.value

@versioned
@sourced
class OrganizationClassification(ComplexField):
    object_ref = models.ForeignKey('Organization')
    value = models.ForeignKey('Classification', default=None, blank=True,
                              null=True)
    field_name = _("Classification")


class Classification(models.Model):
    value = models.TextField()

    def __str__(self):
        return self.value

@versioned
@sourced
class OrganizationDivisionId(ComplexField):
    object_ref = models.ForeignKey('Organization')
    value = models.TextField(default=None, blank=True, null=True)

    field_name = _("Division ID")

    def __str__(self):
        return self.value

