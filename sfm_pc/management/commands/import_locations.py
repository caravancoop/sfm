import urllib.request
import urllib.parse
import subprocess
import os
import zipfile
from io import BytesIO
import json
import re

from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.utils import ProgrammingError
from django.conf import settings

from location.models import Location


class Command(BaseCommand):
    help = 'Import raw location data into Location objects'

    TABLE_NAME = 'test_locations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--location_file',
            dest='location_file',
            default='fixtures/locations.geojson',
            help='Relative path to location file for import'
        )

    def handle(self, *args, **options):

        self.location_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..',
            '..',
            '..',
            options['location_file'],
        )

        self.import_raw_locations()
        self.create_location_objects()

    def import_raw_locations(self):
        with connection.cursor() as cursor:
            cursor.execute('DROP TABLE IF EXISTS {}'.format(self.TABLE_NAME))
            self.stdout.write('Dropped existing table "{}"'.format(self.TABLE_NAME))

        process = subprocess.Popen([
            'ogr2ogr',
            '-f',
            'PostgreSQL',
            'PG:dbname={NAME} user={USER} password={PASSWORD} host={HOST} port={PORT}'.format(**settings.DATABASES['default']),
            self.location_file,
            '-nln',
            self.TABLE_NAME,
        ], stdout=subprocess.PIPE)

        output, error = process.communicate()

        if output:
            self.stdout.write(self.style.SUCCESS(output.decode('utf-8')))

        if error:
            self.stdout.write(self.style.ERROR(error.decode('utf-8')))
            raise CommandError('Could not import raw location file')

        with connection.cursor() as cursor:
            for column in ('sfm', 'tags'):
                cursor.execute('''
                    ALTER TABLE {table_name}
                    ALTER COLUMN {column_name}
                    TYPE json USING {column_name}::json
                '''.format(table_name=self.TABLE_NAME,
                           column_name=column))

                cursor.execute('SELECT COUNT(*) FROM {}'.format(self.TABLE_NAME))

                row = cursor.fetchone()

                n_inserted, = row

        if not error:
            self.stdout.write(
                self.style.SUCCESS(
                    'Imported {} records from raw location file'.format(n_inserted)
                )
            )

    def create_location_objects(self):
        insert = '''
            INSERT INTO location_location (
              id,
              name,
              feature_type,
              division_id,
              tags,
              sfm,
              adminlevel,
              adminlevel1_id,
              adminlevel2_id,
              geometry
            )
            SELECT
              a.id,
              a.sfm->>'location:name' AS name,
              CASE
                WHEN a.tags->>'type' = 'boundary' THEN 'boundary'
                ELSE a.type
              END AS feature_type,
              'ocd-division/country:' || LOWER(b.tags->>'ISO3166-1') AS division_id,
              a.tags,
              a.sfm,
              a.tags->>'admin_level' AS adminlevel,
              c.id AS adminlevel1_id,
              d.id AS adminlevel2_id,
              a.wkb_geometry AS geometry
            FROM {table_name} AS a
            JOIN {table_name} AS b
            ON a.sfm->>'location:admin_level_2' = b.sfm->>'location:humane_id:admin'
            LEFT JOIN {table_name} AS c
            ON a.sfm->>'location:admin_level_6' = c.sfm->>'location:humane_id:admin'
              AND a.sfm->>'location:admin_level' != '6'
            LEFT JOIN {table_name} AS d
            ON a.sfm->>'location:admin_level_4' = d.sfm->>'location:humane_id:admin'
              AND a.sfm->>'location:admin_level' != '4'
            ON CONFLICT (id) DO UPDATE
              /* TODO: Specify desired updates, if any, to existing locations */
              SET sfm = EXCLUDED.sfm
            RETURNING id
        '''.format(table_name=self.TABLE_NAME)

        with connection.cursor() as cursor:
            '''
            TODO: Should we remove locations that were not inserted or updated?
            NO - Location files will be provided on a per-country basis.
            '''
            cursor.execute(insert)

            n_inserted_or_updated = len(cursor.fetchall())

        self.stdout.write(
            self.style.SUCCESS(
                'Inserted or updated {} location objects'.format(n_inserted_or_updated)
            )
        )
