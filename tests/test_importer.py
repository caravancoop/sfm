import os
import csv
import io

import pytest
from django.core.management import call_command

from organization.models import Organization
from person.models import Person
from violation.models import Violation


@pytest.fixture(scope='module')
def data_folder():
    """The directory where importer fixture data is stored."""
    return 'tests/fixtures/importer'


@pytest.fixture
def data_import(data_folder, update_index_mock, fake_signal):
    """Perform a test data import."""
    output = io.StringIO()
    call_command('import_google_doc', folder=data_folder, stdout=output)
    return output


@pytest.mark.django_db
def test_no_sources_missing(data_import):
    assert 'does not have sources' not in data_import.getvalue()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'entity_name,Model',
    [('organization', Organization), ('person', Person), ('event', Violation)]
)
def test_number_of_imported_entities(entity_name, Model, data_import, data_folder):
    with open(os.path.join(data_folder, entity_name + '.csv')) as fobj:
        reader = csv.reader(fobj)
        raw_records = list(reader)
    records = Model.objects.all()
    assert len(records) == len(raw_records[1:])


@pytest.mark.django_db
def test_sources(data_import):
    """
    All records in the source data should have their own sources. Check all
    attributes of all entities and confirm that each has its own source.
    """
    shared_source_attrs = ['division_id']  # Attributes that share sources
    seen_sources = set()
    for Model in [Person, Organization]:
        for entity in Model.objects.all():
            seen_attrs = []  # Keep track of attributes we've seen, for debugging
            for attr in dir(entity):
                if attr not in shared_source_attrs:
                    try:
                        entity_attr = getattr(entity, attr)
                    except AttributeError:
                        # Some built-in attributes are not accessible from model
                        # instances, so skip them
                        continue
                    if hasattr(entity_attr, 'get_sources') and entity_attr.get_value():
                        sources = set(entity_attr.get_sources())
                        assert not sources & seen_sources
                        seen_sources = seen_sources | sources
                        seen_attrs.append(attr)
