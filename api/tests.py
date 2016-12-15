import json
import os
import subprocess

import sqlalchemy as sa

from django.conf import settings
from django.test import TestCase, Client
from django.core.urlresolvers import reverse_lazy
from django.db.models.signals import post_save
from django.core.management import call_command

from sfm_pc.signals import update_source_index, update_publication_index, \
    update_orgname_index, update_orgalias_index, update_personname_index, \
    update_personalias_index, update_violation_index

from organization.models import OrganizationName, OrganizationAlias
from person.models import PersonName, PersonAlias
from violation.models import ViolationDescription
from source.models import Source, Publication


def setUpModule():

    post_save.disconnect(receiver=update_source_index, sender=Source)
    post_save.disconnect(receiver=update_publication_index, sender=Publication)
    post_save.disconnect(receiver=update_orgname_index, sender=OrganizationName)
    post_save.disconnect(receiver=update_orgalias_index, sender=OrganizationAlias)
    post_save.disconnect(receiver=update_personname_index, sender=PersonName)
    post_save.disconnect(receiver=update_personalias_index, sender=PersonAlias)
    post_save.disconnect(receiver=update_violation_index, sender=ViolationDescription)
    

    engine = sa.create_engine('postgresql://postgres:@localhost:5432/test_sfm-db')

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
    
    dump_path = os.path.join(settings.BASE_DIR, 'fixtures/osm_data.sql')

    with engine.begin() as conn:
        conn.execute('CREATE EXTENSION IF NOT EXISTS postgis')
        conn.execute('DROP TABLE IF EXISTS osm_data')
        conn.execute(create)
        conn.execute("SELECT AddGeometryColumn ('public', 'osm_data', 'geometry', 4326, 'GEOMETRY', 2)")
        conn.execute("CREATE INDEX ON osm_data USING GIST (geometry)")

    with open(dump_path, 'r') as f:
        psql = subprocess.run(['psql', '-d', 'test_sfm-db', '-U', 'postgres'], stdin=f)
    
    fixtures = [
        'api/fixtures/auth.json',
        'api/fixtures/source.json',
        'api/fixtures/organization.json',
        'api/fixtures/person.json',
        'api/fixtures/violation.json',
        'api/fixtures/membershiporganization.json',
        'api/fixtures/membershipperson.json',
    ]
    
    for fixture in fixtures:
        call_command('loaddata', fixture)

    call_command('make_flattened_views')

def tearDownModule():
    engine = sa.create_engine('postgresql://postgres:@localhost:5432/test_sfm-db')
    
    with engine.begin() as conn:
        conn.execute('TRUNCATE auth_user CASCADE')
        conn.execute('TRUNCATE source_source CASCADE')
        conn.execute('TRUNCATE organization_organization CASCADE')
        conn.execute('TRUNCATE person_person CASCADE')
        conn.execute('TRUNCATE violation_violation CASCADE')
        conn.execute('TRUNCATE membershipperson_membershipperson CASCADE')
        conn.execute('TRUNCATE membershiporganization_membershiporganization CASCADE')

class RouteTest(TestCase):
    
    def getPage(self, url):
        client = Client()
        return client.get(url)

    def test_country_list(self):
        response = self.getPage(reverse_lazy('country-list'))

        assert response.status_code == 200

        response_json = json.loads(response.content.decode('utf-8'))
        first_country = response_json[0]

        assert set(first_country.keys()) == {'geometry', 'id', 'properties', 'type', 'bbox'}
        assert first_country['id'] == 'ng'

    def test_country_list_tolerance(self):
        url = '{}?tolerance=0.0001'.format(reverse_lazy('country-list'))
        response = self.getPage(url)

        assert response.status_code == 200

    def test_country_list_bad_param(self):
        url = '{}?foo=bar'.format(reverse_lazy('country-list'))
        response = self.getPage(url)

        assert response.status_code == 400

        response_json = json.loads(response.content.decode('utf-8'))
        assert response_json['errors'][0] == "'foo' is not a valid query parameter"

    def test_country_detail(self):
        response = self.getPage(reverse_lazy('country-detail', args=['ng']))

        assert response.status_code == 200

        response_json = json.loads(response.content.decode('utf-8'))
        assert set(response_json.keys()) == {'name', 'title', 'description', 'events_count'}

    def test_country_zip(self):
        response = self.getPage(reverse_lazy('country-zip', args=['ng']))
        assert response.status_code == 204

    def test_country_text(self):
        response = self.getPage(reverse_lazy('country-txt', args=['ng']))
        assert response.status_code == 204

    def test_country_map_no_at(self):
        response = self.getPage(reverse_lazy('country-map', args=['ng']))

        assert response.status_code == 400

        response_json = json.loads(response.content.decode('utf-8'))
        assert response_json['errors'][0] == "at is a required field"

    def test_country_map(self):
        url = '{}?at=2014-01-01'.format(reverse_lazy('country-map', args=['ng']))
        response = self.getPage(url)

        assert response.status_code == 200

    def test_country_events(self):
        response = self.getPage(reverse_lazy('country-events', args=['ng']))
        assert response.status_code == 200

    def test_country_geometries(self):
        response = self.getPage(reverse_lazy('country-geometry', args=['ng']))
        assert response.status_code == 200
    
    def test_country_autocomplete_no_q(self):
        response = self.getPage(reverse_lazy('osm-auto', args=['ng']))
        
        assert response.status_code == 400
        response_json = json.loads(response.content.decode('utf-8'))

        assert response_json['errors'][0] == 'q is a required field'
        
