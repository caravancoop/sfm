# -*- coding: utf-8 -*-

import os
import subprocess
from unittest import mock

import pytest

from django.contrib.auth.models import User

from organization.models import Organization, OrganizationAlias, OrganizationClassification
from person.models import Person, PersonAlias, PersonExternalLink
from violation.models import Violation, ViolationPerpetrator, \
    ViolationPerpetratorOrganization, ViolationType, ViolationPerpetratorClassification
from composition.models import Composition
from emplacement.models import Emplacement
from association.models import Association
from membershiporganization.models import MembershipOrganization
from membershipperson.models import MembershipPerson, Rank, Role
from source.models import Source, AccessPoint
from location.models import Location


def is_tab_active(page, tab_name):
    """
    Determine if a nav tab with a given tab_name is active on a given page.
    Active tabs should have the "primary" class name.
    """
    if 'primary">{}'.format(tab_name) in page.content.decode('utf-8'):
        return True
    else:
        return False


@pytest.fixture
def user():
    return User.objects.create(username='testuser',
                               first_name='Test',
                               last_name='User',
                               email='test@test.com',
                               password='test123')


@pytest.fixture()
def setUp(client, request, user):
    user = User.objects.first()
    client.force_login(user)

    @request.addfinalizer
    def tearDown():
        client.logout()

    return client


@pytest.fixture
def sources(user):
    sources = []

    # Since we only want this mock to be applied during this specific block,
    # use the built-in mock.patch() method instead of pytest-mock's fixture.
    with mock.patch('sfm_pc.signals.update_index', autospec=True):
        for index in range(5):
            source = Source.objects.create(
                title='Test {}'.format(index),
                publication='Publication {}'.format(index),
                publication_country='United States',
                published_on='2018-01-01',
                source_url='https://test.com/test-{}'.format(index),
                user=user
            )
            sources.append(source)

    return sources


@pytest.fixture
def access_points(user, sources):
    access_points = []

    for source in sources:
        for index in range(5):
            access_point = AccessPoint.objects.create(page_number='p10{}'.format(index),
                                                      accessed_on='2018-12-12',
                                                      archive_url='https://web.archive.org/https://test.com/test-{}'.format(index),
                                                      source=source,
                                                      user=user)
            access_points.append(access_point)

    return access_points


@pytest.fixture
def new_access_points(user, sources):
    access_points = []

    for source in sources:
        for index in range(5):
            access_point = AccessPoint.objects.create(page_number='p20{}'.format(index),
                                                      accessed_on='2017-12-12',
                                                      archive_url='https://web.archive.org/https://test.com/test-{}'.format(index),
                                                      source=source,
                                                      user=user)
            access_points.append(access_point)

    return access_points


@pytest.fixture
def location_adminlevel1():
    return Location.objects.create(id=5572040,
                                   name='Túxpam',
                                   division_id='ocd-division/country:mx',
                                   feature_type='relation')


@pytest.fixture
def location_adminlevel2():
    return Location.objects.create(id=2415761,
                                   name='Veracruz',
                                   division_id='ocd-division/country:mx',
                                   feature_type='relation')

@pytest.fixture
def location_node(location_adminlevel1, location_adminlevel2):

    return Location.objects.create(id=472257682,
                                   name='Túxpam de Rodríguez Cano, Veracruz',
                                   division_id='ocd-division/country:mx',
                                   feature_type='node',
                                   adminlevel1=location_adminlevel1,
                                   adminlevel2=location_adminlevel2)


@pytest.fixture
def location_relation(location_adminlevel1, location_adminlevel2):
    return Location.objects.create(id=5996623,
                                   name='Hpasawng Township, Kayah',
                                   division_id='ocd-division/country:mm',
                                   adminlevel1=location_adminlevel1,
                                   adminlevel2=location_adminlevel2)


@pytest.fixture
def organization_aliases(access_points):
    for index in range(2):
        return OrganizationAlias.objects.create(value='Alias {}'.format(index),
                                                accesspoints=access_points)


@pytest.fixture
def base_organizations(access_points):

    organizations = []

    for index in range(3):

        org = {
            'Organization_OrganizationName': {
                'sources': access_points,
                'value': 'Test organization {}'.format(index),
                'confidence': '1',
            },
            'Organization_OrganizationDivisionId': {
                'sources': access_points,
                'value': 'ocd-division/country:us',
                'confidence': '1',
            }
        }

        organization = Organization.create(org)

        organizations.append(organization)

    return organizations


@pytest.fixture
def organization_aliases(base_organizations):

    aliases = []

    for organization in base_organizations:
        for index in range(2):
            alias = OrganizationAlias.objects.create(value='Alias {}'.format(index),
                                                     object_ref=organization,
                                                     lang='en')
            for access_point in organization.name.get_value().accesspoints.all():
                alias.accesspoints.add(access_point)
                alias.sources.add(access_point.source)

            aliases.append(alias)

    return aliases


@pytest.fixture
def organization_classifications(base_organizations):

    classifications = []

    for organization in base_organizations:
        for index in range(2):
            classification = OrganizationClassification.objects.create(value='Classification {}'.format(index),
                                                              object_ref=organization,
                                                              lang='en')
            for access_point in organization.name.get_value().accesspoints.all():
                classification.accesspoints.add(access_point)
                classification.sources.add(access_point.source)

            classifications.append(classification)

    return classifications


@pytest.fixture
def organizations(base_organizations,
                  organization_aliases,
                  organization_classifications,
                  access_points):

    organizations = []

    for organization in base_organizations:

        org_info = {
            'Organization_OrganizationFirstCitedDate': {
                'sources': access_points,
                'value': '2017-01-01',
                'confidence': '2',
            },
            'Organization_OrganizationLastCitedDate': {
                'sources': access_points,
                'value': '2018-01-01',
                'confidence': '1',
            },
            'Organization_OrganizationRealStart': {
                'value': False
            },
            'Organization_OrganizationOpenEnded': {
                'value': 'Y',
                'sources': access_points,
                'confidence': '2',
            }
        }

        organization.update(org_info)

        organization.published = True
        organization.save()

        organizations.append(organization)

    return organizations


@pytest.fixture
def composition(organizations, access_points):
    parent, middle, child = organizations

    compositions = []
    comp_info = {
        'Composition_CompositionParent': {
            'sources': access_points,
            'value': parent,
            'confidence': '2'
        },
        'Composition_CompositionChild': {
            'sources': access_points,
            'value': middle,
            'confidence': '1',
        },
        'Composition_CompositionRealStart': {
            'value': False,
        },
        'Composition_CompositionStartDate': {
            'value': '2018-01-02',
            'confidence': '2',
            'sources': access_points,
        },
        'Composition_CompositionEndDate': {
            'value': '2018-03-01',
            'confidence': '1',
            'sources': access_points,
        },
        'Composition_CompositionOpenEnded': {
            'value': 'N',
            'confidence': '1',
            'sources': access_points,
        },
        'Composition_CompositionClassification': {
            'value': 'Command',
            'confidence': '2',
            'sources': access_points,
        }
    }

    compositions.append(Composition.create(comp_info))

    comp_info['Composition_CompositionParent']['value'] = middle
    comp_info['Composition_CompositionChild']['value'] = child

    compositions.append(Composition.create(comp_info))
    return compositions


@pytest.fixture
def emplacement(organizations, location_node, access_points):
    emplacements = []
    for organization in organizations:
        emp_info = {
            'Emplacement_EmplacementOrganization': {
                'value': organization,
                'sources': access_points,
                'confidence': '3'
            },
            'Emplacement_EmplacementStartDate': {
                'value': '2012-06-01',
                'confidence': '2',
                'sources': access_points,
            },
            'Emplacement_EmplacementEndDate': {
                'value': '2013-03-02',
                'confidence': '1',
                'sources': access_points,
            },
            'Emplacement_EmplacementRealStart': {
                'value': True
            },
            'Emplacement_EmplacementSite': {
                'value': location_node,
                'confidence': '2',
                'sources': access_points,
            },
            'Emplacement_EmplacementOpenEnded': {
                'value': 'Y',
                'confidence': '1',
                'sources': access_points,
            },
        }

        emplacements.append(Emplacement.create(emp_info))

    return emplacements


@pytest.fixture
def association(organizations, location_relation, access_points):
    associations = []
    for organization in organizations:
        ass_info = {
            'Association_AssociationRealStart': {
                'value': False
            },
            'Association_AssociationStartDate': {
                'value': '2016-08-01',
                'confidence': '1',
                'sources': access_points,
            },
            'Association_AssociationEndDate': {
                'value': '2017-10-23',
                'confidence': '2',
                'sources': access_points,
            },
            'Association_AssociationOrganization': {
                'value': organization,
                'confidence': '1',
                'sources': access_points,
            },
            'Association_AssociationArea': {
                'value': location_relation,
                'confidence': '1',
                'sources': access_points,
            },
            'Association_AssociationOpenEnded': {
                'value': 'E',
                'confidence': '1',
                'sources': access_points,
            }
        }

        associations.append(Association.create(ass_info))

    return associations


@pytest.fixture
def membership_organization(organizations, access_points):
    member, _, parent = organizations

    mem_info = {
        'MembershipOrganization_MembershipOrganizationMember': {
            'value': member,
            'sources': access_points,
            'confidence': '1'
        },
        'MembershipOrganization_MembershipOrganizationOrganization': {
            'value': parent,
            'sources': access_points,
            'confidence': '1'
        },
        'MembershipOrganization_MembershipOrganizationFirstCitedDate': {
            'value': '2002-01-01',
            'sources': access_points,
            'confidence': '1'
        },
        'MembershipOrganization_MembershipOrganizationLastCitedDate': {
            'value': '2003-01-01',
            'sources': access_points,
            'confidence': '1'
        },
        'MembershipOrganization_MembershipOrganizationRealStart': {
            'value': False,
        },
        'MembershipOrganization_MembershipOrganizationRealEnd': {
            'value': True,
        },
    }

    return MembershipOrganization.create(mem_info)


@pytest.fixture
def full_organizations(organizations,
                       composition,
                       emplacement,
                       association,
                       membership_organization):

    return organizations


@pytest.fixture
def new_organizations(access_points):

    organizations = []

    for index in range(3):

        org = {
            'Organization_OrganizationName': {
                'sources': access_points,
                'value': 'New Test organization {}'.format(index),
                'confidence': '1',
            },
            'Organization_OrganizationDivisionId': {
                'sources': access_points,
                'value': 'ocd-division/country:us',
                'confidence': '1',
            }
        }

        organization = Organization.create(org)

        organizations.append(organization)

    return organizations


@pytest.fixture
def base_people(access_points):
    people = []

    for index in range(3):
        person = {
            'Person_PersonName': {
                'value': 'Test person {}'.format(index),
                'sources': access_points,
                'confidence': '1'
            },
            'Person_PersonDivisionId':{
                'value': 'ocd-division/country:us',
                'sources': access_points,
                'confidence': '2',
            }
        }

        people.append(Person.create(person))

    return people


@pytest.fixture
def new_people(access_points):
    people = []

    for index in range(3):
        person = {
            'Person_PersonName': {
                'value': 'New Test person {}'.format(index),
                'sources': access_points,
                'confidence': '1'
            },
            'Person_PersonDivisionId':{
                'value': 'ocd-division/country:us',
                'sources': access_points,
                'confidence': '2',
            }
        }

        people.append(Person.create(person))

    return people


@pytest.fixture
def people(base_people, access_points):

    for person in base_people:
        for index in range(2):
            alias = PersonAlias.objects.create(value='Alias {}'.format(index),
                                               lang='en',
                                               object_ref=person)

            alias.accesspoints.set(access_points)

            link = PersonExternalLink.objects.create(value='http://personblog.com/test-{}'.format(index),
                                                     lang='en',
                                                     object_ref=person)
            link.accesspoints.set(access_points)

        person_info = {
            'Person_PersonDivisionId': {
                'value': 'ocd-division/country:us',
                'sources': access_points,
                'confidence': '1'
            },
            'Person_PersonGender': {
                'value': 'Male',
                'sources': access_points,
                'confidence': '1'
            },
            'Person_PersonDateOfBirth': {
                'value': '2018-01-01',
                'sources': access_points,
                'confidence': '1'
            },
            'Person_PersonDateOfDeath': {
                'value': '2018-02-01',
                'sources': access_points,
                'confidence': '1'
            },
            'Person_PersonDeceased': {
                'value': True,
                'sources': access_points,
                'confidence': '1'
            },
            'Person_PersonBiography': {
                'value': 'This guy is great',
                'sources': access_points,
                'confidence': '1'
            },
            'Person_PersonNotes': {
                'value': 'Super great',
                'sources': access_points,
                'confidence': '1'
            },
        }

        person.update(person_info)

    return base_people


@pytest.fixture
def membership_person(access_points, people, organizations):

    memberships = []

    for member in people[:2]:

        rank = Rank.objects.create(value='Commander')
        role = Role.objects.create(value='Honcho')

        mem_info = {
            'MembershipPerson_MembershipPersonMember': {
                'value': member,
                'sources': access_points,
                'confidence': '1',
            },
            'MembershipPerson_MembershipPersonOrganization': {
                'value': organizations[0],
                'sources': access_points,
                'confidence': '1',
            },
            'MembershipPerson_MembershipPersonRole': {
                'value': role,
                'sources': access_points,
                'confidence': '1',
            },
            'MembershipPerson_MembershipPersonRank': {
                'value': rank,
                'sources': access_points,
                'confidence': '1',
            },
            'MembershipPerson_MembershipPersonTitle': {
                'value': 'Big Chief',
                'sources': access_points,
                'confidence': '1',
            },
            'MembershipPerson_MembershipPersonRealEnd': {
                'value': False,
            },
            'MembershipPerson_MembershipPersonStartContext': {
                'value': 'Born',
                'sources': access_points,
                'confidence': '1',
            },
            'MembershipPerson_MembershipPersonEndContext': {
                'value': 'Died',
                'sources': access_points,
                'confidence': '1',
            },
            'MembershipPerson_MembershipPersonFirstCitedDate': {
                'value': '2002-01-01',
                'sources': access_points,
                'confidence': '1',
            },
            'MembershipPerson_MembershipPersonLastCitedDate': {
                'value': '2003-01-01',
                'sources': access_points,
                'confidence': '1',
            },
        }

        memberships.append(MembershipPerson.create(mem_info))

    return memberships


@pytest.fixture
def base_violation(access_points,
                   location_node,
                   location_adminlevel1,
                   location_adminlevel2):

    violation_info = {
        'Violation_ViolationStartDate': {
            'value': '2003-08-09',
            'sources': access_points,
            'confidence': '2',
        },
        'Violation_ViolationEndDate': {
            'value': '2003-08-10',
            'sources': access_points,
            'confidence': '2',
        },
        'Violation_ViolationLocationDescription': {
            'value': 'Out back',
            'sources': access_points,
            'confidence': '2',
        },
        'Violation_ViolationAdminLevel1': {
            'value': location_adminlevel1,
            'sources': access_points,
            'confidence': '2',
        },
        'Violation_ViolationAdminLevel2': {
            'value': location_adminlevel2,
            'sources': access_points,
            'confidence': '2',
        },
        'Violation_ViolationDivisionId': {
            'value': 'ocd-division/country:us',
            'sources': access_points,
            'confidence': '2',
        },
        'Violation_ViolationLocation': {
            'value': location_node,
            'sources': access_points,
            'confidence': '2',
        },
        'Violation_ViolationDescription': {
            'value': 'something real bad',
            'sources': access_points,
            'confidence': '2',
        },
    }

    violation = Violation.create(violation_info)

    violation.published = True
    violation.save()

    return violation


@pytest.fixture
def violation(base_violation,
              people,
              organizations,
              access_points):

    perpetrators = []
    perpetrator_organizations = []

    for person in people:
        perpetrator = ViolationPerpetrator.objects.create(value=person,
                                                          object_ref=base_violation,
                                                          lang='en')
        perpetrators.append(perpetrator)

    for organization in organizations:
        perpetrator_organization = ViolationPerpetratorOrganization.objects.create(value=organization,
                                                                                   object_ref=base_violation,
                                                                                   lang='en')
        perpetrator_organizations.append(perpetrator_organization)

    right_to_life = ViolationType.objects.create(value='Violation against the right to life',
                                                 object_ref=base_violation,
                                                 lang='en')

    right_to_liberty = ViolationType.objects.create(value='Violation against the right to liberty',
                                                    object_ref=base_violation,
                                                    lang='en')

    classification = ViolationPerpetratorClassification.objects.create(value='Bad guys',
                                                                       object_ref=base_violation,
                                                                       lang='en')

    violation_info = {
        'Violation_ViolationPerpetrator': {
            'values': perpetrators,
            'sources': access_points,
            'confidence': '2',
        },
        'Violation_ViolationPerpetratorOrganization': {
            'values': perpetrator_organizations,
            'sources': access_points,
            'confidence': '2',
        },
        'Violation_ViolationType': {
            'values': [right_to_life, right_to_liberty],
            'sources': access_points,
            'confidence': '1',
        },
        'Violation_ViolationPerpetratorClassification': {
            'value': classification.value,
            'sources': access_points,
            'confidence': '1',
        }
    }

    base_violation.update(violation_info)

    return base_violation


@pytest.fixture
def fake_signal(mocker):
    fake_signal = mocker.patch('complex_fields.base_models.object_ref_saved.send')
    return fake_signal


@pytest.fixture
def update_index_mock(mocker):
    """Mock the update_index method that fires on the post_save and post_delete signals."""
    return mocker.patch('sfm_pc.signals.update_index', autospec=True)


@pytest.fixture
def searcher_mock(mocker):
    """Mock the pysolr client used to access the search index."""
    return mocker.patch('search.search.Searcher.delete', autospec=True)
