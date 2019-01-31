import urllib.request
import urllib.parse
import subprocess
import os
import zipfile
from io import BytesIO
import json
import re

import sqlalchemy as sa
import psycopg2

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import ProgrammingError
from django.conf import settings

from location.models import Location

DB_CONN = 'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}'

engine = sa.create_engine(DB_CONN.format(**settings.DATABASES['default']),
                          convert_unicode=True,
                          server_side_cursors=True)

class Command(BaseCommand):
    help = 'Import OSM data'

    def handle(self, *args, **options):

        self.connection = engine.connect()

        self.createLocations(country)
        self.createHierarchy(country)

    def createLocations(self):
        insert = '''
            INSERT INTO location_location (
              id,
              name,
              division_id,
              feature_type,
              tags,
              geometry,
              adminlevel
            )
            SELECT
              id,
              localname AS name,
              'ocd-division/country:' || country_code AS division_id,
              feature_type,
              tags,
              geometry,
              admin_level
            FROM osm_data
            ON CONFLICT DO NOTHING
        '''
        self.executeTransaction(sa.text(insert), country_code=country['country_code'])

    def createHierarchy(self):

        for location in Location.objects.all().iterator():

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
                  WHERE id = :location_id
                )  AS child
                ON parents.id = child.h_id::integer
                WHERE parents.admin_level = '4'
                  OR parents.admin_level = '6'
            '''

            hierarchy = self.connection.execute(sa.text(hierarchy),
                                                location_id=location.id)

            if hierarchy:
                for member in hierarchy:
                    if int(member.admin_level) == 6:
                        adminlevel1 = self.get_or_create_location(member)
                        location.adminlevel1 = adminlevel1

                    if int(member.admin_level) == 4:
                        adminlevel2 = self.get_or_create_location(member)
                        location.adminlevel2 = adminlevel2

                    location.save()
                    self.stdout.write(self.style.HTTP_INFO('saved {}'.format(location)))

    def get_or_create_location(self, geo):
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

    def executeTransaction(self, query, *args, **kwargs):
        trans = self.connection.begin()

        raise_exc = kwargs.get('raise_exc', True)

        try:
            self.connection.execute("SET local timezone to '{}'".format(settings.TIME_ZONE))
            if kwargs:
                self.connection.execute(query, **kwargs)
            else:
                self.connection.execute(query, *args)
            trans.commit()
        except (psycopg2.ProgrammingError, sa.exc.ProgrammingError) as e:
            # TODO: Make some kind of logger
            # logger.error(e, exc_info=True)
            trans.rollback()
            if raise_exc:
                raise e
