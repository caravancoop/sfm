import pytest

from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User

from organization.models import Organization
from source.models import Source
from composition.models import Composition


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
def test_edit_organization(setUp, fake_signal):
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

    fake_signal.assert_called_with(object_id=org.uuid,
                                   sender=Organization)


@pytest.mark.django_db
def test_edit_relationship(setUp, fake_signal):
    org1, org2 = Organization.objects.exclude(child_organization__isnull=True)\
                                     .exclude(parent_organization__isnull=True)[:2]

    first_comp = org1.parent_organization.first().object_ref

    response = setUp.get(reverse_lazy('edit-organization-relationships',
                                      args=[org1.uuid, first_comp.id]))

    assert response.status_code == 200

    new_sources = Source.objects.order_by('?')[:2]
    new_source_ids = [s.uuid for s in new_sources]

    post_data = {
        'parent': org1.id,
        'parent_source': new_source_ids,
        'child': org2.id,
        'child_source': new_source_ids,
        'classification': 'Command',
        'classification_source': new_source_ids,
    }

    response = setUp.post(reverse_lazy('edit-organization-relationships',
                                       args=[org1.uuid, first_comp.id]),
                          post_data)

    assert response.status_code == 302

    assert first_comp.parent.get_value().value == org1
    assert first_comp.child.get_value().value == org2
    assert [s for s in first_comp.child.get_sources()] == [s for s in first_comp.parent.get_sources()]

    fake_signal.assert_called_with(object_id=first_comp.id,
                                   sender=Composition)
