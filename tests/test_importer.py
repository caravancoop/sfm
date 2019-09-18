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


@pytest.mark.django_db
def test_relationships(data_import):
    """Make sure the correct relationships between entities get imported."""
    # Test org compositions
    org_nodes = ('Alpha', 'Beta', 'Gamma', 'Delta')
    org_edges = (None, 'Alpha', 'Beta', 'Gamma')
    for node, edge in zip(org_nodes, org_edges):
        org = Organization.objects.get(
            # Orgs in the source data have trailing spaces in their names
            organizationname__value='Importer Test Organization {} Name '.format(node)
        )
        if edge:
            assert org.parent_organization.count() == 1
            expected_parent_name = 'Importer Test Organization {} Name '.format(edge)
            parent_org = org.parent_organization.first().object_ref.parent.get_value().value
            assert parent_org.name.get_value().value == expected_parent_name
        else:
            assert org.parent_organization.count() == 0
            assert org.child_organization.count() == 1

    # Test org memberships
    is_member_org = Organization.objects.get(
        organizationname__value='Is-member Organization name'
    )
    has_member_org = Organization.objects.get(
        organizationname__value='Has-member Organization name'
    )
    assert is_member_org.membershiporganizationmember_set.count() == 1
    assert has_member_org.membershiporganizationorganization_set.count() == 1

    membership = is_member_org.membershiporganizationmember_set.first().object_ref
    member_org = membership.organization.get_value().value
    assert member_org == has_member_org

    # Test chain of command
    person_nodes = org_nodes
    person_edges = person_nodes
    for node, edge in zip(person_nodes, person_edges):
        person = Person.objects.get(
            personname__value='Importer Test Person {} Name'.format(node)
        )
        assert person.memberships.count() == 1
        member_org = person.memberships.first().object_ref.organization.get_value().value
        expected_org_name = 'Importer Test Organization {} Name '.format(edge)
        assert member_org.name.get_value().value == expected_org_name
