import os
import subprocess

import pytest

from django.db.models.signals import post_save
from django.core.management import call_command
from django.db import connection
from django.conf import settings

from sfm_pc.signals import update_source_index, \
    update_orgname_index, update_orgalias_index, update_personname_index, \
    update_personalias_index, update_violation_index

from organization.models import OrganizationName, OrganizationAlias
from person.models import PersonName, PersonAlias
from violation.models import ViolationDescription
from source.models import Source


@pytest.fixture(scope='session')
@pytest.mark.django_db(transaction=True)
def django_db_setup(django_db_setup, django_db_blocker, request):

    post_save.disconnect(receiver=update_source_index, sender=Source)
    post_save.disconnect(receiver=update_orgname_index, sender=OrganizationName)
    post_save.disconnect(receiver=update_orgalias_index, sender=OrganizationAlias)
    post_save.disconnect(receiver=update_personname_index, sender=PersonName)
    post_save.disconnect(receiver=update_personalias_index, sender=PersonAlias)
    post_save.disconnect(receiver=update_violation_index, sender=ViolationDescription)

    create = '''
        CREATE TABLE osm_data (
            id BIGINT,
            localname VARCHAR,
            hierarchy VARCHAR[],
            tags JSONB,
            admin_level INTEGER,
            name VARCHAR,
            country_code VARCHAR,
            feature_type VARCHAR,
            search_index tsvector,
            PRIMARY KEY (id)
        )
    '''

    with django_db_blocker.unblock():
        with connection.cursor() as conn:
            conn.execute('CREATE EXTENSION IF NOT EXISTS postgis')
            conn.execute('DROP TABLE IF EXISTS osm_data')
            conn.execute(create)
            conn.execute("SELECT AddGeometryColumn ('public', 'osm_data', 'geometry', 4326, 'GEOMETRY', 2)")
            conn.execute("CREATE INDEX ON osm_data USING GIST (geometry)")

        dump_path = os.path.join(settings.BASE_DIR, 'fixtures/osm_data.sql')

        conn_str, db_name = settings.DATABASE_URL.rsplit('/', 1)
        conn_str = '{0}/test_{1}'.format(conn_str, db_name)

        prefix, conn_str = conn_str.split(':', 1)
        conn_str = 'postgresql:{}'.format(conn_str)

        with open(dump_path, 'r') as f:
            subprocess.run(['psql', conn_str], stdin=f)

        fixtures = [
            'tests/fixtures/auth.json',
            'tests/fixtures/source.json',
            'tests/fixtures/accesspoint.json',
            'tests/fixtures/organization.json',
            'tests/fixtures/person.json',
            'tests/fixtures/violation.json',
            'tests/fixtures/membershiporganization.json',
            'tests/fixtures/membershipperson.json',
            'tests/fixtures/composition.json',
        ]

        for fixture in fixtures:
            call_command('loaddata', fixture)

        call_command('update_countries_plus')
        call_command('make_flattened_views', '--recreate')

    @request.addfinalizer
    def tearDownModule():

        with django_db_blocker.unblock():
            with connection.cursor() as conn:
                conn.execute('TRUNCATE auth_user CASCADE')
                conn.execute('TRUNCATE source_source CASCADE')
                conn.execute('TRUNCATE source_accesspoint CASCADE')
                conn.execute('TRUNCATE organization_organization CASCADE')
                conn.execute('TRUNCATE person_person CASCADE')
                conn.execute('TRUNCATE violation_violation CASCADE')
                conn.execute('TRUNCATE membershipperson_membershipperson CASCADE')
                conn.execute('TRUNCATE membershiporganization_membershiporganization CASCADE')
                conn.execute('TRUNCATE composition_composition CASCADE')
