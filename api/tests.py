import json
import os
import subprocess

import sqlalchemy as sa

from django.conf import settings
from django.test import TestCase, Client
from django.core.urlresolvers import reverse_lazy
from django.db.models.signals import post_save
from django.core.management import call_command
from django.db import connection

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

    with connection.cursor() as conn:
        conn.execute('CREATE EXTENSION IF NOT EXISTS postgis')
        conn.execute('DROP TABLE IF EXISTS osm_data')
        conn.execute(create)
        conn.execute("SELECT AddGeometryColumn ('public', 'osm_data', 'geometry', 4326, 'GEOMETRY', 2)")
        conn.execute("CREATE INDEX ON osm_data USING GIST (geometry)")

    dump_path = os.path.join(settings.BASE_DIR, 'fixtures/osm_data.sql')

    with open(dump_path, 'r') as f:
        psql = subprocess.run(['psql', '-d', 'test_sfm-db', '-U', 'postgres'], stdin=f)

    fixtures = [
        'tests/fixtures/auth.json',
        'tests/fixtures/source.json',
        'tests/fixtures/organization.json',
        'tests/fixtures/person.json',
        'tests/fixtures/violation.json',
        'tests/fixtures/membershiporganization.json',
        'tests/fixtures/membershipperson.json',
    ]

    for fixture in fixtures:
        call_command('loaddata', fixture)

    call_command('make_flattened_views', '--recreate')
    # call_command('make_search_index')


def tearDownModule():

    with connection.cursor() as conn:
        conn.execute('TRUNCATE auth_user CASCADE')
        conn.execute('TRUNCATE source_source CASCADE')
        conn.execute('TRUNCATE source_publication CASCADE')
        conn.execute('TRUNCATE organization_organization CASCADE')
        conn.execute('TRUNCATE person_person CASCADE')
        conn.execute('TRUNCATE violation_violation CASCADE')
        conn.execute('TRUNCATE membershipperson_membershipperson CASCADE')
        conn.execute('TRUNCATE membershiporganization_membershiporganization CASCADE')

class TestBase(TestCase):

    def getPage(self, url):
        client = Client()
        return client.get(url)

    def getStatusJSON(self, url):
        response = self.getPage(url)

        response_json = json.loads(response.content.decode('utf-8'))

        return response.status_code, response_json

class CountryList(TestBase):

    def test_country_list(self):
        status_code, response = self.getStatusJSON(reverse_lazy('country-list'))

        assert status_code == 200

        first_country = response[0]

        assert set(first_country.keys()) == {'geometry', 'id', 'properties', 'type', 'bbox'}
        assert first_country['id'] == 'ng'

    def test_country_list_tolerance(self):
        url = '{}?tolerance=0.0001'.format(reverse_lazy('country-list'))
        response = self.getPage(url)

        assert response.status_code == 200

    def test_country_list_bad_param(self):
        url = '{}?foo=bar'.format(reverse_lazy('country-list'))
        status_code, response = self.getStatusJSON(url)

        assert status_code == 400

        assert response['errors'][0] == "'foo' is not a valid query parameter"


class CountryDetail(TestBase):

    def test_country_detail(self):
        status_code, response = self.getStatusJSON(reverse_lazy('country-detail', args=['ng']))

        assert status_code == 200

        assert set(response.keys()) == {'name', 'title', 'description', 'events_count'}

    def test_country_detail_bad_param(self):
        url = '{}?foo=bar'.format(reverse_lazy('country-detail', args=['ng']))
        status_code, response = self.getStatusJSON(url)

        assert status_code == 400

        assert response['errors'][0] == "'foo' is not a valid query parameter"

    def test_country_zip(self):
        response = self.getPage(reverse_lazy('country-zip', args=['ng']))
        assert response.status_code == 204

    def test_country_text(self):
        response = self.getPage(reverse_lazy('country-txt', args=['ng']))
        assert response.status_code == 204


class CountryMap(TestBase):

    def test_country_map_no_at(self):
        status_code, response = self.getStatusJSON(reverse_lazy('country-map', args=['ng']))

        assert status_code == 400

        assert response['errors'][0] == "at is a required field"

    def test_country_map(self):
        url = '{}?at=2014-01-01'.format(reverse_lazy('country-map', args=['ng']))
        response = self.getPage(url)

        assert response.status_code == 200

    def test_country_map_bbox(self):
        url = '{}?bbox=11,7,9,9&at=2014-01-01'.format(reverse_lazy('country-map', args=['ng']))
        response = self.getPage(url)

        assert response.status_code == 200

    def test_country_map_bad_bbox(self):
        url = '{}?bbox=11,7,9&at=2014-01-01'.format(reverse_lazy('country-map', args=['ng']))
        status_code, response = self.getStatusJSON(url)

        assert status_code == 400

        assert response['errors'][0] == '"bbox" should be a comma separated list of four floats'

    def test_country_map_bad_bbox_value(self):
        url = '{}?bbox=11,7,9,ugh&at=2014-01-01'.format(reverse_lazy('country-map', args=['ng']))
        status_code, response = self.getStatusJSON(url)

        assert status_code == 400

        assert response['errors'][0] == '"ugh" is not a valid value for a bbox'

    def test_country_map_classification(self):
        url = '{}?classification__in=Violations of the right to life&at=2014-01-01'.format(reverse_lazy('country-map', args=['ng']))
        response = self.getPage(url)

        assert response.status_code == 200

    def test_country_map_classification_bad_operator(self):
        url = '{}?classification__foo=Violations of the right to life&at=2014-01-01'.format(reverse_lazy('country-map', args=['ng']))
        status_code, response = self.getStatusJSON(url)

        assert status_code == 400

        assert response['errors'][0] == "Invalid operator for 'classification'"


class CountryEvents(TestBase):

    def test_country_events(self):
        response = self.getPage(reverse_lazy('country-events', args=['ng']))
        assert response.status_code == 200


class CountryGeometries(TestBase):

    def test_country_geometries(self):
        response = self.getPage(reverse_lazy('country-geometry', args=['ng']))
        assert response.status_code == 200

    def test_country_geometries_tolerance(self):
        url = '{}?tolerance=0.0001'.format(reverse_lazy('country-geometry', args=['ng']))
        response = self.getPage(url)

        assert response.status_code == 200

    def test_country_geometries_classification(self):
        url = '{}?classification=4'.format(reverse_lazy('country-geometry', args=['ng']))
        response = self.getPage(url)

        assert response.status_code == 200


class OSMAutocomplete(TestBase):

    def test_country_autocomplete_no_q(self):
        status_code, response = self.getStatusJSON(reverse_lazy('osm-auto', args=['ng']))

        assert status_code == 400

        assert response['errors'][0] == 'q is a required field'

    def test_country_autocomplete(self):
        url = '{}?q=Lagos'.format(reverse_lazy('osm-auto', args=['ng']))

        status_code, response = self.getStatusJSON(url)

        assert status_code == 200

        assert len(response) == 11


class OrganizationSearch(TestBase):

    def test_org_search_no_q(self):
        status_code, response = self.getStatusJSON(reverse_lazy('organization-search', args=['ng']))

        assert status_code == 400

        assert response['errors'][0] == 'q is a required field'

#    def test_org_search(self):
#        url = '{}?q=Battalion'.format(reverse_lazy('organization-search', args=['ng']))
#
#        status_code, response = self.getStatusJSON(url)
#
#        assert status_code == 200
#
#        assert len(response['results']) == 20
#
#    def test_org_search_first_cited(self):
#        url = '{}?q=Battalion&date_first_cited__gte=2011-01-01'.format(reverse_lazy('organization-search', args=['ng']))
#
#        status_code, response = self.getStatusJSON(url)
#
#        assert status_code == 200


#class PeopleSearch(TestBase):
#
##    def test_people_search_no_q(self):
#        status_code, response = self.getStatusJSON(reverse_lazy('people-search', args=['ng']))
#
#        assert status_code == 400
#
#        assert response['errors'][0] == 'q is a required field'

#    def test_people_search(self):
#        url = '{}?q=John'.format(reverse_lazy('people-search', args=['ng']))
#
#        status_code, response = self.getStatusJSON(url)
#
#        assert status_code == 200
#
#        assert len(response['results']) == 4
#

#class EventSearch(TestBase):
#
#    def test_event_search_no_q(self):
#        status_code, response = self.getStatusJSON(reverse_lazy('event-search', args=['ng']))
#
#        assert status_code == 400
#
#        assert response['errors'][0] == 'q is a required field'
#
#    def test_event_search(self):
#        url = '{}?q=According'.format(reverse_lazy('event-search', args=['ng']))
#
#        status_code, response = self.getStatusJSON(url)
#
#        assert status_code == 200
#
#        assert len(response['results']) == 20


class CountryGeoJSON(TestBase):

    def test_country_geojson(self):
        response = self.getPage(reverse_lazy('country-geojson', args=['ng']))

        assert response.status_code == 200


#class EventDetail(TestBase):
#
#    def test_event_detail(self):
#        curs = connection.cursor()
#
#        curs.execute('''
#            SELECT id FROM violation
#        ''')
#
#        for row in curs:
#            response = self.getPage(reverse_lazy('event-detail', args=[row[0]]))
#
#            assert response.status_code == 200


class OrganizationMap(TestBase):
    
    def getRandomOrgs(self):
        curs = connection.cursor()

        curs.execute('''
            SELECT id FROM organization
            ORDER BY RANDOM()
            LIMIT 15
        ''')
        
        return curs

#    def test_org_map(self):
#
#        for row in self.getRandomOrgs():
#            url = '{}?at=2014-01-01'.format(reverse_lazy('organization-map', args=[row[0]]))
#            response = self.getPage(url)
#
#            assert response.status_code == 200
#    
#    def test_bbox(self):
#        
#        for row in self.getRandomOrgs():
#            url = '{}?at=2014-01-01&bbox=9,9,12,7'.format(reverse_lazy('organization-map', args=[row[0]]))
#            response = self.getPage(url)
#
#            assert response.status_code == 200



class OrganizationChart(TestBase):

    def test_org_chart(self):
        curs = connection.cursor()

        curs.execute('''
            SELECT id FROM organization
            ORDER BY RANDOM()
            LIMIT 15
        ''')

        for row in curs:
            url = '{}?at=2014-01-01'.format(reverse_lazy('organization-chart', args=[row[0]]))
            response = self.getPage(url)

            assert response.status_code == 200


#class OrganizationDetail(TestBase):
#
#    def test_org_detail(self):
#        curs = connection.cursor()
#
#        curs.execute('''
#            SELECT id FROM organization
#            ORDER BY RANDOM()
#            LIMIT 15
#        ''')
#
#        for row in curs:
#            response = self.getPage(reverse_lazy('organization-detail', args=[row[0]]))
#
#            assert response.status_code == 200


#class PersonDetail(TestBase):
#
#    def test_person_detail(self):
#        curs = connection.cursor()
#
#        curs.execute('''
#            SELECT id FROM person
#            ORDER BY RANDOM()
#            LIMIT 15
#        ''')
#
#        for row in curs:
#            response = self.getPage(reverse_lazy('person-detail', args=[row[0]]))
#
#            assert response.status_code == 200
