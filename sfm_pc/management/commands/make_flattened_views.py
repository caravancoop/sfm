import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from django.db.utils import ProgrammingError

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
    
        this_dir = os.path.abspath(os.path.dirname(__file__))
        sql_dir = os.path.join(this_dir, 'sql')

        for view in os.listdir(sql_dir):
            
            file_path = os.path.join(sql_dir, view)
            
            with open(file_path) as f:
                create = f.read()
        
                with connection.cursor() as c:
                    c.execute(create)
                    
