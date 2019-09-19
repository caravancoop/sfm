from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from location.models import Location


class Command(BaseCommand):
    help = 'Clear extraneous OSM data from the database.'

    def handle(self, *args, **kwargs):
        if Location.objects.count() == 0:
            raise CommandError('No Locations found -- did you run link_locations first?')

        num_deleted, _ = Location.objects.filter(
            Q(associationarea__isnull=True) &
            Q(emplacementsite__isnull=True) &
            Q(violationlocation__isnull=True)
        ).delete()

        self.stdout.write(
            self.style.SUCCESS('Deleted {} extraneous locations'.format(num_deleted))
        )
