import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from django.db.utils import ProgrammingError

class Command(BaseCommand):
    help = 'Create flattened versions of entity tables'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--recreate',
            action='store_true',
            dest='recreate',
            default=False,
            help='Recreate all views'
        )
        parser.add_argument(
            '--refresh',
            action='store_true',
            dest='refresh',
            default=False,
            help='Refresh all views'
        )
    
    def handle(self, *args, **options):
    
        this_dir = os.path.abspath(os.path.dirname(__file__))
        sql_dir = os.path.join(this_dir, 'sql')

        for view in os.listdir(sql_dir):
            file_path = os.path.join(sql_dir, view)
            view_name = view.rsplit('_', 1)[0]
            
            if options['recreate']:
                
                with connection.cursor() as c:
                    c.execute('DROP MATERIALIZED VIEW IF EXISTS {}'.format(view_name))
                
                self.createView(file_path)

            elif options['refresh']:

                with connection.cursor() as c:
                    c.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY {}'.format(view_name))
            
            else:
                self.createView(file_path)

    def createView(self, file_path):
        
        with open(file_path) as f:
            statements = f.read().split(';')
        
            with connection.cursor() as c:
                for statement in statements:
                    c.execute(statement.strip())
