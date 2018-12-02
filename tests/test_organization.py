import pytest

from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User

from organization.models import Organization, OrganizationAlias, \
    OrganizationClassification
from source.models import AccessPoint
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

    new_sources = AccessPoint.objects.order_by('?')[:2]
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
def test_create_organization(setUp, fake_signal):

    response = setUp.get(reverse_lazy('create-organization'))

    assert response.status_code == 200

    new_sources = AccessPoint.objects.order_by('?')[:2]
    new_source_ids = [s.uuid for s in new_sources]

    classifications = OrganizationClassification.objects.order_by('?')[:2]
    classification_ids = [c.id for c in classifications]

    post_data = {
        'name': 'Big, big guys',
        'name_source': new_source_ids,
        'aliases': ['floop', 'flooper'],
        'aliases_source': new_source_ids,
        'classification': classification_ids,
        'classification_source': new_source_ids,
        'division_id': 'ocd-division/country:us',
        'division_id_source': new_source_ids,
        'firstciteddate': '1999',
        'firstciteddate_source': new_source_ids,
        'lastciteddate': '2001',
        'lastciteddate_source': new_source_ids,
        'realstart': 'on',
        'open_ended': 'N',
        'open_ended_source': new_source_ids,
    }

    response = setUp.post(reverse_lazy('create-organization'),
                          post_data)

    assert response.status_code == 302

    organization = Organization.objects.get(organizationname__value='Big, big guys')

    assert set(new_sources) <= set(organization.name.get_sources())
    assert set(new_sources) <= set(organization.aliases.get_list()[0].get_sources())
    assert 'floop' in [a.get_value().value for a in organization.aliases.get_list()]

    fake_signal.assert_called_with(object_id=str(organization.uuid),
                                   sender=Organization)


@pytest.mark.django_db
def test_edit_composition(setUp, fake_signal):
    org1, org2 = Organization.objects.exclude(child_organization__isnull=True)\
                                     .exclude(parent_organization__isnull=True)[:2]

    first_comp = org1.parent_organization.first().object_ref

    response = setUp.get(reverse_lazy('edit-organization-composition',
                                      args=[org1.uuid, first_comp.id]))

    assert response.status_code == 200

    new_sources = AccessPoint.objects.order_by('?')[:2]
    new_source_ids = [s.uuid for s in new_sources]

    post_data = {
        'parent': org1.id,
        'parent_source': new_source_ids,
        'child': org2.id,
        'child_source': new_source_ids,
        'classification': 'Command',
        'classification_source': new_source_ids,
    }

    response = setUp.post(reverse_lazy('edit-organization-composition',
                                       args=[org1.uuid, first_comp.id]),
                          post_data)

    assert response.status_code == 302

    assert first_comp.parent.get_value().value == org1
    assert first_comp.child.get_value().value == org2
    assert [s for s in first_comp.child.get_sources()] == [s for s in first_comp.parent.get_sources()]

    fake_signal.assert_called_with(object_id=first_comp.id,
                                   sender=Composition)

@pytest.mark.django_db
def test_create_relationship(setUp, fake_signal):
    org1, org2 = Organization.objects.exclude(child_organization__isnull=True)\
                                     .exclude(parent_organization__isnull=True)[:2]

    response = setUp.get(reverse_lazy('create-organization-composition',
                                      args=[org1.uuid]))

    assert response.status_code == 200

    new_sources = AccessPoint.objects.order_by('?')[:2]
    new_source_ids = [s.uuid for s in new_sources]

    post_data = {
        'parent': org1.id,
        'parent_source': new_source_ids,
        'child': org2.id,
        'child_source': new_source_ids,
        'classification': 'Command',
        'classification_source': new_source_ids,
    }

    response = setUp.post(reverse_lazy('create-organization-composition',
                                       args=[org1.uuid]),
                          post_data)

    assert response.status_code == 302

    composition = Composition.objects.filter(compositionparent__value=org1,
                                             compositionchild__value=org2).first()

    assert composition.parent.get_value().value == org1
    assert composition.child.get_value().value == org2
    assert {s for s in composition.child.get_sources()} == {s for s in composition.parent.get_sources()}

    fake_signal.assert_called_with(object_id=composition.id,
                                   sender=Composition)
