import os
from collections import OrderedDict

import djqscsv
from django.conf import settings
from django.db import models, connection


class BaseDownload(models.Model):
    """
    Base class for a non-managed model that controls access to database download
    tables.

    Download tables are saved as materialized views using the *_materialized_view()
    methods on this model. These materialized views are primarily constructed using
    SQL files stored in the sql/ subdirectory of the downloads/ directory.
    """
    # The name of the download, corresponding to the SQL filename for the file
    # that produces the materialized view for this download
    download_type = None

    # Common serializer functions for exporting tables to CSV
    serializers = {
        'string': lambda x: str(x),
        'identity': lambda x: x,
        'division_id': lambda x: x.split(':')[-1] if x else x,
        'list': lambda x: '; '.join(str(elem) for elem in x if elem),
    }

    class Meta:
        # Don't manage this model with Django migrations
        managed = False
        abstract = True

    @classmethod
    def render_to_csv_response(cls, division_id, filename, sources=False, confidences=False):
        """
        The primary method for this class. Given a division_id, filename, and
        optional flags for whether or not to return sources/confidences, render
        an HttpResponse containing a CSV export of the model data.
        """
        # Get the queryset that will be used to write a CSV
        queryset = cls.objects.filter(division_id=division_id)

        # Retrieve the metadata we need for each field
        field_map = cls.get_field_map(sources, confidences)
        field_list = list(field_map.keys())
        qset_values = queryset.values(*field_list)

        # The field header map defines the headers that the CSV will use for
        # each queryset field
        field_header_map = {key: data['label'] for key, data in field_map.items()}

        # The field serializer map defines the serializers that should be used
        # to write each queryset field to a CSV field
        field_serializer_map = {key: data['serializer'] for key, data in field_map.items()}

        return djqscsv.render_to_csv_response(
            qset_values,
            field_header_map=field_header_map,
            field_serializer_map=field_serializer_map,
            field_order=field_list,
            filename=filename
        )

    @classmethod
    def get_field_map(cls, sources=False, confidences=False):
        """
        Retrieve a metadata map of fields in this download, optionally filtering
        out fields related to sources and confidences.
        """
        try:
            field_map = cls._get_field_map()
        except AttributeError:
            raise NotImplementedError(
                'Inheritors of DownloadMixin must implement the _get_field_map method'
            )
        else:
            fields = field_map.items()
            if sources is False:
                fields = [(key, val) for key, val in fields if not val.get('source')]
            if confidences is False:
                fields = [(key, val) for key, val in fields if not val.get('confidence')]
            return OrderedDict(fields)

    @classmethod
    def create_materialized_view(cls):
        """
        Create the materialized view that backs this download class.
        """
        sql_path = os.path.join(
            settings.BASE_DIR,
            'sfm_pc',
            'downloads',
            'sql',
            '{}.sql'.format(cls.download_type)
        )

        with open(sql_path) as f:
            sql = f.read()

        select = ''
        field_map = cls.get_field_map(sources=True, confidences=True)
        for key, field in field_map.items():
            select += '%s AS "%s",' % (field['sql'], key)

        # Strip the trailing comma from the SELECT
        if select:
            select = select[:-1]

        sql = sql.format(select=select)
        sql_prefix = 'CREATE MATERIALIZED VIEW {} AS'.format(cls._meta.db_table)
        query = '{} {}'.format(sql_prefix, sql)

        with connection.cursor() as cursor:
            cursor.execute(query)

    @classmethod
    def refresh_materialized_view(cls):
        """
        Refresh the materialized view that backs this download class.
        """
        with connection.cursor() as cursor:
            cursor.execute('REFRESH MATERIALIZED VIEW {}'.format(cls._meta.db_table))

    @classmethod
    def drop_materialized_view(cls):
        """
        Drop the materialized view that backs this download class.
        """
        with connection.cursor() as cursor:
            cursor.execute('DROP MATERIALIZED VIEW IF EXISTS {}'.format(cls._meta.db_table))
