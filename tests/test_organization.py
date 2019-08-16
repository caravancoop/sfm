import pytest

from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User

from organization.models import Organization, OrganizationAlias, \
    OrganizationClassification
from source.models import AccessPoint
from composition.models import Composition


@pytest.mark.django_db
def test_view_organization(full_organizations, client):

    them = Organization.objects.order_by('?')[:10]
    for it in them:
        response = client.get(reverse_lazy('view-organization', args=[it.uuid]))

        assert response.status_code == 200


@pytest.mark.django_db
def test_edit_organization(setUp,
                           full_organizations,
                           fake_signal,
                           new_access_points):

    org = Organization.objects.exclude(child_organization__isnull=True,
                                       parent_organization__isnull=True).first()

    response = setUp.get(reverse_lazy('edit-organization', args=[org.uuid]))

    assert response.status_code == 200

    new_source_ids = [s.uuid for s in new_access_points]

    post_data = {
        'name': org.name.get_value().value,
        'name_source': new_source_ids,
        'aliases': [a.get_value().id for a in org.aliases.get_list()] + ['floop'],
        'aliases_source': new_source_ids
    }

    response = setUp.post(reverse_lazy('edit-organization', args=[org.uuid]),
                          post_data)

    assert response.status_code == 302

    assert set(new_access_points) <= set(org.name.get_sources())
    assert set(new_access_points) <= set(org.aliases.get_list()[0].get_sources())
    assert 'floop' in [a.get_value().value for a in org.aliases.get_list()]

    fake_signal.assert_called_with(object_id=org.uuid,
                                   sender=Organization)


@pytest.mark.django_db
def test_create_organization(setUp,
                             new_access_points,
                             fake_signal,
                             organization_classifications):

    response = setUp.get(reverse_lazy('create-organization'))

    assert response.status_code == 200

    new_source_ids = [s.uuid for s in new_access_points]

    classification_ids = [c.id for c in organization_classifications]

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

    assert set(new_access_points) <= set(organization.name.get_sources())
    assert set(new_access_points) <= set(organization.aliases.get_list()[0].get_sources())
    assert 'floop' in [a.get_value().value for a in organization.aliases.get_list()]

    fake_signal.assert_called_with(object_id=str(organization.uuid),
                                   sender=Organization)


@pytest.mark.django_db
def test_edit_composition(setUp,
                          full_organizations,
                          new_access_points,
                          fake_signal):

    parent, middle, _ = full_organizations

    first_comp = middle.parent_organization.first().object_ref

    response = setUp.get(reverse_lazy('edit-organization-composition',
                                      args=[parent.uuid, first_comp.id]))

    assert response.status_code == 200

    new_source_ids = [s.uuid for s in new_access_points]

    post_data = {
        'parent': parent.id,
        'parent_source': new_source_ids,
        'child': middle.id,
        'child_source': new_source_ids,
        'classification': 'Command',
        'classification_source': new_source_ids,
    }

    response = setUp.post(reverse_lazy('edit-organization-composition',
                                       args=[parent.uuid, first_comp.id]),
                          post_data)

    assert response.status_code == 302

    assert first_comp.parent.get_value().value == parent
    assert first_comp.child.get_value().value == middle
    assert [s for s in first_comp.child.get_sources()] == [s for s in first_comp.parent.get_sources()]

    fake_signal.assert_called_with(object_id=first_comp.id,
                                   sender=Composition)

@pytest.mark.django_db
def test_create_relationship(setUp,
                             organizations,
                             new_access_points,
                             fake_signal):

    parent, middle, _ = organizations

    response = setUp.get(reverse_lazy('create-organization-composition',
                                      args=[parent.uuid]))

    assert response.status_code == 200

    new_source_ids = [s.uuid for s in new_access_points]

    post_data = {
        'parent': parent.id,
        'parent_source': new_source_ids,
        'child': middle.id,
        'child_source': new_source_ids,
        'classification': 'Command',
        'classification_source': new_source_ids,
    }

    response = setUp.post(reverse_lazy('create-organization-composition',
                                       args=[parent.uuid]),
                          post_data)

    assert response.status_code == 302

    composition = Composition.objects.filter(compositionparent__value=parent,
                                             compositionchild__value=middle).first()

    assert composition.parent.get_value().value == parent
    assert composition.child.get_value().value == middle
    assert {s for s in composition.child.get_sources()} == {s for s in composition.parent.get_sources()}

    fake_signal.assert_called_with(object_id=composition.id,
                                   sender=Composition)

def is_tab_active(page, tab_name):
    if 'primary">{}'.format(tab_name) in page.content.decode('utf-8'):
        return True
    else:
        return False


@pytest.mark.django_db
def test_organization_edit_buttons(setUp,
                                   full_organizations,
                                   membership_person,
                                   membership_organization):
     org = full_organizations[0]
     composition = Composition.objects.first()
     person = org.personnel[0]
     association = org.associations[0]
     emplacement = org.emplacements[0]

     assert is_tab_active(setUp.get(reverse_lazy('edit-organization', args=[org.uuid])),
                          'Basics') == True

     assert is_tab_active(setUp.get(reverse_lazy('create-organization-composition', args=[org.uuid])),
                          'Relationships') == True
     assert is_tab_active(setUp.get(reverse_lazy('edit-organization-composition', args=[org.uuid, composition.pk])),
                          'Relationships') == True

     assert is_tab_active(setUp.get(reverse_lazy('create-organization-personnel', args=[org.uuid])),
                          'Personnel') == True
     assert is_tab_active(setUp.get(reverse_lazy('edit-organization-personnel', args=[org.uuid, person.pk])),
                          'Personnel') == True

     assert is_tab_active(setUp.get(reverse_lazy('create-organization-emplacement', args=[org.uuid])),
                          'Locations') == True
     assert is_tab_active(setUp.get(reverse_lazy('edit-organization-emplacement', args=[org.uuid, emplacement.pk])),
                          'Locations') == True

     assert is_tab_active(setUp.get(reverse_lazy('create-organization-association', args=[org.uuid])),
                          'Locations') == True
     assert is_tab_active(setUp.get(reverse_lazy('edit-organization-association', args=[org.uuid, association.pk])),
                          'Locations') == True

     assert is_tab_active(setUp.get(reverse_lazy('create-organization-membership', args=[org.uuid])),
                          'Relationships') == True
