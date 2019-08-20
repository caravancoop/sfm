import json
from uuid import uuid4

import pytest

from django.test import TestCase, Client
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db import connection
from django.core.management import call_command
from django.db.models import Count

from reversion.models import Version

from source.models import Source, AccessPoint
from person.models import Person


@pytest.mark.django_db
def test_create_source(setUp, update_index_mock):

    response = setUp.get(reverse_lazy('create-source'), follow=True)
    assert response.status_code == 200

    post_data = {
        'publication': 'Test Publication Title',
        'publication_country': 'Nigeria',
        'title': 'Test Source Title',
        'source_url': 'http://test.com/',
        'published_on': '2014-01-01',
        'comment': 'Test change',
        'uuid': str(uuid4()),
    }

    response = setUp.post(reverse_lazy('create-source'), post_data, follow=True)
    assert response.status_code == 200
    update_index_mock.assert_called_once_with('sources', post_data['uuid'])

    source = Source.objects.get(publication='Test Publication Title')

    assert source.title == post_data['title']
    assert source.source_url == post_data['source_url']

    revision = Version.objects.get_for_object(source).first().revision
    assert revision.comment == 'Test change'


@pytest.mark.django_db
def test_create_accesspoint(setUp, sources):
    source = sources[0]

    response = setUp.get(reverse_lazy('add-access-point',
                                            kwargs={'source_id': str(source.uuid)}))

    assert response.status_code == 200

    post_data = {
        'archive_url': 'https://web.archive.org/',
        'accessed_on': '2018-04-01',
        'page_number': '',
        'comment': 'This is a big change'
    }

    response = setUp.post(reverse_lazy('add-access-point',
                                                kwargs={'source_id': str(source.uuid)}),
                                post_data,
                                follow=True)

    assert response.status_code == 200

    accesspoint = AccessPoint.objects.get(source__uuid=source.uuid,
                                            accessed_on='2018-04-01')

    assert accesspoint.archive_url == 'https://web.archive.org/'

    revision = Version.objects.get_for_object(accesspoint).first().revision
    assert revision.comment == 'This is a big change'


@pytest.mark.django_db
def test_update_source(setUp, sources, update_index_mock):
    source = sources[0]

    response = setUp.get(reverse_lazy('update-source', kwargs={'pk': source.uuid}))
    assert response.status_code == 200

    post_data = {
        'publication': 'Test Publication Title',
        'publication_country': source.publication_country,
        'title': source.title,
        'source_url': source.source_url,
        'published_on': source.published_on,
        'comment': 'Test change',
        'uuid': str(source.uuid),
    }

    response = setUp.post(reverse_lazy('update-source', kwargs={'pk': source.uuid}), post_data, follow=True)

    assert response.status_code == 200
    update_index_mock.assert_called_once_with('sources', post_data['uuid'])

    source = Source.objects.get(uuid=source.uuid)

    assert source.publication == 'Test Publication Title'

    revision = Version.objects.get_for_object(source).first().revision
    assert revision.comment == 'Test change'


@pytest.mark.django_db
def test_update_accesspoint(setUp, access_points):
    accesspoint = access_points[0]

    response = setUp.get(reverse_lazy('update-access-point',
                                            kwargs={'source_id': accesspoint.source.uuid,
                                                    'pk': accesspoint.uuid}))
    assert response.status_code == 200

    post_data = {
        'archive_url': 'https://web.archive.org/',
        'accessed_on': '2018-04-01',
        'page_number': accesspoint.page_number,
        'comment': 'This is a big change'
    }

    response = setUp.post(reverse_lazy('update-access-point',
                                            kwargs={'source_id': accesspoint.source.uuid,
                                                    'pk': accesspoint.uuid}),
                                post_data,
                                follow=True)
    assert response.status_code == 200

    accesspoint = AccessPoint.objects.get(uuid=accesspoint.uuid)
    assert accesspoint.archive_url == 'https://web.archive.org/'

    revision = Version.objects.get_for_object(accesspoint).first().revision
    assert revision.comment == 'This is a big change'


@pytest.mark.django_db
def test_autocomplete(setUp):
    url = '{}?q=Nigeria'.format(reverse_lazy('source-autocomplete'))

    response = setUp.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_view_source(setUp, sources, access_points):
    source = sources[0]
    url = reverse_lazy('view-source', args=[source.uuid])
    response = setUp.get(url)
    assert response.status_code == 200
    assert 'Select an access point' in response.content.decode('utf-8')
    # Make sure that all of the access points are represented as options on the page
    assert source.accesspoint_set.count() > 0
    for access_point in source.accesspoint_set.all():
        assert str(access_point.uuid) in response.content.decode('utf-8')


@pytest.mark.django_db
def test_view_source_with_evidence(setUp, sources, access_points):
    source = Source.objects.annotate(count=Count('accesspoint')).filter(count__gte=1).first()
    access_point = source.accesspoint_set.first()
    url = reverse_lazy('view-source-with-evidence', args=[source.uuid, access_point.uuid])
    response = setUp.get(url)
    assert response.status_code == 200
    assert 'evidences the following records:' in response.content.decode('utf-8')


@pytest.mark.django_db
def test_view_source_with_no_evidence(setUp, sources):
    source = Source.objects.annotate(count=Count('accesspoint')).filter(count=0).first()
    url = reverse_lazy('view-source', args=[source.uuid])
    response = setUp.get(url)
    assert response.status_code == 200
    assert 'No access points found' in response.content.decode('utf-8')
