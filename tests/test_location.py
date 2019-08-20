import pytest
from django.core.urlresolvers import reverse_lazy
from django.template.defaultfilters import truncatewords

from location.models import Location


@pytest.fixture
def expected_entity_names(violation, emplacement):
    """
    Generate a list of related entity names that we expect to see in the
    Violation DeleteView.
    """
    return [
        emp.organization.get_value().value.name.get_value().value for emp in emplacement
    ] + [truncatewords(violation.description.get_value(), 10)]


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
    assert 'disabled' in response.content.decode('utf-8')


@pytest.mark.django_db
def test_location_delete_view_no_related_entities(setUp, location_node):
    url = reverse_lazy('delete-location', args=[location_node.id])
    response = setUp.get(url)
    assert response.status_code == 200
    # Make sure no related entities are rendered on the page.
    assert 'Related entities' not in response.content.decode('utf-8')
    # Make sure that the confirm button is enabled.
    assert 'disabled' not in response.content.decode('utf-8')
