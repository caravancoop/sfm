import pytest

from django.test import TestCase, Client
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db import connection
from django.core.management import call_command

from organization.models import Organization, OrganizationName, OrganizationAlias
from source.models import Source

from sfm_pc.signals import update_orgname_index, update_orgalias_index, \
    update_source_index


@pytest.fixture()
@pytest.mark.django_db(transaction=True)
def setUp(django_db_setup, client, request):
    user = User.objects.first()
    client.force_login(user)

    @request.addfinalizer
    def tearDown():
        client.logout()

    return client


@pytest.mark.django_db
def test_view_organization(client):

    them = Organization.objects.order_by('?')[:10]
    for it in them:
        response = client.get(reverse_lazy('view-organization', args=[it.uuid]))

        assert response.status_code == 200


@pytest.mark.django_db
def test_edit_organization(setUp):
    org = Organization.objects.exclude(child_organization__isnull=True,
                                       parent_organization__isnull=True).first()

    response = setUp.get(reverse_lazy('edit-organization', args=[org.uuid]))

    assert response.status_code == 200

    new_sources = Source.objects.order_by('?')[:2]
    new_source_ids = [s.uuid for s in new_sources]

    post_data = {
        'name': org.name.get_value().value,
        'name_source': new_source_ids,
        'aliases': [a.get_value().id for a in org.aliases.get_list()] + ['floop'],
        'aliases_source': new_source_ids
    }

    response = setUp.post(reverse_lazy('edit-organization', args=[org.uuid]),
                          post_data)

    assert response.status_code == 302

    assert set(new_sources) <= set(org.name.get_sources())
    assert set(new_sources) <= set(org.aliases.get_list()[0].get_sources())
    assert 'floop' in [a.get_value().value for a in org.aliases.get_list()]


@pytest.mark.django_db
def test_edit_relationship(setUp):
    org = Organization.objects.exclude(child_organization__isnull=True,
                                       parent_organization__isnull=True).first()

    response = setUp.get(reverse_lazy('edit-organization', args=[org.uuid]))

    assert response.status_code == 200

    new_sources = Source.objects.order_by('?')[:2]
    new_source_ids = [s.uuid for s in new_sources]

    post_data = {
        'parent': org,
        'parent_sources':
    }
