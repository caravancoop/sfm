import pytest

from django.test import TestCase, Client
from django.core.urlresolvers import reverse_lazy
from django.db import connection
from django.core.management import call_command
from django.contrib.auth.models import User

from source.models import Source
from violation.models import Violation


@pytest.mark.django_db
def test_view_violation(client):

    them = Violation.objects.order_by('?')[:10]

    for violation in them:
        response = client.get(reverse_lazy('view-violation', args=[violation.id]))

        try:
            assert response.status_code == 200
        except AssertionError as e:
            print(viol_id)
            print(response.content)
            raise(e)
