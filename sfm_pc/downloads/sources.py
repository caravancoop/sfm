from collections import OrderedDict

from django.db import models
from django_date_extensions.fields import ApproximateDateField

from .base import BaseDownload
from source.models import Source, AccessPoint


class SourceDownload(BaseDownload):
    # Class metadata
    download_type = 'sources'

    # Download fields
    source_id = models.UUIDField(primary_key=True)
    source_title = models.TextField()
    source_type = models.TextField()
    source_author = models.TextField()
    source_publication = models.TextField()
    source_publication_country = models.TextField()
    source_published_date = ApproximateDateField()
    source_published_timestamp = models.DateTimeField()
    source_created_date = ApproximateDateField()
    source_created_timestamp = models.DateTimeField()
    source_uploaded_date = ApproximateDateField()
    source_uploaded_timestamp = models.DateTimeField()
    source_source_url = models.URLField()
    access_point_id = models.UUIDField()
    access_point_type = models.TextField()
    access_point_trigger = models.TextField()
    access_point_accessed_on = models.DateField()
    access_point_archive_url = models.URLField()

    @classmethod
    def _get_field_map(cls):
        """
        Return metadata for each field defined on this model, to aid in serializing
        and exporing data.
        """
        return OrderedDict([
            ('source_id', {
                'sql': 'source.uuid',
                'label': 'source:id:admin',
                'serializer': cls.serializers['identity'],
            }),
            ('source_title', {
                'sql': 'source.title',
                'label': Source.get_spreadsheet_field_name('title'),
                'serializer': cls.serializers['identity'],
            }),
            ('source_type', {
                'sql': 'source.type',
                'label': Source.get_spreadsheet_field_name('type'),
                'serializer': cls.serializers['identity'],
            }),
            ('source_author', {
                'sql': 'source.author',
                'label': Source.get_spreadsheet_field_name('author'),
                'serializer': cls.serializers['identity'],
            }),
            ('source_publication', {
                'sql': 'source.publication',
                'label': Source.get_spreadsheet_field_name('publication'),
                'serializer': cls.serializers['identity'],
            }),
            ('source_publication_country', {
                'sql': 'source.publication_country',
                'label': Source.get_spreadsheet_field_name('publication_country'),
                'serializer': cls.serializers['identity'],
            }),
            ('source_published_date', {
                'sql': "COALESCE(source.published_date, to_char(source.published_timestamp, 'YYYY-MM-DD HH12:MI:SS'))",
                'label': Source.get_spreadsheet_field_name('published_date'),
                'serializer': cls.serializers['identity'],
            }),
            ('source_created_date', {
                'sql': "COALESCE(source.created_date, to_char(source.created_timestamp, 'YYYY-MM-DD HH12:MI:SS'))",
                'label': Source.get_spreadsheet_field_name('created_date'),
                'serializer': cls.serializers['identity'],
            }),
            ('source_uploaded_date', {
                'sql': "COALESCE(source.uploaded_date, to_char(source.uploaded_timestamp, 'YYYY-MM-DD HH12:MI:SS'))",
                'label': Source.get_spreadsheet_field_name('uploaded_date'),
                'serializer': cls.serializers['identity'],
            }),
            ('source_source_url', {
                'sql': 'source.source_url',
                'label': Source.get_spreadsheet_field_name('source_url'),
                'serializer': cls.serializers['identity'],
            }),
            ('access_point_id', {
                'sql': 'access_point.uuid',
                'label': 'source:access_point_id',
                'serializer': cls.serializers['identity'],
            }),
            ('access_point_type', {
                'sql': 'access_point.type',
                'label': AccessPoint.get_spreadsheet_field_name('type'),
                'serializer': cls.serializers['identity'],
            }),
            ('access_point_trigger', {
                'sql': 'access_point.trigger',
                'label': AccessPoint.get_spreadsheet_field_name('trigger'),
                'serializer': cls.serializers['identity'],
            }),
            ('access_point_accessed_on', {
                'sql': 'access_point.accessed_on',
                'label': AccessPoint.get_spreadsheet_field_name('accessed_on'),
                'serializer': cls.serializers['identity'],
            }),
            ('access_point_archive_url', {
                'sql': 'access_point.archive_url',
                'label': AccessPoint.get_spreadsheet_field_name('archive_url'),
                'serializer': cls.serializers['identity'],
            }),
        ])
