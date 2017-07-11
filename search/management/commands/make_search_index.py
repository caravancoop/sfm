from os.path import join, abspath, dirname

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from django.db.utils import ProgrammingError

from search.search import Searcher

class Command(BaseCommand):
    help = 'Add global search index'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--recreate',
            action='store_true',
            dest='recreate',
            default=False,
            help='Recreate search index'
        )
        parser.add_argument(
            '--force-refresh',
            action='store_true',
            dest='force_refresh',
            default=False,
            help='Force search index to refresh'
        )
    
    def handle(self, *args, **options):
        
        self.index_everything()

        self.stdout.write(self.style.SUCCESS('Successfully created global search index'))
    
    def index_everything(self):
        sql_file = abspath(join(dirname(__file__), 'search_index.sql'))

        with open(sql_file) as f:
            cursor = connection.cursor()
            
            cursor.execute(f.read())

            for row in cursor:
                print(row)

    def index_people(self):
        pass

    def index_organizations(self):
        pass

    def index_sources(self):
        pass
