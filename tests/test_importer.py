import os
import csv
import collections
import io

import pytest
from django.core.management import call_command
from django.db.models import Q

from organization.models import Organization, OrganizationRealStart, \
    OrganizationOpenEnded
from person.models import Person
from personextra.models import PersonExtra
from personbiography.models import PersonBiography
from violation.models import Violation
from source.models import Source, AccessPoint


@pytest.fixture(scope='module')
def data_folder():
    """The directory where importer fixture data is stored."""
    return 'tests/fixtures/importer'


@pytest.fixture
def data_import(location_data_import, data_folder):
    """Perform a test data import."""
    output = io.StringIO()
    call_command('import_google_doc', folder=data_folder, stdout=output)
    return output


@pytest.mark.django_db
def test_no_sources_missing(data_import):
    assert 'does not have sources' not in data_import.getvalue()
    assert 'does not have confidence' not in data_import.getvalue()
    assert 'did not have sources' not in data_import.getvalue()
    assert 'did not have a confidence or source' not in data_import.getvalue()
    assert 'has no confidence' not in data_import.getvalue()


@pytest.mark.django_db
@pytest.mark.parametrize('entity_name,Model', [
    ('units', Organization),
    ('persons', Person),
    ('persons_extra', (PersonExtra, PersonBiography)),
    ('incidents', Violation),
    ('sources', AccessPoint),
])
def test_number_of_imported_entities(entity_name, Model, data_import, data_folder):
    with open(os.path.join(data_folder, entity_name + '.csv')) as fobj:
        reader = csv.DictReader(fobj)
        raw_records = list(reader)
        # Exclude entities with a non-final status
        if entity_name in ('units', 'persons', 'incidents'):
            singular_entity_name = entity_name[:-1]
            id_field = singular_entity_name + ':id:admin'
            status_field = singular_entity_name + ':status:admin'
            comments_field = singular_entity_name + ':comments:admin'
            num_raw_records = len(
                set(
                    rec[id_field] for rec in raw_records
                    if rec[status_field] == '3'
                    and 'duplicate' not in rec[comments_field].lower()
                )
            )
        else:
            num_raw_records = len(raw_records)
    if type(Model) == tuple:
        num_records = sum(Mod.objects.count() for Mod in Model)
    else:
        num_records = Model.objects.count()
    assert num_records == num_raw_records


@pytest.mark.django_db
def test_all_data_points_have_sources(data_import):
    def check_for_sources(complex_field):
        unsourced_models = (OrganizationRealStart, OrganizationOpenEnded)
        value = entity_attr.get_value()

        if value:
            if any(isinstance(value, Model) for Model in unsourced_models):
                assert not entity_attr.get_sources()
            else:
                try:
                    assert entity_attr.get_sources()
                except AssertionError:
                    return value

    errors = []

    for Model in [Person, Organization, Violation]:
        for entity in Model.objects.all():
            for entity_attr in getattr(entity, 'complex_fields', []):
                error = check_for_sources(entity_attr)
                if error:
                    errors.append(error)

            for entity_attrs in getattr(entity, 'complex_lists', []):
                for entity_attr in entity_attrs.get_list():
                    error = check_for_sources(entity_attr)
                    if error:
                        errors.append(error)

    if errors:
        raise AssertionError('The following data points are unsourced:\n{}'.format(errors))


@pytest.mark.django_db
def test_sources_only_created_for_data_points_they_evidence(data_import, data_folder):
    '''
    In https://github.com/security-force-monitor/sfm-cms/issues/637, we
    discovered a bug in which sources were multiplied when derived from the
    original, mutable source list, rather than a shallow copy. Test data was
    created such that we could test sources weren't inadvertantly assigned
    to unrelated attributes. This test asserts that extraneous sources are not
    created, based on that data.

    N.b., there are not constraints on what data points can share sources
    outside of this test.
    '''
    sourced_attributes = [
        attr for attr in dir(AccessPoint.objects.first())
        if attr.endswith('_related')
    ]

    access_points_for_test = Q()

    for substring in ('alpha', 'beta', 'gamma', 'delta', 'is-member', 'has-member'):
        access_points_for_test |= Q(source__title__icontains=substring)

    for access_point in AccessPoint.objects.filter(access_points_for_test):
        related_objects = []

        for attr in sourced_attributes:
            related_objects += [
                obj for obj in getattr(access_point, attr).all() if obj
            ]

        related_obj_types = set(obj._meta.object_name for obj in related_objects)

        if len(related_obj_types) > 1:
            # Data points can be evidenced directly through an accompanying
            # source field and indirectly through a related field, e.g., if
            # Unit A is the parent of Unit B, the source for Unit A's name is
            # also added to that composition.
            #
            # These sets are groupings of attributes that we expect could share
            # sources based on on our practice of direct and indirect sourcing.
            # The success of this test depends on the particular assignment of
            # sources in the test data. If the test data or data model changes,
            # these sets may need to be adjusted.
            permitted_org_set = set([
               'CompositionChild',
               'CompositionParent',
               'EmplacementOrganization',
               'EmplacementSite',
               'EmplacementStartDate',
               'MembershipOrganizationMember',
               'MembershipOrganizationOrganization',
               'MembershipPersonMember',
               'MembershipPersonOrganization',
               'OrganizationName',
            ])
            permitted_person_set = set([
                'PersonName',
            ])
            permitted_incident_set = set([
                'ViolationAdminLevel1',
                'ViolationAdminLevel2',
                'ViolationDescription',
                'ViolationDivisionId',
                'ViolationEndDate',
                'ViolationFirstAllegation',
                'ViolationLastUpdate',
                'ViolationLocation',
                'ViolationLocationDescription',
                'ViolationPerpetrator',
                'ViolationPerpetratorClassification',
                'ViolationPerpetratorOrganization',
                'ViolationStartDate',
                'ViolationStatus',
                'ViolationType',
            ])
            permitted_country_set = set([
                'OrganizationDivisionId',
                'PersonDivisionId',
            ])
            assert any([
                related_obj_types.issubset(permitted_org_set),
                related_obj_types.issubset(permitted_person_set),
                related_obj_types.issubset(permitted_incident_set),
                related_obj_types.issubset(permitted_country_set)
            ])


@pytest.mark.skip(reason='Broken, fixed in sfm-cms/pull/776')
@pytest.mark.django_db
def test_source_dates_and_timestamps(data_import):
    """Make sure Source date fields properly parse dates and timestamps."""
    timestamp_src = Source.objects.get(title='Source Timestamps')
    date_src = Source.objects.get(title='Source Dates')
    date_and_timestamp_prefixes = ('created', 'published', 'uploaded')
    for prefix in date_and_timestamp_prefixes:
        date_field = '{}_date'.format(prefix)
        timestamp_field = '{}_timestamp'.format(prefix)
        assert getattr(date_src, date_field)
        assert not getattr(date_src, timestamp_field)
        assert not getattr(timestamp_src, date_field)
        assert getattr(timestamp_src, timestamp_field)

    # Test that invalid published dates are reported as expected
    error_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..',
        'sources-errors.csv'
    )

    undated_sources = Source.objects.filter(published_date='', published_timestamp__isnull=True)\
                                    .values_list('accesspoint__uuid', flat=True)

    undated_source_set = set(str(uuid) for uuid in undated_sources)

    error_source_set = set()

    with open(error_file, 'r') as f:
        reader = csv.reader(f)

        next(reader)  # discard header

        for record in reader:
            _, message = record
            assert message.startswith('Invalid published_date')

            source_id = message.split()[-1]
            assert source_id in undated_source_set
            error_source_set.add(source_id)

        assert undated_source_set == error_source_set

@pytest.mark.django_db
def test_incidents(data_import):
    """Test some properties of imported Incidents."""
    # Make sure the full description gets rendered
    semicolon_incident = Violation.objects.first()
    semicolon_description = semicolon_incident.description.get_value().value
    assert len(semicolon_description.split(';')) == 2

    # Make sure perpetrator classifications get parsed correctly
    assert len(semicolon_incident.perpetratorclassification.get_list()) == 2

    # Check geometry fields
    incident_location = semicolon_incident.location.get_value().value
    assert semicolon_incident.adminlevel1.get_value().value == incident_location.adminlevel1
    assert semicolon_incident.adminlevel2.get_value().value == incident_location.adminlevel2


@pytest.mark.django_db
def test_relationships(data_import):
    """Make sure the correct relationships between entities get imported."""
    # Test org compositions
    org_nodes = ('Alpha', 'Beta', 'Gamma', 'Delta')
    org_edges = (None, 'Alpha', 'Beta', 'Gamma')
    for node, edge in zip(org_nodes, org_edges):
        # Orgs in the source data have trailing spaces in their names
        org = Organization.objects.get(
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


@pytest.mark.django_db
def test_shared_name_creates_distinct_entities(data_import):
    '''
    It's possible for a person or a unit to share a name. Test that, if we
    receive data with same-named entities having different UUIDs, we create
    an object for each distinct instance.
    '''
    organizations_sharing_name = Organization.objects.filter(
        organizationname__value='Unit has same name but duplicate UUID'
    )
    assert organizations_sharing_name.count() == 2

    people_sharing_name = Person.objects.filter(
        personname__value='Importer Test Different UUIDs for Same Name'
    )
    assert people_sharing_name.count() == 2


@pytest.mark.django_db
def test_ambiguous_name_logs_error(data_import):
    '''
    If name is inconsistent between records sharing a UUID, test that an error
    is logged for each record.
    '''
    name = 'Unit has different names for same UUID'
    org = Organization.objects.get(organizationname__value__startswith=name)
    output = data_import.getvalue()

    assert output.count('Got multiple name values for organization UUID "{}'.format(org.uuid)) == 2
    assert output.count('Current row contains value "{}'.format(name)) == 2
