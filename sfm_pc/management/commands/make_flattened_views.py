import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from django.db.utils import ProgrammingError
from sfm_pc.utils import execute_sql

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
                self.stdout.write(self.style.SUCCESS('Recreating view from %s' %
                                                     file_path))
                with connection.cursor() as c:
                    c.execute('DROP MATERIALIZED VIEW IF EXISTS {}'.format(view_name))

                execute_sql(file_path)

            elif options['refresh']:
                self.stdout.write(self.style.SUCCESS('Refreshing view for %s' %
                                                     view_name))
                with connection.cursor() as c:
                    c.execute('REFRESH MATERIALIZED VIEW {}'.format(view_name))

            else:
                self.stdout.write(self.style.SUCCESS('Recreating views from %s' %
                                                     file_path))
                execute_sql(file_path)
