import pytest

from django.test import TestCase, Client
from django.core.urlresolvers import reverse_lazy
from django.db import connection
from django.core.management import call_command
from django.contrib.auth.models import User

from source.models import AccessPoint
from person.models import Person
from organization.models import Organization
from violation.models import Violation, ViolationType, \
    ViolationPerpetratorClassification


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
def test_view_violation(client):

    them = Violation.objects.order_by('?')[:10]

    for violation in them:
        response = client.get(reverse_lazy('view-violation', args=[violation.uuid]))

        assert response.status_code == 200


@pytest.mark.django_db
def test_edit_violation(setUp, fake_signal):
    violation = Violation.objects.exclude(violationtype__isnull=True).order_by('?').first()

    existing_types = [v.get_value().id for v in violation.types.get_list()]
    new_types = [v.id for v in ViolationType.objects.exclude(id__in=existing_types)[:2]]

    perpetrators = [p.id for p in Person.objects.order_by('?')[:2]]
    perpetratororganizations = [o.id for o in Organization.objects.order_by('?')[:2]]
    perpetratorclassification = ViolationPerpetratorClassification.objects.order_by('?').first()

    new_sources = AccessPoint.objects.order_by('?')[:2]

    response = setUp.get(reverse_lazy('edit-violation', kwargs={'slug': violation.uuid}))

    assert response.status_code == 200

    new_source_ids = [s.uuid for s in new_sources]

    post_data = {
        'division_id': 'ocd-division/country:us',
        'division_id_source': new_source_ids,
        'startdate': '1976',
        'startdate_source': new_source_ids,
        'enddate': '2012-02-14',
        'enddate_source': new_source_ids,
        'types': new_types,
        'types_source': new_source_ids,
        'perpetrator': perpetrators,
        'perpetrator_source': new_source_ids,
        'perpetratororganization': perpetratororganizations,
        'perpetratororganization_source': new_source_ids,
        'perpetratorclassification': perpetratorclassification.id,
        'perpetratorclassification_source': new_source_ids,
        'description': violation.description.get_value().value,
        'description_source': new_source_ids,
    }

    response = setUp.post(reverse_lazy('edit-violation', kwargs={'slug': violation.uuid}), post_data)

    assert response.status_code == 302

    assert set(new_source_ids) <= {s.uuid for s in violation.description.get_sources()}

    assert violation.division_id.get_value().value == 'ocd-division/country:us'
    assert str(violation.startdate.get_value().value) == '1976'
    assert str(violation.enddate.get_value().value) == '14th February 2012'
    assert {v.get_value().value for v in violation.types.get_list()} == {v.value for v in ViolationType.objects.filter(id__in=new_types)}

    fake_signal.assert_called_with(object_id=violation.uuid, sender=Violation)
