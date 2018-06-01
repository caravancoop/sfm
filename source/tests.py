from uuid import UUID
import json

from django.test import TestCase, Client
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db import connection
from django.core.management import call_command

from source.models import Source

from sfm_pc.signals import update_source_index

def setUpModule():

    post_save.disconnect(receiver=update_source_index, sender=Source)

    call_command('loaddata', 'tests/fixtures/auth.json')
    call_command('loaddata', 'tests/fixtures/source.json')

def tearDownModule():

    with connection.cursor() as conn:
        conn.execute('TRUNCATE auth_user CASCADE')
        conn.execute('TRUNCATE source_source CASCADE')

class SourceTest(TestCase):

    client = Client()

    def setUp(self):
        self.user = User.objects.first()
        self.client.force_login(self.user)

    def tearDown(self):
        self.client.logout()

    def test_create_source(self):

        response = self.client.get(reverse_lazy('create-source'), follow=True)

        assert 'source_id' not in list(self.client.session.keys())

        post_data = {
            'publication': 'Test Publication Title',
            'publication_country': 'Nigeria',
            'title': 'Test Source Title',
            'source_url': 'http://test.com/',
            'published_on': '2014-01-01',
            'accessed_on': '2016-01-01',
        }

        response = self.client.post(reverse_lazy('create-source'), post_data, follow=True)

        assert response.status_code == 200

        source = Source.objects.get(publication='Test Publication Title')

        assert source.title == post_data['title']
        assert source.source_url == post_data['source_url']

    def test_autocomplete(self):
        url = '{}?q=Nigeria'.format(reverse_lazy('source-autocomplete'))

        response = self.client.get(url)

        assert response.status_code == 200
        response_json = json.loads(response.content.decode('utf-8'))

        assert len(response_json) == 421

    def test_pub_autocomplete(self):
        url = '{}?q=Nigeria'.format(reverse_lazy('publications-autocomplete'))

        response = self.client.get(url)

        assert response.status_code == 200
        response_json = json.loads(response.content.decode('utf-8'))

        assert len(response_json) == 95
