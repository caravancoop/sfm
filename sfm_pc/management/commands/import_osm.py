import urllib.request
import urllib.parse
import subprocess
import os
import zipfile
from io import BytesIO
import json
import re

import sqlalchemy as sa
import psycopg2

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import ProgrammingError
from django.conf import settings

from location.models import Location

DB_CONN = 'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}'

engine = sa.create_engine(DB_CONN.format(**settings.DATABASES['default']),
                          convert_unicode=True,
                          server_side_cursors=True)

class Command(BaseCommand):
    help = 'Import OSM data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--download_only',
            action='store_true',
            dest='download',
            default=False,
            help='Just download OSM data'
        )

        parser.add_argument(
            '--import_only',
            action='store_true',
            dest='import',
            default=False,
            help='Just import previously downloaded OSM data'
        )

        parser.add_argument(
            '--recreate',
            action='store_true',
            dest='recreate',
            default=False,
            help='Destroy OSM table before importing'
        )

    def handle(self, *args, **options):

        self.connection = engine.connect()

        self.data_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

        try:
            os.mkdir(self.data_directory)
        except OSError:
            pass

        download_only = options['download']
        import_only = options['import']
        recreate = options['recreate']

        if recreate:
            self.executeTransaction('DROP TABLE IF EXISTS osm_data')
            self.stdout.write(self.style.SUCCESS('Removed OSM table'))

        if not download_only and not import_only:
            download_only = True
            import_only = True

        self.makeDataTable()

        for country in settings.OSM_DATA:
            if download_only:
                self.downloadPBFs(country)
                self.downloadBoundaries(country)

            if import_only:
                self.importPBF(country)
                self.importBoundaries(country)

            self.createCombinedTable(country)

    def createCombinedTable(self, country):
        self.makeRawTable(country)
        self.findNewRecords(country)
        self.insertNewRecords(country)
        self.createLocations(country)
        self.createHierarchy(country)

    def createLocations(self, country):
        insert = '''
            INSERT INTO location_location (
              id,
              name,
              division_id,
              feature_type,
              tags,
              geometry,
              adminlevel
            )
            SELECT
              id,
              localname AS name,
              'ocd-division/country:' || country_code AS division_id,
              feature_type,
              tags,
              geometry,
              admin_level
            FROM osm_data
            WHERE country_code = :country_code
            ON CONFLICT DO NOTHING
        '''
        self.executeTransaction(sa.text(insert), country_code=country['country_code'])

    def createHierarchy(self, country):

        division_id = 'ocd-division/country:{}'.format(country['country_code'])

        for location in Location.objects.filter(division_id=division_id).iterator():

            hierarchy = '''
                SELECT parents.*
                FROM osm_data AS parents
                JOIN (
                  SELECT
                    UNNEST(hierarchy) AS h_id,
                    localname,
                    tags,
                    admin_level,
                    name,
                    geometry
                  FROM osm_data
                  WHERE id = :location_id
                )  AS child
                ON parents.id = child.h_id::integer
                WHERE parents.admin_level = '4'
                  OR parents.admin_level = '6'
            '''

            hierarchy = self.connection.execute(sa.text(hierarchy),
                                                location_id=location.id)

            if hierarchy:
                for member in hierarchy:
                    if int(member.admin_level) == 6:
                        adminlevel1 = self.get_or_create_location(member)
                        location.adminlevel1 = adminlevel1

                    if int(member.admin_level) == 4:
                        adminlevel2 = self.get_or_create_location(member)
                        location.adminlevel2 = adminlevel2

                    location.save()
                    self.stdout.write(self.style.HTTP_INFO('saved {}'.format(location)))

    def get_or_create_location(self, geo):
        location, created = Location.objects.get_or_create(id=geo.id)

        if created:
            location.name = geo.name
            location.geometry = geo.geometry

            country_code = geo.country_code.lower()
            location.division_id = 'ocd-division/country:{}'.format(country_code)

            if location.feature_type == 'point':
                location.feature_type = 'node'
            else:
                location.feature_type = 'relation'

            location.save()

        return location

    def makeDataTable(self):
        create = '''
            CREATE TABLE IF NOT EXISTS osm_data (
                id BIGINT,
                localname VARCHAR,
                hierarchy VARCHAR[],
                tags JSONB,
                admin_level INTEGER,
                name VARCHAR,
                country_code VARCHAR,
                feature_type VARCHAR,
                PRIMARY KEY (id, feature_type)
            )
        '''

        self.executeTransaction(sa.text(create))

        self.executeTransaction("""
            SELECT AddGeometryColumn ('public', 'osm_data', 'geometry', 4326, 'GEOMETRY', 2)
        """, raise_exc=False)

        self.executeTransaction("""
            CREATE INDEX geometry_index ON osm_data USING GIST (geometry)
        """, raise_exc=False)

        self.executeTransaction("""
            ALTER TABLE osm_data ALTER COLUMN admin_level TYPE VARCHAR
        """, raise_exc=False)

    def makeRawTable(self, country):
        create = '''
            CREATE TABLE raw_osm_data AS
              SELECT
                id,
                localname,
                hierarchy,
                tags,
                admin_level::VARCHAR,
                name,
                country_code,
                geometry,
                'boundary'::VARCHAR AS feature_type
              FROM osm_boundaries
              WHERE country_code = :country_code
              UNION
              SELECT
                osm_id,
                name AS localname,
                NULL::VARCHAR[] AS hierarchy,
                NULL::jsonb AS tags,
                admin_level::VARCHAR,
                name AS name,
                country_code,
                ST_Transform(way, 4326) AS geometry,
                'point'::VARCHAR AS feature_type
              FROM planet_osm_point
              WHERE name IS NOT NULL
                AND country_code = :country_code
              UNION
              SELECT
                osm_id,
                MAX(name) AS localname,
                NULL::VARCHAR[] AS hierarchy,
                NULL::jsonb AS tags,
                MAX(admin_level)::VARCHAR,
                MAX(name) AS name,
                NULL::VARCHAR AS country_code,
                ST_Transform(ST_Union(way), 4326) AS geometry,
                'polygon'::VARCHAR AS feature_type
              FROM planet_osm_polygon
              WHERE name IS NOT NULL
              GROUP BY osm_id
        '''

        self.executeTransaction('DROP TABLE IF EXISTS raw_osm_data')
        self.executeTransaction(sa.text(create), country_code=country['country_code'])


    def findNewRecords(self, country):
        create = '''
            CREATE TABLE new_osm_data (
                id BIGINT,
                feature_type VARCHAR,
                PRIMARY KEY (id, feature_type)
            )
        '''

        self.executeTransaction('DROP TABLE IF EXISTS new_osm_data')
        self.executeTransaction(create)

        insert = '''
            INSERT INTO new_osm_data
              SELECT r.id, r.feature_type
              FROM raw_osm_data AS r
              LEFT JOIN osm_data AS d
                ON r.id = d.id
              WHERE d.id IS NULL
        '''
        self.executeTransaction(insert)

    def insertNewRecords(self, country):

        update_data = '''
            INSERT INTO osm_data (
              id,
              localname,
              hierarchy,
              tags,
              admin_level,
              name,
              country_code,
              geometry,
              feature_type
            )
              SELECT raw.*
              FROM new_osm_data AS new
              JOIN raw_osm_data AS raw
                ON new.id = raw.id
                AND new.feature_type = raw.feature_type
        '''

        update_hierarchy = '''
            UPDATE osm_data SET
              hierarchy = s.hierarchy
            FROM (
              SELECT
                (array_append(array_agg(b.id ORDER BY b.admin_level DESC), 0::bigint))[2:10] AS hierarchy,
                a.id
              FROM osm_data AS a
              JOIN (
                SELECT
                  id,
                  geometry,
                  admin_level
                FROM osm_data
                WHERE feature_type = 'boundary'
              ) AS b
                ON ST_Within(a.geometry, b.geometry)
              GROUP BY a.id
            ) AS s
            WHERE osm_data.id = s.id AND osm_data.hierarchy IS NULL
        '''

        self.executeTransaction(sa.text(update_data), country_code=country['country_code'])
        self.executeTransaction(update_hierarchy)


    def importPBF(self, country):

        self.executeTransaction('DROP TABLE IF EXISTS planet_osm_point')
        self.executeTransaction('DROP INDEX planet_osm_point_index', raise_exc=False)

        DB_NAME = settings.DATABASES['default']['NAME']
        DB_USER = settings.DATABASES['default']['USER']
        DB_HOST = settings.DATABASES['default']['HOST']
        DB_PORT = settings.DATABASES['default']['PORT']

        filename = country['pbf_url'].rsplit('/', 1)[1]

        file_path = os.path.join(self.data_directory, filename)

        process = subprocess.Popen(['osm2pgsql',
                                    '-d',
                                    DB_NAME,
                                    '-U',
                                    DB_USER,
                                    '-H',
                                    DB_HOST,
                                    '-P',
                                    str(DB_PORT),
                                    '--cache-strategy',
                                    'sparse',
                                    '--slim',
                                    '--cache',
                                    '100',
                                    file_path], stdout=subprocess.PIPE)

        output, error = process.communicate()

        if output:
            self.stdout.write(self.style.SUCCESS(output.decode('utf-8')))

        if error:
            self.stdout.write(self.style.ERROR(error.decode('utf-8')))

        self.executeTransaction('ALTER TABLE planet_osm_point ADD COLUMN country_code VARCHAR')
        self.executeTransaction(sa.text('UPDATE planet_osm_point SET country_code = :code'), code=country['country_code'])


    def importBoundaries(self, country):

        self.executeTransaction('DROP TABLE IF EXISTS osm_boundaries')

        create = '''
            CREATE TABLE IF NOT EXISTS osm_boundaries (
                id BIGINT,
                localname VARCHAR,
                hierarchy VARCHAR[],
                tags JSONB,
                admin_level INTEGER,
                name VARCHAR,
                country_code VARCHAR
            )
        '''
        self.executeTransaction(create)
        self.executeTransaction("SELECT AddGeometryColumn ('public','osm_boundaries','geometry',4326,'MULTIPOLYGON',2)")

        file_path = os.path.join(self.data_directory, '{}.zip'.format(country['country']))

        insert_sql = '''
            INSERT INTO osm_boundaries (
              id,
              tags,
              admin_level,
              name,
              localname,
              geometry,
              country_code
            )
              SELECT
                :id,
                :tags,
                :admin_level,
                :name,
                :localname,
                ST_SetSRID(ST_GeomFromGeoJSON(:geometry), 4326),
                :country_code
        '''

        inserts = []
        count = 0

        with zipfile.ZipFile(file_path) as zf:
            for filename in zf.namelist():

                if "GeoJson" in filename:

                    with zf.open(filename) as geojson:

                        geojson_cleaned = re.sub(r'""(?!,)', '', geojson.read().decode('utf-8'))
                        boundary_data = json.loads(geojson_cleaned)

                        for feature in boundary_data['features']:

                            insert = {
                                'id': feature['properties']['id'],
                                'geometry': json.dumps(feature['geometry']),
                                'tags': json.dumps(feature['properties']),
                                'admin_level': feature['properties']['admin_level'],
                                'name': feature['properties']['name'],
                                'localname': feature['properties']['localname'],
                                'country_code': country['country_code'],
                            }

                            inserts.append(insert)

                            if len(inserts) % 10000 == 0:
                                self.executeTransaction(sa.text(insert_sql), inserts)
                                count += 10000
                                inserts = []
                                self.stdout.write(self.style.SUCCESS('Inserted {} boundaries'.format(count)))

            if inserts:
                count += len(inserts)
                self.executeTransaction(sa.text(insert_sql), inserts)
                self.stdout.write(self.style.SUCCESS('Inserted {} boundaries'.format(count)))

    def downloadPBFs(self, country):

        pbf_url = country['pbf_url']

        filename = pbf_url.rsplit('/', 1)[1]
        file_path = os.path.join(self.data_directory, filename)

        with urllib.request.urlopen(pbf_url) as u:
            with open(file_path, 'wb') as f:
                while True:
                    chunk = u.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)

        self.stdout.write(self.style.SUCCESS('Downloaded PBF file for {}'.format(country['country'])))

    def downloadBoundaries(self, country):

        file_path = os.path.join(self.data_directory, '{}.zip'.format(country['country']))

        url = "{base_url}?cliVersion=1.0&cliKey={api_key}&exportFormat=json&exportLayout=levels&exportAreas=water&union=false&from_AL=2&to_AL=8&selected={relation_id}".format(
            base_url=settings.OSM_BASE_URL,
            api_key=settings.OSM_API_KEY,
            relation_id=country['relation_id'])

        with urllib.request.urlopen(url) as u:
            with open(file_path, 'wb') as f:
                while True:
                    chunk = u.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)

        self.stdout.write(self.style.SUCCESS('Downloaded boundary file for {}'.format(country['country'])))

    def executeTransaction(self, query, *args, **kwargs):
        trans = self.connection.begin()

        raise_exc = kwargs.get('raise_exc', True)

        try:
            self.connection.execute("SET local timezone to '{}'".format(settings.TIME_ZONE))
            if kwargs:
                self.connection.execute(query, **kwargs)
            else:
                self.connection.execute(query, *args)
            trans.commit()
        except (psycopg2.ProgrammingError, sa.exc.ProgrammingError) as e:
            # TODO: Make some kind of logger
            # logger.error(e, exc_info=True)
            trans.rollback()
            if raise_exc:
                raise e
