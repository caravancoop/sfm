import os

from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse
from django.db import connection


class BaseDownload:
    download_type = None
    selected_fields = []

    @classmethod
    def get_select_statement(cls, sources=False, confidences=False):
        """
        Get the SELECT statement for the fields of this download.
        """
        if cls.selected_fields == []:
            raise NotImplementedError(
                'Children of BaseDownload must implement the selected_fields attribute'
            )

        select = ''
        for field in cls.selected_fields:
            if field.get('source') is True and sources is False:
                continue
            elif field.get('confidence') is True and confidences is False:
                continue
            else:
                select += '%s AS "%s",' % (field['name'], field['label'])

        # Strip the trailing comma from the SELECT
        if select:
            select = select[:-1]

        return select

    @classmethod
    def render_to_csv_response(cls, division_id, sources=False, confidences=False):
        """
        Render a CSV download for a given division_id, optionally including
        sources and confidences in the download.
        """
        if cls.download_type is None:
            raise NotImplementedError(
                'Children of BaseDownload must implement the download_type attribute'
            )

        sql_path = os.path.join(
            settings.BASE_DIR,
            'sfm_pc',
            'downloads',
            'sql',
            '{}.sql'.format(cls.download_type)
        )

        with open(sql_path) as f:
            sql = f.read()

        iso = division_id[-2:]

        download_name = '{}_{}_{}'.format(
            cls.download_type,
            iso.upper(),
            timezone.now().isoformat()
        )

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(download_name)

        with connection.cursor() as cursor:
            copy = '''
                COPY (%s) TO STDOUT WITH CSV HEADER FORCE QUOTE *
            ''' % sql

            select = cls.get_select_statement(sources, confidences)

            try:
                copy = copy.format(
                    division_id=division_id,
                    select=select
                )
            except TypeError:
                # division_id was not required, so skip it
                copy - copy.format(select=select)

            cursor.copy_expert(copy, response)

        return response
