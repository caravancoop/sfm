from tqdm import tqdm
from django.core.management.base import BaseCommand, CommandError
from django.core.paginator import Paginator
from django.db.models import Q

from location.models import Location


class Command(BaseCommand):
    help = 'Clear extraneous OSM data from the database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch',
            dest='batch',
            action='store_true',
            default=False,
            help=(
                'Batch-delete data with a SQL DELETE statement. '
                'This argument makes the command run faster but uses more memory.'
            )
        )

    def handle(self, *args, **options):
        location_count = Location.objects.count()
        if location_count == 0:
            raise CommandError('No Locations found -- did you run link_locations first?')

        if options['batch'] is True:
            num_deleted, _ = Location.objects.filter(
                Q(associationarea__isnull=True) &
                Q(emplacementsite__isnull=True) &
                Q(violationlocation__isnull=True)
            ).delete()
        else:
            num_deleted = 0
            paginator = Paginator(Location.objects.all().order_by('id'), 50)
            with tqdm(total=location_count) as progress_bar:
                for page in paginator.page_range:
                    for location in paginator.page(page).object_list:
                        if not location.related_entities:
                            location.delete()
                            num_deleted += 1
                        progress_bar.update(1)

        self.stdout.write(
            self.style.SUCCESS('Deleted {} extraneous locations'.format(num_deleted))
        )
