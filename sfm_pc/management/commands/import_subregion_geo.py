import os
import zipfile

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from django.db.utils import ProgrammingError
from django.conf import settings

import psycopg2

import cities
DB_CONN = 'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}'
DB_CONN_STR = DB_CONN.format(**settings.DATABASES['default'])

class Command(BaseCommand):
    help = 'Create flattened versions of entity tables'
    
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
        
        data_directory = os.path.join(os.path.dirname(os.path.abspath(cities.__file__)), 'data')
        self.createTable()

        for filename in settings.CITIES_FILES['city']['filenames']:
            txt_file = filename.rsplit('.', 1)[0]
            txt_file = '{}.txt'.format(txt_file)
            

            with zipfile.ZipFile(os.path.join(data_directory, filename)) as zf:
                zf.extract(txt_file, path=os.path.join(data_directory))

            with open(os.path.join(data_directory, txt_file)) as f:

                copy_st = ''' 
                    COPY raw_geonames FROM STDIN 
                    WITH (FORMAT CSV, DELIMITER'\t')
                '''
                
                with psycopg2.connect(DB_CONN_STR) as conn:
                    with conn.cursor() as curs:
                        try:
                            curs.copy_expert(copy_st, f)
                        except psycopg2.IntegrityError as e:
                            conn.rollback()
                            raise e

        update = ''' 
            UPDATE geosite_geositecoordinates SET
              value=s.location
            FROM (
              SELECT 
                ST_SetSRID(ST_MakePoint(longitude, latitude), 4326) AS location,
                ggc.id
              FROM raw_geonames AS r
              JOIN geosite_geositegeonameid AS ggi
                ON r.geonameid = ggi.value
              JOIN geosite_geosite AS gg
                ON ggi.object_ref_id = gg.id
              JOIN geosite_geositecoordinates AS ggc
                ON gg.id = ggc.object_ref_id
            ) AS s
            WHERE geosite_geositecoordinates.id = s.id
        '''

        with psycopg2.connect(DB_CONN_STR) as conn:
            with conn.cursor() as curs:
                curs.execute(update)

    def createTable(self):
        create = ''' 
            CREATE TABLE raw_geonames (
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
            conn.execute('DROP TABLE IF EXISTS raw_geonames')
            conn.execute(create)

