from django.core.management.base import BaseCommand, CommandError
from django.db.utils import ProgrammingError

from sfm_pc.downloads import download_classes


class Command(BaseCommand):
    help = 'Create materialized views for spreadsheet exports'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recreate',
            action='store_true',
            dest='recreate',
            default=False,
            help='Recreate views instead of refreshing them'
        )
        parser.add_argument(
            'views',
            nargs='*',
            default=list(download_classes.keys()),
            help='The name of the views to create or update'
        )

    def handle(self, *args, **kwargs):
        for view in kwargs['views']:
            try:
                Model = download_classes[view]
            except KeyError:
                raise CommandError(
                    'View {} is not valid, should be one of: {}'.format(
                        view,
                        list(download_classes.keys())
                    )
                )

            if kwargs['recreate'] is True:
                Model.drop_materialized_view()

            try:
                Model.create_materialized_view()
            except ProgrammingError as e:
                if 'already exists' in str(e):
                    Model.refresh_materialized_view()
                    self.stdout.write('Refreshed view for {}'.format(view))
                else:
                    raise(e)
            else:
                self.stdout.write('Created view for {}'.format(view))
