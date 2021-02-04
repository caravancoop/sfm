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
            self.stdout.write('Dropped {}'.format(self.TABLE_NAME))

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

        if not error:
            self.stdout.write(self.style.SUCCESS('Imported raw location file'))

    def create_location_objects(self):
        ...
