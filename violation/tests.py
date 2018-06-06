from django.test import TestCase, Client
from django.core.urlresolvers import reverse_lazy
from django.db import connection
from django.core.management import call_command
from django.contrib.auth.models import User

from source.models import Source

def setUpModule():

    call_command('loaddata', 'tests/fixtures/auth.json')
    call_command('loaddata', 'tests/fixtures/source.json')
    call_command('loaddata', 'tests/fixtures/organization.json')
    call_command('loaddata', 'tests/fixtures/person.json')
    call_command('loaddata', 'tests/fixtures/violation.json')
    call_command('update_countries_plus')

def tearDownModule():

    with connection.cursor() as conn:
        conn.execute('TRUNCATE auth_user CASCADE')
        conn.execute('TRUNCATE source_source CASCADE')
        conn.execute('TRUNCATE violation_violation CASCADE')

class ViolationTest(TestCase):

    client = Client()

    def setUp(self):
        self.user = User.objects.first()
        self.client.force_login(self.user)
        self.source = Source.objects.first()

        session = self.client.session
        session['source_id'] = str(self.source.uuid)
        session.save()

    def tearDown(self):
        self.client.logout()

    def test_view_violation(self):

        for viol_id in range(13, 23):
            response = self.client.get(reverse_lazy('view-violation', args=[viol_id]))

            try:
                assert response.status_code == 200
            except AssertionError as e:
                print(viol_id)
                print(response.content)
                raise(e)
