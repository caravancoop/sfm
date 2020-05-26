from collections import OrderedDict

from django.conf import settings
from django.db import models
from django.contrib.postgres import fields as pg_fields
from django_date_extensions.fields import ApproximateDateField

from .base import BaseDownload
from composition.models import Composition
from organization.models import Organization


class ParentageDownload(BaseDownload):
    # Class metadata
    download_type = 'parentage'

    # Download fields
    child_unit_id = models.UUIDField()
    name = models.TextField()
    name_confidence = models.CharField(max_length=1)
    division_id = models.TextField()
    division_id_confidence = models.CharField(max_length=1)
    classifications = pg_fields.ArrayField(models.TextField(), default=list)
    classifications_confidence = models.CharField(max_length=1)
    aliases = pg_fields.ArrayField(models.TextField(), default=list)
    aliases_confidence = models.CharField(max_length=1)
    firstciteddate = ApproximateDateField()
    firstciteddate_confidence = models.CharField(max_length=1)
    lastciteddate = ApproximateDateField()
    lastciteddate_confidence = models.CharField(max_length=1)
    realstart = models.NullBooleanField(default=None)
    realstart_confidence = models.CharField(max_length=1)
    open_ended = models.CharField(max_length=1, default='N', choices=settings.OPEN_ENDED_CHOICES)
    open_ended_confidence = models.CharField(max_length=1)
    related_id = models.UUIDField()
    related_id_confidence = models.CharField(max_length=1)
    related_name = models.TextField()
    related_name_confidence = models.CharField(max_length=1)
    related_division_id = models.TextField()
    related_division_id_confidence = models.CharField(max_length=1)
    related_classifications = pg_fields.ArrayField(models.TextField(), default=list)
    related_classifications_confidence = models.CharField(max_length=1)
    related_firstciteddate = ApproximateDateField()
    related_firstciteddate_confidence = models.CharField(max_length=1)
    related_lastciteddate = ApproximateDateField()
    related_lastciteddate_confidence = models.CharField(max_length=1)
    related_realstart = models.NullBooleanField(default=None)
    related_realstart_confidence = models.CharField(max_length=1)
    related_open_ended = models.CharField(max_length=1, default='N', choices=settings.OPEN_ENDED_CHOICES)
    related_open_ended_confidence = models.CharField(max_length=1)

    @classmethod
    def _get_field_map(cls):
        """
        Return metadata for each field defined on this model, to aid in serializing
        and exporing data.
        """
        return OrderedDict([
            ('child_unit_id', {
                'sql': 'child.uuid',
                'label': 'unit:id:admin',
                'serializer': cls.serializers['string'],
            }),
            ('name', {
                'sql': 'child.name',
                'label': Organization.get_spreadsheet_field_name('name'),
                'serializer': cls.serializers['identity'],
            }),
            ('name_confidence', {
                'sql': 'child.name_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('name'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('division_id', {
                'sql': 'child.division_id',
                'label': Organization.get_spreadsheet_field_name('division_id'),
                'serializer': cls.serializers['division_id'],
            }),
            ('division_id_confidence', {
                'sql': 'child.division_id_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('division_id'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('classifications', {
                'sql': 'child.classifications',
                'label': Organization.get_spreadsheet_field_name('classification'),
                'serializer': cls.serializers['list'],
            }),
            ('classifications_confidence', {
                'sql': 'child.classifications_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('classification'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('aliases', {
                'sql': 'child.aliases',
                'label': Organization.get_spreadsheet_field_name('aliases'),
                'serializer': cls.serializers['list'],
            }),
            ('aliases_confidence', {
                'sql': 'child.aliases_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('aliases'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('firstciteddate', {
                'sql': 'child.first_cited_date',
                'label': Organization.get_spreadsheet_field_name('firstciteddate'),
                'serializer': cls.serializers['identity'],
            }),
            ('firstciteddate_confidence', {
                'sql': 'child.first_cited_date_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('firstciteddate'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('lastciteddate', {
                'sql': 'child.last_cited_date',
                'label': Organization.get_spreadsheet_field_name('lastciteddate'),
                'serializer': cls.serializers['identity'],
            }),
            ('lastciteddate_confidence', {
                'sql': 'child.last_cited_date_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('lastciteddate'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('realstart', {
                'sql': 'child.real_start',
                'label': Organization.get_spreadsheet_field_name('realstart'),
                'serializer': cls.serializers['identity'],
            }),
            ('realstart_confidence', {
                'sql': 'child.real_start_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('realstart'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('open_ended', {
                'sql': 'child.open_ended',
                'label': Organization.get_spreadsheet_field_name('open_ended'),
                'serializer': cls.serializers['identity'],
            }),
            ('open_ended_confidence', {
                'sql': 'child.open_ended_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('open_ended'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('related_id', {
                'sql': 'parent.uuid',
                'label': Composition.get_spreadsheet_field_name('parent'),
                'serializer': cls.serializers['string'],
            }),
            ('related_id_confidence', {
                'sql': "composition_parent_metadata.confidence",
                'label': Composition.get_spreadsheet_confidence_field_name('parent'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('related_name', {
                'sql': 'parent.name',
                'label': Composition.get_spreadsheet_field_name('parent') + ':name',
                'serializer': cls.serializers['identity'],
            }),
            ('related_name_confidence', {
                'sql': 'parent.name_confidence',
                'label': Composition.get_spreadsheet_field_name('parent') + ':name:confidence',
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('related_division_id', {
                'sql': 'parent.division_id',
                'label': Composition.get_spreadsheet_field_name('parent') + ':country',
                'serializer': cls.serializers['division_id'],
            }),
            ('related_division_id_confidence', {
                'sql': 'parent.division_id_confidence',
                'label': Composition.get_spreadsheet_field_name('parent') + ':country:confidence',
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('related_classifications', {
                'sql': 'composition.classifications',
                'label': Composition.get_spreadsheet_field_name('classification'),
                'serializer': cls.serializers['list'],
            }),
            ('related_classifications_confidence', {
                'sql': 'composition.classifications_confidence',
                'label': Composition.get_spreadsheet_confidence_field_name('classification'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('related_firstciteddate', {
                'sql': 'composition.first_cited_date',
                'label': Composition.get_spreadsheet_field_name('startdate'),
                'serializer': cls.serializers['identity'],
            }),
            ('related_firstciteddate_confidence', {
                'sql': 'composition.first_cited_date_confidence',
                'label': Composition.get_spreadsheet_confidence_field_name('startdate'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('related_realstart', {
                'sql': 'composition.real_start',
                'label': Composition.get_spreadsheet_field_name('realstart'),
                'serializer': cls.serializers['identity'],
            }),
            ('related_realstart_confidence', {
                'sql': 'composition.real_start_confidence',
                'label': Composition.get_spreadsheet_confidence_field_name('realstart'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('related_lastciteddate', {
                'sql': 'composition.last_cited_date',
                'label': Composition.get_spreadsheet_field_name('enddate'),
                'serializer': cls.serializers['identity'],
            }),
            ('related_lastciteddate_confidence', {
                'sql': 'composition.last_cited_date_confidence',
                'label': Composition.get_spreadsheet_confidence_field_name('enddate'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('related_open_ended', {
                'sql': 'composition.open_ended',
                'label': Composition.get_spreadsheet_field_name('open_ended'),
                'serializer': cls.serializers['identity'],
            }),
            ('related_open_ended_confidence', {
                'sql': 'composition.open_ended_confidence',
                'label': Composition.get_spreadsheet_confidence_field_name('open_ended'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
        ])
