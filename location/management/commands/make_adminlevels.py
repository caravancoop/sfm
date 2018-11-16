from collections import namedtuple
import os

from django.db import connection
from django.core.management.base import BaseCommand, CommandError

from violation.models import Violation, ViolationAdminLevel1, ViolationAdminLevel2
from location.models import Location

class Command(BaseCommand):
    help = 'Add some admin levels to the violations'

    def handle(self, *args, **kwargs):

        locations = Location.objects.all()

        def get_or_create_location(geo):
            location, created = Location.objects.get_or_create(id=geo.id)

            if created:
                location.name = geo.name
                location.geometry = geo.geometry

                country_code = geo.country_code.lower()
                location.division_id = 'ocd-division/country:{}'.format(country_code)

                if location.feature_type == 'point':
                    location.feature_type = 'node'
                else:
                    location.feature_type = 'relation'

                location.save()

            return location

        for location in locations.iterator():

            hierarchy = '''
                SELECT parents.*
                FROM osm_data AS parents
                JOIN (
                SELECT
                UNNEST(hierarchy) AS h_id,
                localname,
                tags,
                admin_level,
                name,
                geometry
                FROM osm_data
                WHERE id = %s
                ) AS child
                ON parents.id = child.h_id::integer
                WHERE parents.admin_level = '4'
                OR parents.admin_level = '6'
            '''

            cursor = connection.cursor()
            cursor.execute(hierarchy, [location.id])

            columns = [c[0] for c in cursor.description]
            results_tuple = namedtuple('OSMFeature', columns)

            hierarchy = (results_tuple(*r) for r in cursor)

            if hierarchy:
                for member in hierarchy:
                    if int(member.admin_level) == 6:
                        adminlevel1 = get_or_create_location(member)
                        location.adminlevel1 = adminlevel1

                    if int(member.admin_level) == 4:
                        adminlevel2 = get_or_create_location(member)
                        location.adminlevel2 = adminlevel2

                    location.save()
