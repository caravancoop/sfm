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
            assert response.status_code == 200

    def test_edit_person(self):
        person = Person.objects.exclude(personalias__isnull=True).order_by('?').first()
        new_sources = Source.objects.order_by('?')[:2]

        response = self.client.get(reverse_lazy('edit-person', kwargs={'slug': person.uuid}))

        assert response.status_code == 200

        new_source_ids = [s.uuid for s in new_sources]

        post_data = {
            'name': person.name.get_value(),
            'name_source': new_source_ids,
            'aliases': [p.get_value().id for p in person.aliases.get_list()] + ['Foo'],
            'aliases_source': new_source_ids,
            'division_id': 'ocd-division/country:us',
            'division_id_source': new_source_ids,
            'date_of_birth': '1976',
            'date_of_birth_source': new_source_ids,
            'date_of_death': '2012-02-14',
            'date_of_death_source': new_source_ids,
            'modified_fields': ['name', 'aliases', 'division_id', 'date_of_birth', 'date_of_death'],
        }

        response = self.client.post(reverse_lazy('edit-person', kwargs={'slug': person.uuid}), post_data, follow=True)

        assert response.status_code == 200

        assert set(new_source_ids) <= {s.uuid for s in person.name.get_value().sources.all()}

        assert 'Foo' in [p.get_value().value for p in person.aliases.get_list()]

        for alias in person.aliases.get_list():
            assert set(new_source_ids) <= {a.uuid for a in alias.get_value().sources.all()}

        assert person.division_id.get_value().value == 'ocd-division/country:us'
        assert str(person.date_of_birth.get_value().value) == '1976'
        assert str(person.date_of_death.get_value().value) == '14th February 2012'

    def test_no_source_one_value(self):
        person = Person.objects.exclude(personalias__isnull=True).order_by('?').first()

        post_data = {
            'name': person.name.get_value(),
            'modified_fields': ['name'],
        }

        response = self.client.post(reverse_lazy('edit-person', kwargs={'slug': person.uuid}), post_data, follow=True)

        assert '"name" requires a new source' in response.context['form'].errors['name']

    def test_no_source_multiple_value(self):
        person = Person.objects.exclude(personalias__isnull=True).order_by('?').first()

        post_data = {
            'aliases': person.name.get_value(),
            'modified_fields': ['aliases'],
        }

        response = self.client.post(reverse_lazy('edit-person', kwargs={'slug': person.uuid}), post_data, follow=True)

        assert '"aliases" requires a new source' in response.context['form'].errors['aliases']

    def test_remove_value(self):
        person = Person.objects.exclude(personalias__isnull=True).order_by('?').first()

        aliases = [a.get_value().id for a in person.aliases.get_list()]
        removed = aliases.pop()

        new_sources = Source.objects.order_by('?')[:2]
        new_source_ids = [s.uuid for s in new_sources]

        post_data = {
            'name': person.name.get_value().value,
            'name_sources': new_source_ids,
            'aliases': aliases,
            'aliases_source': new_source_ids,
            'modified_fields': ['aliases'],
        }

        response = self.client.post(reverse_lazy('edit-person', kwargs={'slug': person.uuid}), post_data, follow=True)

        assert response.status_code == 200

        assert aliases == [a.get_value().id for a in person.aliases.get_list()]

    def test_remove_value_same_sources(self):
        person = Person.objects.exclude(personalias__isnull=True).order_by('?').first()

        aliases = [a.get_value().id for a in person.aliases.get_list()]
        removed = aliases.pop()

        sources = set()

        for alias in person.aliases.get_list():
            for source in alias.get_value().sources.all():
                sources.add(source.uuid)

        post_data = {
            'name': person.name.get_value().value,
            'name_sources': list(sources),
            'aliases': aliases,
            'aliases_source': list(sources),
            'modified_fields': ['aliases'],
        }

        response = self.client.post(reverse_lazy('edit-person', kwargs={'slug': person.uuid}), post_data, follow=True)

        assert response.status_code == 200

        assert aliases == [a.get_value().id for a in person.aliases.get_list()]

    def test_remove_all_values(self):
        person = Person.objects.exclude(personalias__isnull=True).order_by('?').first()

        sources = [s.uuid for s in person.name.get_value().sources.all()]

        post_data = {
            'name': person.name.get_value().value,
            'name_source': sources,
            'aliases': [],
            'aliases_source': sources,
            'modified_fields': ['aliases'],
        }

        response = self.client.post(reverse_lazy('edit-person', kwargs={'slug': person.uuid}), post_data, follow=True)

        assert response.status_code == 200

        assert [] == [a.get_value().id for a in person.aliases.get_list()]
