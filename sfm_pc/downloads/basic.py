from collections import OrderedDict

from django.conf import settings
from django.db import models
from django.contrib.postgres import fields as pg_fields
from django_date_extensions.fields import ApproximateDateField

from .base import BaseDownload
from organization.models import Organization


class BasicDownload(BaseDownload):
    # Class metadata
    download_type = 'basic'

    # Download fields
    org_id = models.UUIDField(primary_key=True)
    name = models.TextField()
    name_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    name_confidence = models.CharField(max_length=1)
    division_id = models.TextField()
    division_id_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    division_id_confidence = models.CharField(max_length=1)
    classifications = pg_fields.ArrayField(models.TextField(), default=list)
    classifications_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    classifications_confidence = models.CharField(max_length=1)
    aliases = pg_fields.ArrayField(models.TextField(), default=list)
    aliases_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    aliases_confidence = models.CharField(max_length=1)
    firstciteddate = ApproximateDateField()
    firstciteddate_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    firstciteddate_confidence = models.CharField(max_length=1)
    lastciteddate = ApproximateDateField()
    lastciteddate_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    lastciteddate_confidence = models.CharField(max_length=1)
    realstart = models.NullBooleanField(default=None)
    realstart_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    realstart_confidence = models.CharField(max_length=1)
    open_ended = models.CharField(max_length=1, default='N', choices=settings.OPEN_ENDED_CHOICES)
    open_ended_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    open_ended_confidence = models.CharField(max_length=1)

    @classmethod
    def _get_field_map(cls):
        """
        Return metadata for each field defined on this model, to aid in serializing
        and exporing data.
        """
        return OrderedDict([
            ('org_id', {
                'sql': 'organization.uuid',
                'label': 'unit:id:admin',
                'serializer': cls.serializers['string'],
            }),
            ('name', {
                'sql': 'organization.name',
                'label': Organization.get_spreadsheet_field_name('name'),
                'serializer': cls.serializers['identity'],
            }),
            ('name_sources', {
                'sql': 'organization.name_sources',
                'label': Organization.get_spreadsheet_source_field_name('name'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('name_confidence', {
                'sql': 'organization.name_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('name'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('division_id', {
                'sql': 'organization.division_id',
                'label': Organization.get_spreadsheet_field_name('division_id'),
                'serializer': cls.serializers['division_id'],
            }),
            ('division_id_sources', {
                'sql': 'organization.division_id_sources',
                'label': Organization.get_spreadsheet_source_field_name('division_id'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('division_id_confidence', {
                'sql': 'organization.division_id_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('division_id'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('classifications', {
                'sql': 'organization.classifications',
                'label': Organization.get_spreadsheet_field_name('classification'),
                'serializer': cls.serializers['list'],
            }),
            ('classifications_sources', {
                'sql': 'organization.classifications_sources',
                'label': Organization.get_spreadsheet_source_field_name('classification'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('classifications_confidence', {
                'sql': 'organization.classifications_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('classification'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('aliases', {
                'sql': 'organization.aliases',
                'label': Organization.get_spreadsheet_field_name('aliases'),
                'serializer': cls.serializers['list'],
            }),
            ('aliases_sources', {
                'sql': 'organization.aliases_sources',
                'label': Organization.get_spreadsheet_source_field_name('aliases'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('aliases_confidence', {
                'sql': 'organization.aliases_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('aliases'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('firstciteddate', {
                'sql': 'organization.first_cited_date',
                'label': Organization.get_spreadsheet_field_name('firstciteddate'),
                'serializer': cls.serializers['identity'],
            }),
            ('firstciteddate_sources', {
                'sql': 'organization.first_cited_date_sources',
                'label': Organization.get_spreadsheet_source_field_name('firstciteddate'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('firstciteddate_confidence', {
                'sql': 'organization.first_cited_date_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('firstciteddate'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('lastciteddate', {
                'sql': 'organization.last_cited_date',
                'label': Organization.get_spreadsheet_field_name('lastciteddate'),
                'serializer': cls.serializers['identity'],
            }),
            ('lastciteddate_sources', {
                'sql': 'organization.last_cited_date_sources',
                'label': Organization.get_spreadsheet_source_field_name('lastciteddate'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('lastciteddate_confidence', {
                'sql': 'organization.last_cited_date_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('lastciteddate'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('realstart', {
                'sql': 'organization.real_start',
                'label': Organization.get_spreadsheet_field_name('realstart'),
                'serializer': cls.serializers['identity'],
            }),
            ('realstart_sources', {
                'sql': 'organization.real_start_sources',
                'label': Organization.get_spreadsheet_source_field_name('realstart'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('realstart_confidence', {
                'sql': 'organization.real_start_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('realstart'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('open_ended', {
                'sql': 'organization.open_ended',
                'label': Organization.get_spreadsheet_field_name('open_ended'),
                'serializer': cls.serializers['identity'],
            }),
            ('open_ended_sources', {
                'sql': 'organization.open_ended_sources',
                'label': Organization.get_spreadsheet_source_field_name('open_ended'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('open_ended_confidence', {
                'sql': 'organization.open_ended_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('open_ended'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
        ])
