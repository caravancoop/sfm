import urllib.request
import urllib.parse
import subprocess
import os
import zipfile
from io import BytesIO
import json

import sqlalchemy as sa

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from django.db.utils import ProgrammingError
from django.conf import settings

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
            '--transform_only',
            action='store_true',
            dest='transform',
            default=False,
            help='Just transform existing OSM table into useful format'
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
        transform_only = options['transform']

        if not download_only and not import_only and not transform_only:
            download_only = True
            import_only = True
            transform_only = True
        
        for country in settings.OSM_DATA:
            
            if download_only:
                self.downloadPBFs(country)
                self.downloadBoundaries(country)

            if import_only:
                # self.importPBF(country)
                self.importBoundaries(country)
    
    def transform(self):
        pass

    def importPBF(self, country):
        
        DB_NAME = settings.DATABASES['default']['NAME']
        
        osm_tables = ['planet_osm_point', 
                      'planet_osm_roads', 
                      'planet_osm_polygon', 
                      'planet_osm_line']
        
        for table in osm_tables:
            self.executeTransaction('DROP TABLE IF EXISTS {}'.format(table))

        filename = country['pbf_url'].rsplit('/', 1)[1]
            
        file_path = os.path.join(self.data_directory, pbf_file)
        
        process = subprocess.Popen(['osm2pgsql',
                                    '-d',
                                    DB_NAME,
                                    '-a',
                                    file_path], stdout=subprocess.PIPE)
        
        output, error = process.communicate()
        
        if output:
            self.stdout.write(self.style.SUCCESS(output.decode('utf-8')))
        
        if error:
            self.stdout.write(self.style.ERROR(error.decode('utf-8')))
    
    def importBoundaries(self, country):
        
        create = ''' 
            CREATE TABLE raw_osm_boundaries (
                id BIGINT,
                localname VARCHAR,
                hierarchy VARCHAR[],
                tags JSONB,
                admin_level INTEGER,
                name VARCHAR
            )
        '''
        
        self.executeTransaction('DROP TABLE IF EXISTS raw_osm_boundaries')
        self.executeTransaction(create)
        
        self.executeTransaction("SELECT AddGeometryColumn ('public','raw_osm_boundaries','geometry',4326,'MULTIPOLYGON',2)")

        file_path = os.path.join(self.data_directory, '{}.zip'.format(country['country']))
        
        insert_sql = ''' 
            INSERT INTO raw_osm_boundaries (
              id,
              localname,
              hierarchy,
              tags,
              admin_level,
              name,
              geometry
            ) 
              SELECT
                :id,
                :localname,
                :hierarchy,
                :tags,
                :admin_level,
                :name,
                ST_SetSRID(ST_GeomFromGeoJSON(:geometry), 4326)
        '''
        
        inserts = []
        count = 0

        with zipfile.ZipFile(file_path) as zf:
            for filename in zf.namelist():

                geojson = BytesIO(zf.read(filename))
                geojson.seek(0)
                
                boundary_data = json.loads(geojson.getvalue().decode('utf-8'))

                for feature in boundary_data['features']:

                    insert = {
                        'id': feature['properties']['id'],
                        'localname': feature['properties']['localname'],
                        'hierarchy': feature['rpath'],
                        'geometry': json.dumps(feature['geometry']),
                        'tags': json.dumps(feature['properties']['tags']),
                        'admin_level': feature['properties']['admin_level'],
                        'name': feature['properties']['name'],
                    }
                    
                    inserts.append(insert)

                    if len(inserts) % 10000 == 0:
                        self.executeTransaction(sa.text(insert_sql), inserts)
                        count += 10000
                        inserts = []
                        self.stdout.write(self.style.SUCCESS('Inserted {}'.format(count)))

            if inserts:
                count += len(inserts)
                self.executeTransaction(sa.text(insert_sql), inserts)
                self.stdout.write(self.style.SUCCESS('Inserted {}'.format(count)))
        

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

        country_feature_id = country['osm_id']
        
        params = {
            'apiversion': '1.0',
            'apikey': settings.OSM_API_KEY,
            'exportFormat': 'json',
            'exportLayout': 'levels',
            'exportAreas': 'land',
            'from_al': '2',
            'to_al': '8',
            'union': 'false',
            'selected': country_feature_id,
        }
        
        data = urllib.parse.urlencode(params)

        file_path = os.path.join(self.data_directory, '{}.zip'.format(country['country']))

        with urllib.request.urlopen(country['boundary_url'], data=data) as u:
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
        except sa.exc.ProgrammingError as e:
            # TODO: Make some kind of logger
            # logger.error(e, exc_info=True)
            trans.rollback()
            if raise_exc:
                raise e

