from django.test import TestCase, Client
from django.core.urlresolvers import reverse_lazy
from django.db import connection
from django.core.management import call_command
from django.contrib.auth.models import User

from source.models import Source
from person.models import Person

def setUpModule():

    call_command('loaddata', 'tests/fixtures/auth.json')
    call_command('loaddata', 'tests/fixtures/source.json')
    call_command('loaddata', 'tests/fixtures/person.json')
    call_command('loaddata', 'tests/fixtures/organization.json')
    call_command('loaddata', 'tests/fixtures/membershipperson.json')
    call_command('update_countries_plus')

def tearDownModule():

    with connection.cursor() as conn:
        conn.execute('TRUNCATE auth_user CASCADE')
        conn.execute('TRUNCATE source_source CASCADE')
        conn.execute('TRUNCATE person_person CASCADE')

class PersonTest(TestCase):

    client = Client()

    def setUp(self):
        self.user = User.objects.first()
        self.client.force_login(self.user)

    def tearDown(self):
        self.client.logout()

    def test_view_person(self):

        them = Person.objects.order_by('?')[:10]

        for person in them:
            response = self.client.get(reverse_lazy('view-person', args=[person.uuid]))

            try:
                assert response.status_code == 200
            except AssertionError as e:
                raise(e)
