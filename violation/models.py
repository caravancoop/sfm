import uuid

import reversion

from django.contrib.gis.db import models
from django.utils.translation import ugettext as _
from django.db.models import Max
from django.contrib.gis import geos
from django.core.urlresolvers import reverse

from django_date_extensions.fields import ApproximateDateField

from complex_fields.model_decorators import versioned, translated, sourced, sourced_optional
from complex_fields.models import ComplexField, ComplexFieldContainer, ComplexFieldListContainer
from complex_fields.base_models import BaseModel
from source.models import Source
from person.models import Person
from organization.models import Organization
from sfm_pc.utils import VersionsMixin
from location.models import Location


VERSION_RELATED_FIELDS = [
    'violationadminlevel1_set',
    'violationadminlevel2_set',
    'violationdescription_set',
    'violationdivisionid_set',
    'violationenddate_set',
    'violationfirstallegation_set',
    'violationlastupdate_set',
    'violationlocation_set',
    'violationlocationdescription_set',
    'violationlocationid_set',
    'violationlocationname_set',
    'violationosmid_set',
    'violationosmname_set',
    'violationperpetrator_set',
    'violationperpetratorclassification_set',
    'violationperpetratororganization_set',
    'violationstartdate_set',
    'violationstatus_set',
    'violationtype_set'
]


@reversion.register(follow=VERSION_RELATED_FIELDS)
class Violation(models.Model, BaseModel, VersionsMixin):
    uuid = models.UUIDField(default=uuid.uuid4,
                            editable=False,
                            db_index=True)

    published = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dates and status
        self.startdate = ComplexFieldContainer(self, ViolationStartDate)
        self.first_allegation = ComplexFieldContainer(self, ViolationFirstAllegation)
        self.enddate = ComplexFieldContainer(self, ViolationEndDate)
        self.last_update = ComplexFieldContainer(self, ViolationLastUpdate)
        self.status = ComplexFieldContainer(self, ViolationStatus)

        # Location fields
        self.locationdescription = ComplexFieldContainer(
            self, ViolationLocationDescription
        )
        self.adminlevel1 = ComplexFieldContainer(self, ViolationAdminLevel1)
        self.adminlevel2 = ComplexFieldContainer(self, ViolationAdminLevel2)
        self.osmname = ComplexFieldContainer(self, ViolationOSMName)
        self.osmid = ComplexFieldContainer(self, ViolationOSMId)
        self.division_id = ComplexFieldContainer(self, ViolationDivisionId)
        self.location = ComplexFieldContainer(self, ViolationLocation)
        self.location_name = ComplexFieldContainer(self, ViolationLocationName)
        self.location_id = ComplexFieldContainer(self, ViolationLocationId)

        # Descriptions and other attributes
        self.description = ComplexFieldContainer(self, ViolationDescription)
        self.perpetrator = ComplexFieldListContainer(self, ViolationPerpetrator)
        self.perpetratororganization = ComplexFieldListContainer(
            self, ViolationPerpetratorOrganization
        )
        self.perpetratorclassification = ComplexFieldContainer(
            self, ViolationPerpetratorClassification
        )
        self.types = ComplexFieldListContainer(self, ViolationType)

        self.complex_fields = [
            self.startdate, self.first_allegation, self.enddate, self.last_update,
            self.status, self.locationdescription, self.adminlevel1, self.adminlevel2,
            self.location, self.description, self.division_id
        ]

        self.complex_lists = [
            self.perpetrator, self.perpetratororganization,
            self.perpetratorclassification, self.types
        ]

        self.required_fields = [self.description, self.startdate, self.enddate]

    def get_value(self):
        return self.description.get_value()

    @property
    def related_entities(self):
        """
        Return a list of dicts with metadata for all of the entities linked to
        this Violation.

        Metadata dicts must have the following keys:
            - name
            - entity_type
            - url (a link to edit the entity)
        """
        related_entities = []

        # Second-highest administrative level for the location of the violation.
        if self.adminlevel1.get_value():
            location = self.adminlevel1.get_value().value
            related_entities.append({
                'name': location.name,
                'entity_type': _('AdminLevel1'),
                'url': reverse('edit-violation', args=[self.uuid])
            })

        # Highest administrative level for the location of the violation.
        if self.adminlevel2.get_value():
            location = self.adminlevel2.get_value().value
            related_entities.append({
                'name': location.name,
                'entity_type': _('AdminLevel2'),
                'url': reverse('edit-violation', args=[self.uuid])
            })

        # The location of the violation.
        if self.location.get_value():
            location = self.location.get_value().value
            related_entities.append({
                'name': location.name,
                'entity_type': _('Location'),
                'url': reverse('edit-violation', args=[self.uuid])
            })

        # The perpetrators of the violation (personnel).
        perpetrators = self.perpetrator.get_list()
        if perpetrators:
            perpetrators = [perp.get_value() for perp in perpetrators if perp.get_value()]
            for perpetrator in perpetrators:
                person = perpetrator.value
                related_entities.append({
                    'name': person.name.get_value().value,
                    'entity_type': _('Perpetrator'),
                    'url': reverse('edit-violation', args=[self.uuid])
                })

        # The perpetrators of the violation (organizations).
        perpetratororganizations = self.perpetratororganization.get_list()
        if perpetratororganizations:
            perpetrators = [perp.get_value() for perp in perpetratororganizations
                            if perp.get_value()]
            for perpetrator in perpetrators:
                org = perpetrator.value
                related_entities.append({
                    'name': org.name.get_value().value,
                    'entity_type': _('PerpetratorOrganization'),
                    'url': reverse('edit-violation', args=[self.uuid])
                })

        return related_entities


@versioned
class ViolationStartDate(ComplexField):
    object_ref = models.ForeignKey('Violation')
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("Start date")


@versioned
class ViolationFirstAllegation(ComplexField):
    object_ref = models.ForeignKey('Violation')
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("First allegation")


@versioned
class ViolationEndDate(ComplexField):
    object_ref = models.ForeignKey('Violation')
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("End date")


@versioned
class ViolationLastUpdate(ComplexField):
    object_ref = models.ForeignKey('Violation')
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("Last update")


@translated
@versioned
class ViolationStatus(ComplexField):
    object_ref = models.ForeignKey('Violation')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Current status")


@translated
@versioned
class ViolationLocationDescription(ComplexField):
    object_ref = models.ForeignKey('Violation')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Location description")


@versioned
class ViolationAdminLevel1(ComplexField):
    object_ref = models.ForeignKey('Violation')
    value = models.ForeignKey(Location, null=True)
    field_name = _("Admin level 1")


@versioned
class ViolationAdminLevel2(ComplexField):
    object_ref = models.ForeignKey('Violation')
    value = models.ForeignKey(Location, null=True)
    field_name = _("Admin level 2")


@versioned
class ViolationOSMName(ComplexField):
    object_ref = models.ForeignKey('Violation')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("OSM Name")


@versioned
class ViolationOSMId(ComplexField):
    object_ref = models.ForeignKey('Violation')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("OSM ID")


@versioned
class ViolationDivisionId(ComplexField):
    object_ref = models.ForeignKey('Violation')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Division ID")


@versioned
class ViolationLocation(ComplexField):
    object_ref = models.ForeignKey('Violation')
    value = models.ForeignKey(Location, null=True)
    field_name = _("Location")


@versioned
class ViolationLocationName(ComplexField):
    object_ref = models.ForeignKey('Violation')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Exact location name")


@versioned
class ViolationLocationId(ComplexField):
    object_ref = models.ForeignKey('Violation')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Exact location ID")


@versioned
@sourced
class ViolationDescription(ComplexField):
    object_ref = models.ForeignKey('Violation')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Description")


@versioned
class ViolationPerpetrator(ComplexField):
    object_ref = models.ForeignKey('Violation')
    value = models.ForeignKey(Person, default=None, blank=True, null=True)
    field_name = _("Perpetrator")


@versioned
class ViolationPerpetratorOrganization(ComplexField):
    object_ref = models.ForeignKey('Violation')
    value = models.ForeignKey(Organization, default=None, blank=True, null=True)
    field_name = _("Perpetrating unit")


@versioned
@translated
class ViolationType(ComplexField):
    object_ref = models.ForeignKey('Violation', null=True)
    value = models.TextField(blank=True, null=True)
    field_name = _("Violation type")


@versioned
@translated
class ViolationPerpetratorClassification(ComplexField):
    object_ref = models.ForeignKey('Violation', null=True)
    value = models.TextField(blank=True, null=True)
    field_name = _("Perpetrating unit classification")
