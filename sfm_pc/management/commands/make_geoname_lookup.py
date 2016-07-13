from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from django.db.utils import ProgrammingError

class Command(BaseCommand):
    help = 'Create lookup table for geonames'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--recreate',
            action='store_true',
            dest='recreate',
            default=False,
            help='Recreate search lookup table'
        )
    
    def handle(self, *args, **options):
        if options['recreate']:
            with connection.cursor() as c:
                c.execute('DROP MATERIALIZED VIEW IF EXISTS geonames_lookup')

            self.stdout.write(self.style.SUCCESS('Successfully dropped lookup'))
        
        create = ''' 
            CREATE MATERIALIZED VIEW geonames_lookup AS
              SELECT 
                id,
                'city' AS geoname_type
              FROM cities_city
              UNION
              SELECT
                id,
                'country' AS geoname_type
              FROM cities_country
              UNION
              SELECT
                id,
                'district' AS geoname_type
              FROM cities_district
              UNION
              SELECT
                id,
                'region' AS geoname_type
              FROM cities_region
              UNION
              SELECT
                id,
                'subregion' AS geoname_type
              FROM cities_subregion
        '''
        
        c = connection.cursor()

        try:
            c.execute(create)
            c.execute(''' 
                CREATE INDEX ON geonames_lookup (id)
            ''')
        except ProgrammingError as e:
            print(e)
            self.stdout.write(self.style.ERROR('Lookup already exists. If you want to recreate it, use the --recreate flag'))

        c.close()
