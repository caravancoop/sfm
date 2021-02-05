import io
import json
import os

import pytest
from django.core.urlresolvers import reverse_lazy
from django.core.management import call_command
from django.template.defaultfilters import truncatewords

from location.models import Location


@pytest.fixture
def location_fixture_data():
    fixture_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'fixtures',
        'locations.geojson',
    )

    with open(fixture_file, 'r') as f:
        fixture_data = json.load(f)

    return fixture_data


@pytest.fixture
def initial_location(location_fixture_data):
    initial_id = location_fixture_data['features'][0]['properties']['id']
    return Location.objects.create(id=initial_id)


@pytest.fixture
def location_data_import(initial_location):
    """Perform a test location data import."""
    output = io.StringIO()
    call_command(
        'import_locations',
        location_file='tests/fixtures/locations.geojson',
        stdout=output
    )
    return output, initial_location


@pytest.fixture
def expected_entity_names(violation, emplacement):
    """
    Generate a list of related entity names that we expect to see in the
    Violation DeleteView.
    """
    return [
        emp.organization.get_value().value.name.get_value().value for emp in emplacement
    ] + [truncatewords(violation.description.get_value(), 10)]


@pytest.mark.django_db(transaction=True)
def test_location_import(location_data_import, location_fixture_data):
    _, initial_location = location_data_import

    # test location created for each feature
    assert Location.objects.count() == len(location_fixture_data['features'])

    # test admin relationships created
    l1 = Location.objects.get(adminlevel1__isnull=False)
    assert l1.sfm['location:admin_level_6'].split()[0] == l1.adminlevel1.name
    assert l1.adminlevel1.adminlevel == '6'
    assert not l1.adminlevel1.adminlevel1

    l2 = Location.objects.get(adminlevel2__isnull=False)
    assert l2.sfm['location:admin_level_4'].split()[0] == l2.adminlevel2.name
    assert l2.adminlevel2.adminlevel == '4'
    assert not l2.adminlevel2.adminlevel2

    # test existing location updated
    # TODO: Update this when we decide what updates to apply to existing locations
    assert initial_location.sfm


@pytest.mark.django_db
def test_location_related_entities(location_node, expected_entity_names):
    related_entities = location_node.related_entities
    assert len(related_entities) == len(expected_entity_names)
    assert set([entity['name'] for entity in related_entities]) == set(expected_entity_names)


@pytest.mark.django_db
def test_location_delete(setUp, location_node):
    url = reverse_lazy('delete-location', args=[location_node.id])
    response = setUp.post(url)
    assert response.status_code == 302
    with pytest.raises(Location.DoesNotExist):
        Location.objects.get(id=location_node.id)


@pytest.mark.django_db
def test_location_delete_view_with_related_entities(setUp, location_node, expected_entity_names):
    url = reverse_lazy('delete-location', args=[location_node.id])
    response = setUp.get(url)
    assert response.status_code == 200
    # Make sure all the related entities are rendered on the page.
    for entity_name in expected_entity_names:
        assert entity_name in response.content.decode('utf-8')
    # Make sure that the confirm button is disabled.
    assert 'value="Confirm" disabled' in response.content.decode('utf-8')


@pytest.mark.django_db
def test_location_delete_view_no_related_entities(setUp, location_node):
    url = reverse_lazy('delete-location', args=[location_node.id])
    response = setUp.get(url)
    assert response.status_code == 200
    # Make sure no related entities are rendered on the page.
    assert 'Related entities' not in response.content.decode('utf-8')
    # Make sure that the confirm button is enabled.
    assert 'disabled' not in response.content.decode('utf-8')


@pytest.mark.django_db
def test_location_views_with_negative_ids(setUp):
    # Make sure we can view locations with negative IDs.
    location = Location.objects.create(
        id=-1,
        name="Test location",
        division_id='ocd-division/country:mx',
        feature_type='relation'
    )
    list_url = reverse_lazy('list-location') + '?q=-1'
    list_response = setUp.get(list_url)
    assert list_response.status_code == 200
    assert location in list_response.context['object_list']

    detail_url = reverse_lazy('view-location', args=[location.id])
    detail_response = setUp.get(detail_url)
    assert detail_response.status_code == 200
