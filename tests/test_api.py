import json

import pytest

from django.test import TestCase, Client
from django.core.urlresolvers import reverse_lazy
from django.db.models.signals import post_save
from django.core.management import call_command
from django.db import connection

from sfm_pc.signals import update_source_index, \
    update_orgname_index, update_orgalias_index, update_personname_index, \
    update_personalias_index, update_violation_index

from organization.models import OrganizationName, OrganizationAlias
from person.models import PersonName, PersonAlias
from violation.models import ViolationDescription
from source.models import Source


@pytest.mark.django_db
def test_country_list(client):
    response = client.get(reverse_lazy('country-list'))

    assert response.status_code == 200

    content = json.loads(response.content.decode('utf-8'))

    first_country = content[0]

    assert set(first_country.keys()) == {'geometry', 'id', 'properties', 'type', 'bbox'}
    assert first_country['id'] == 'ng'


@pytest.mark.django_db
def test_country_list_tolerance(client):
    url = '{}?tolerance=0.0001'.format(reverse_lazy('country-list'))
    response = client.get(url)

    assert response.status_code == 200

@pytest.mark.django_db
def test_country_list_bad_param(client):
    url = '{}?foo=bar'.format(reverse_lazy('country-list'))
    response = client.get(url)

    assert response.status_code == 400

    content = json.loads(response.content.decode('utf-8'))

    assert content['errors'][0] == "'foo' is not a valid query parameter"


@pytest.mark.django_db
def test_country_detail(client):
    response = client.get(reverse_lazy('country-detail', args=['ng']))

    assert response.status_code == 200

    content = json.loads(response.content.decode('utf-8'))

    assert set(content.keys()) == {'name', 'title', 'description', 'events_count'}


@pytest.mark.django_db
def test_country_detail_bad_param(client):
    url = '{}?foo=bar'.format(reverse_lazy('country-detail', args=['ng']))
    response = client.get(url)

    assert response.status_code == 400

    content = json.loads(response.content.decode('utf-8'))

    assert content['errors'][0] == "'foo' is not a valid query parameter"


@pytest.mark.django_db
def test_country_zip(client):
    response = client.get(reverse_lazy('country-zip', args=['ng']))
    assert response.status_code == 204


@pytest.mark.django_db
def test_country_text(client):
    response = client.get(reverse_lazy('country-txt', args=['ng']))
    assert response.status_code == 204


@pytest.mark.django_db
def test_country_map_no_at(client):
    response = client.get(reverse_lazy('country-map', args=['ng']))

    assert response.status_code == 400

    content = json.loads(response.content.decode('utf-8'))

    assert content['errors'][0] == "at is a required field"


@pytest.mark.django_db
def test_country_map(client):
    url = '{}?at=2014-01-01'.format(reverse_lazy('country-map', args=['ng']))
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_country_map_bbox(client):
    url = '{}?bbox=11,7,9,9&at=2014-01-01'.format(reverse_lazy('country-map', args=['ng']))
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_country_map_bad_bbox(client):
    url = '{}?bbox=11,7,9&at=2014-01-01'.format(reverse_lazy('country-map', args=['ng']))
    response = client.get(url)

    assert response.status_code == 400

    content = json.loads(response.content.decode('utf-8'))

    assert content['errors'][0] == '"bbox" should be a comma separated list of four floats'


@pytest.mark.django_db
def test_country_map_bad_bbox_value(client):
    url = '{}?bbox=11,7,9,ugh&at=2014-01-01'.format(reverse_lazy('country-map', args=['ng']))
    response = client.get(url)

    assert response.status_code == 400

    content = json.loads(response.content.decode('utf-8'))

    assert content['errors'][0] == '"ugh" is not a valid value for a bbox'


@pytest.mark.django_db
def test_country_map_classification(client):
    url = '{}?classification__in=Violations of the right to life&at=2014-01-01'.format(reverse_lazy('country-map', args=['ng']))
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_country_map_classification_bad_operator(client):
    url = '{}?classification__foo=Violations of the right to life&at=2014-01-01'.format(reverse_lazy('country-map', args=['ng']))
    response = client.get(url)

    assert response.status_code == 400

    content = json.loads(response.content.decode('utf-8'))

    assert content['errors'][0] == "Invalid operator for 'classification'"


@pytest.mark.django_db
def test_country_events(client):
    response = client.get(reverse_lazy('country-events', args=['ng']))
    assert response.status_code == 200


@pytest.mark.django_db
def test_country_geometries(client):
    response = client.get(reverse_lazy('country-geometry', args=['ng']))
    assert response.status_code == 200


@pytest.mark.django_db
def test_country_geometries_tolerance(client):
    url = '{}?tolerance=0.0001'.format(reverse_lazy('country-geometry', args=['ng']))
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_country_geometries_classification(client):
    url = '{}?classification=4'.format(reverse_lazy('country-geometry', args=['ng']))
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_country_autocomplete_no_q(client):
    response = client.get(reverse_lazy('osm-auto', args=['ng']))

    assert response.status_code == 400

    content = json.loads(response.content.decode('utf-8'))

    assert content['errors'][0] == 'q is a required field'


@pytest.mark.django_db
def test_country_autocomplete(client):
    url = '{}?q=Lagos'.format(reverse_lazy('osm-auto', args=['ng']))

    response = client.get(url)

    assert response.status_code == 200

    content = json.loads(response.content.decode('utf-8'))

    assert len(content) == 11


@pytest.mark.django_db
def test_org_search_no_q(client):
    response = client.get(reverse_lazy('organization-search', args=['ng']))

    assert response.status_code == 400

    content = json.loads(response.content.decode('utf-8'))

    assert content['errors'][0] == 'q is a required field'


@pytest.mark.django_db
def test_country_geojson(client):
    response = client.get(reverse_lazy('country-geojson', args=['ng']))

    assert response.status_code == 200
