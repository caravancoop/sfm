import uuid

import reversion

from django.contrib.gis.db import models
from django.utils.translation import ugettext as _
from django.db.models import Max
from django.contrib.gis import geos
from django.urls import reverse

from django_date_extensions.fields import ApproximateDateField

from complex_fields.model_decorators import versioned, translated, sourced, sourced_optional
from complex_fields.models import ComplexField, ComplexFieldContainer, ComplexFieldListContainer
from complex_fields.base_models import BaseModel
from source.models import Source
from person.models import Person
from organization.models import Organization
from sfm_pc.utils import VersionsMixin
from sfm_pc.models import GetComplexFieldNameMixin
from source.mixins import SourcesMixin
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
class Violation(models.Model, BaseModel, SourcesMixin, VersionsMixin, GetComplexFieldNameMixin):
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
        self.perpetratorclassification = ComplexFieldListContainer(
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
@sourced
class ViolationStartDate(ComplexField):
    object_ref = models.ForeignKey('Violation', on_delete=models.CASCADE)
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("Start Date")
    shortcode = 'i_sd'
    spreadsheet_field_name = 'incident:start_date'


@versioned
@sourced
class ViolationFirstAllegation(ComplexField):
    object_ref = models.ForeignKey('Violation', on_delete=models.CASCADE)
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("Date of Publication")
    shortcode = 'i_pd'
    spreadsheet_field_name = 'incident:pub_date'


@versioned
@sourced
class ViolationEndDate(ComplexField):
    object_ref = models.ForeignKey('Violation', on_delete=models.CASCADE)
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("End Date")
    shortcode = 'i_ed'
    spreadsheet_field_name = 'incident:end_date'


@versioned
@sourced
class ViolationLastUpdate(ComplexField):
    object_ref = models.ForeignKey('Violation', on_delete=models.CASCADE)
    value = ApproximateDateField(default=None, blank=True, null=True)
    field_name = _("Date of Last Update")
    shortcode = 'i_ud'
    spreadsheet_field_name = 'incident:update_date'


@translated
@versioned
@sourced
class ViolationStatus(ComplexField):
    object_ref = models.ForeignKey('Violation', on_delete=models.CASCADE)
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Status of Last Update")
    shortcode = 'i_us'
    spreadsheet_field_name = 'incident:update_status'


@translated
@versioned
@sourced
class ViolationLocationDescription(ComplexField):
    object_ref = models.ForeignKey('Violation', on_delete=models.CASCADE)
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Location Description")
    shortcode = 'i_ld'
    spreadsheet_field_name = 'incident:location_description'


@versioned
@sourced
class ViolationAdminLevel1(ComplexField):
    object_ref = models.ForeignKey('Violation', on_delete=models.CASCADE)
    value = models.ForeignKey(Location, null=True, on_delete=models.CASCADE)
    field_name = _("Settlement")


@versioned
@sourced
class ViolationAdminLevel2(ComplexField):
    object_ref = models.ForeignKey('Violation', on_delete=models.CASCADE)
    value = models.ForeignKey(Location, null=True, on_delete=models.CASCADE)
    field_name = _("First-Level Administrative Area")


@versioned
@sourced
class ViolationOSMName(ComplexField):
    object_ref = models.ForeignKey('Violation', on_delete=models.CASCADE)
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("OSM Name")


@versioned
@sourced
class ViolationOSMId(ComplexField):
    object_ref = models.ForeignKey('Violation', on_delete=models.CASCADE)
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("OSM ID")


@versioned
@sourced
class ViolationDivisionId(ComplexField):
    object_ref = models.ForeignKey('Violation', on_delete=models.CASCADE)
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Country")


@versioned
@sourced
class ViolationLocation(ComplexField):
    object_ref = models.ForeignKey('Violation', on_delete=models.CASCADE)
    value = models.ForeignKey(Location, null=True, on_delete=models.CASCADE)
    field_name = _("Exact Location")


@versioned
@sourced
class ViolationLocationName(ComplexField):
    object_ref = models.ForeignKey('Violation', on_delete=models.CASCADE)
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Exact Location Name")


@versioned
@sourced
class ViolationLocationId(ComplexField):
    object_ref = models.ForeignKey('Violation', on_delete=models.CASCADE)
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Exact Location ID")
    shortcode = 'i_loc'
    spreadsheet_field_name = 'incident:location'


@versioned
@sourced
class ViolationDescription(ComplexField):
    object_ref = models.ForeignKey('Violation', on_delete=models.CASCADE)
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Description")
    shortcode = 'i_vd'
    spreadsheet_field_name = 'incident:violation_description'


@versioned
@sourced
class ViolationPerpetrator(ComplexField):
    object_ref = models.ForeignKey('Violation', on_delete=models.CASCADE)
    value = models.ForeignKey(Person, default=None, blank=True, null=True, on_delete=models.CASCADE)
    field_name = _("Perpetrator")
    shortcode = 'i_ppn'
    spreadsheet_field_name = 'incident:perpetrator_person_name'


@versioned
@sourced
class ViolationPerpetratorOrganization(ComplexField):
    object_ref = models.ForeignKey('Violation', on_delete=models.CASCADE)
    value = models.ForeignKey(Organization, default=None, blank=True, null=True, on_delete=models.CASCADE)
    field_name = _("Perpetrator Unit")
    shortcode = 'i_pun'
    spreadsheet_field_name = 'incident:perpetrator_unit_name'


@versioned
@translated
@sourced
class ViolationType(ComplexField):
    object_ref = models.ForeignKey('Violation', null=True, on_delete=models.CASCADE)
    value = models.TextField(blank=True, null=True)
    field_name = _("Violation Types")
    shortcode = 'i_vt'
    spreadsheet_field_name = 'incident:violation_type'


@versioned
@translated
@sourced
class ViolationPerpetratorClassification(ComplexField):
    object_ref = models.ForeignKey('Violation', null=True, on_delete=models.CASCADE)
    value = models.TextField(blank=True, null=True)
    field_name = _("Perpetrator Classification")
    shortcode = 'i_pcl'
    spreadsheet_field_name = 'incident:perpetrator_classification'
