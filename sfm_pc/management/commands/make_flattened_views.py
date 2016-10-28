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
    
        all_views = [
            'area',
            'association',
            'composition',
            'emplacement',
            'violation',
            'geosite',
            'membershipperson',
            'organization',
            'person',
        ]
        
        this_dir = os.path.abspath(os.path.dirname(__file__))
        for view in all_views:
            
            file_path = os.path.join(this_dir, 'sql/{}_view.sql'.format(view))
            
            with open(file_path) as f:
                create = f.read()
        
                c = connection.cursor()

                try:
                    c.execute(create)
                except ProgrammingError as e:
                    print(e)
                    self.stdout.write(self.style.ERROR('{} view already exists. If you want to recreate it use the --recreate flag'))

                c.close()
