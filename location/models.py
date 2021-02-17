from django.db import models
from django.contrib.gis.db.models.fields import GeometryField
from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.template.defaultfilters import truncatewords
from django.utils.translation import ugettext as _


class LocationManager(models.Manager):

    def from_humane_id(self, humane_id):
        return self.get(**{'sfm__location:humane_id:admin': humane_id})


class Location(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    division_id = models.TextField(blank=True, null=True)
    feature_type = models.TextField(blank=True, null=True)
    tags = JSONField(blank=True, null=True)
    sfm = JSONField(blank=True, null=True)
    adminlevel1 = models.ForeignKey('self',
                                    related_name='area_locations',
                                    null=True,
                                    blank=True)
    adminlevel2 = models.ForeignKey('self',
                                    related_name='place_locations',
                                    null=True,
                                    blank=True)
    adminlevel = models.CharField(max_length=50, null=True, blank=True)
    geometry = GeometryField(blank=True, null=True)

    objects = LocationManager()

    def __str__(self):
        if self.name is None:
            return str(self.id)
        return self.name

    @property
    def related_entities(self):
        """
        Return a list of dicts with metadata for all of the entities (Organizations
        and Violations) linked to this Location via an Emplacement or Association.

        Metadata dicts must have the following keys:
            - name
            - entity_type
            - start_date
            - end_date
            - open_ended
            - url (a link to edit the entity)
        """
        related_entities = []

        for associationarea in self.associationarea_set.all():
            association = associationarea.object_ref
            organization = association.organization.get_value().value
            related_entities.append({
                'name': organization.name.get_value().value,
                'entity_type': _('Organization'),
                'start_date': association.startdate.get_value(),
                'end_date': association.enddate.get_value(),
                'open_ended': association.open_ended.get_value(),
                'url': reverse('view-organization', kwargs={'slug': organization.uuid}),
            })

        for emplacementsite in self.emplacementsite_set.all():
            emplacement = emplacementsite.object_ref
            organization = emplacement.organization.get_value().value
            related_entities.append({
                'name': organization.name.get_value().value,
                'entity_type': _('Organization'),
                'start_date': emplacement.startdate.get_value(),
                'end_date': emplacement.enddate.get_value(),
                'open_ended': emplacement.open_ended.get_value(),
                'url': reverse('view-organization', kwargs={'slug': organization.uuid}),
            })

        for violationlocation in self.violationlocation_set.all():
            violation = violationlocation.object_ref
            related_entities.append({
                'name': truncatewords(violation.description.get_value(), 10),
                'entity_type': _('Violation'),
                'start_date': violation.startdate.get_value(),
                'end_date': violation.enddate.get_value(),
                'open_ended': '',
                'url': reverse('view-violation', kwargs={'slug': violation.uuid}),
            })

        return related_entities
