import os
import zipfile
import urllib

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction, connection
from django.db.utils import ProgrammingError
from django.conf import settings

import psycopg2

DB_CONN = 'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}'
DB_CONN_STR = DB_CONN.format(**settings.DATABASES['default'])

if not hasattr(settings, 'GEONAMES_FILES'):
    raise ImproperlyConfigured('"GEONAMES_FILES" is not set in your settings.py')

class Command(BaseCommand):
    help = 'Import geonames files'
    
    def add_arguments(self, parser):
        pass 
        # parser.add_argument(
        #     '--recreate',
        #     action='store_true',
        #     dest='recreate',
        #     default=False,
        #     help='Recreate all views'
        # )
    
    def handle(self, *args, **options):
        
        self.data_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        
        try:
            os.mkdir(self.data_directory)
        except OSError:
            pass

        self.createTable()
        self.importHierarchy()

        for filename in settings.GEONAMES_FILES['filenames']:
            txt_file = filename.rsplit('.', 1)[0]
            txt_file = '{}.txt'.format(txt_file)
            
            self.downloadFile(filename)
            self.stdout.write(self.style.NOTICE('Downloaded "{}" ...'.format(filename)))

            with zipfile.ZipFile(os.path.join(self.data_directory, filename)) as zf:
                zf.extract(txt_file, path=os.path.join(self.data_directory))

            with open(os.path.join(self.data_directory, txt_file)) as f:

                copy_st = ''' 
                    COPY geonames FROM STDIN 
                    WITH (FORMAT CSV, DELIMITER'\t')
                '''
                
                with psycopg2.connect(DB_CONN_STR) as conn:
                    with conn.cursor() as curs:
                        try:
                            curs.copy_expert(copy_st, f)
                        except psycopg2.IntegrityError as e:
                            conn.rollback()
                            raise e
            
            self.stdout.write(self.style.SUCCESS('Imported "{}" ...'.format(filename)))

        add_geometry = ''' 
            SELECT AddGeometryColumn('public', 'geonames', 'location', 4326, 'POINT', 2)
        '''
        
        update = ''' 
            UPDATE geonames SET
              location = s.location
            FROM (
              SELECT 
                geonameid,
                ST_SetSRID(ST_MakePoint(longitude, latitude), 4326) AS location
              FROM geonames
            ) AS s
            WHERE geonames.geonameid = s.geonameid
        '''

        with psycopg2.connect(DB_CONN_STR) as conn:
            with conn.cursor() as curs:
                curs.execute(add_geometry)
                curs.execute(update)
                curs.execute(''' 
                    CREATE INDEX ON geonames USING GIST (location)
                ''')
        
        self.stdout.write(self.style.SUCCESS('Added geospatial index'))
        
        add_search = ''' 
            ALTER TABLE geonames ADD COLUMN search_index tsvector
        '''
        
        update = ''' 
            UPDATE geonames SET
              search_index = s.vector
            FROM (
              SELECT 
                geonameid,
                to_tsvector('english', COALESCE(name, '') || ' ' || COALESCE(alternatenames, '')) AS vector
              FROM geonames
            ) AS s
            WHERE geonames.geonameid = s.geonameid
        '''
        
        add_index = ''' 
            CREATE INDEX on geonames USING GIN (search_index)
        '''

        with psycopg2.connect(DB_CONN_STR) as conn:
            with conn.cursor() as curs:
                curs.execute(add_search)
                curs.execute(update)
                curs.execute(add_index)
        
        self.stdout.write(self.style.SUCCESS('Added search index'))
        

    def downloadFile(self, filename):
        file_path = os.path.join(self.data_directory, filename)
        
        url = settings.GEONAMES_FILES['url'].format(filename=filename)

        with urllib.request.urlopen(url) as u:
            with open(file_path, 'wb') as f:
                while True:
                    chunk = u.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
    
    def importHierarchy(self):
        self.downloadFile('hierarchy.zip')
        
        with zipfile.ZipFile(os.path.join(self.data_directory, 'hierarchy.zip')) as zf:
            zf.extract('hierarchy.txt', path=os.path.join(self.data_directory))

        with open(os.path.join(self.data_directory, 'hierarchy.txt')) as f:

            copy_st = ''' 
                COPY geonames_hierarchy FROM STDIN 
            '''
            
            with psycopg2.connect(DB_CONN_STR) as conn:
                with conn.cursor() as curs:
                    try:
                        curs.copy_expert(copy_st, f)
                    except psycopg2.IntegrityError as e:
                        conn.rollback()
                        raise e


    def createTable(self):
        create = ''' 
            CREATE TABLE geonames (
              geonameid INTEGER,
              name varchar(200),
              asciiname varchar(200),
              alternatenames varchar(10000),
              latitude double precision,
              longitude double precision,
              feature_class varchar(1),
              feature_code varchar(10),
              country_code varchar(2),
              cc2 varchar(200),
              admin1 varchar(20),
              admin2 varchar(80),
              admin3 varchar(20),
              admin4 varchar(20),
              population bigint,
              elevation integer,
              dem integer,
              timezone varchar(40),
              modification_date DATE,
              PRIMARY KEY (geonameid)
            )
        '''
        
        with connection.cursor() as conn:
            conn.execute('DROP TABLE IF EXISTS geonames')
            conn.execute(create)

