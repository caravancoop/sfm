from uuid import uuid4

import pytest

from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User
from django.db.models import Count

from source.models import AccessPoint
from person.models import Person
from organization.models import Organization
from membershipperson.models import MembershipPerson, Rank, Role


@pytest.fixture()
def setUp(user, client, request):
    user = User.objects.first()
    client.force_login(user)

    @request.addfinalizer
    def tearDown():
        client.logout()

    return client


@pytest.mark.django_db
def test_view_person(setUp, people):

    for person in people:
        response = setUp.get(reverse_lazy('view-person', args=[person.uuid]))
        assert response.status_code == 200


@pytest.mark.django_db
def test_edit_person(setUp, people, new_access_points, fake_signal):
    person = people[0]

    response = setUp.get(reverse_lazy('edit-person', kwargs={'slug': person.uuid}))

    assert response.status_code == 200

    new_source_ids = [s.uuid for s in new_access_points]

    post_data = {
        'name': person.name.get_value(),
        'name_source': [s.uuid for s in person.name.get_sources()],
        'name_confidence': '2',
        'aliases': [p.get_value().id for p in person.aliases.get_list()] + ['Foo'],
        'aliases_source': new_source_ids + [s.uuid for s in person.aliases.get_list()[0].get_sources()],
        'aliases_confidence': '2',
        'division_id': 'ocd-division/country:us',
        'division_id_source': new_source_ids + [s.uuid for s in person.division_id.get_sources()],
        'division_id_confidence': '3',
        'date_of_birth': '1976',
        'date_of_birth_source': new_source_ids,
        'date_of_birth_confidence': '1',
        'date_of_death': '2012-02-14',
        'date_of_death_source': new_source_ids,
        'date_of_death_confidence': '3',
        'deceased': True,
        'deceased_source': new_source_ids,
        'deceased_confidence': '3',
    }

    response = setUp.post(reverse_lazy('edit-person', kwargs={'slug': person.uuid}), post_data)

    assert response.status_code == 302

    assert 'Foo' in [p.get_value().value for p in person.aliases.get_list()]

    for alias in person.aliases.get_list():
        assert set(new_source_ids) <= {a.uuid for a in alias.get_sources()}

    assert person.division_id.get_value().value == 'ocd-division/country:us'
    assert str(person.date_of_birth.get_value().value) == '1976'
    assert str(person.date_of_death.get_value().value) == '14th February 2012'
    assert person.deceased.get_value().value == True

    assert person.name.get_value().confidence == '2'
    assert person.aliases.get_list()[0].get_value().confidence == '2'
    assert person.division_id.get_value().confidence == '3'
    assert person.date_of_birth.get_value().confidence == '1'
    assert person.date_of_death.get_value().confidence == '3'
    assert person.deceased.get_value().confidence == '3'

    fake_signal.assert_called_with(object_id=person.uuid, sender=Person)


@pytest.mark.django_db
def test_no_source_one_value(setUp, base_people):
    person = base_people[0]

    post_data = {
        'name': person.name.get_value().value,
        'biography': person.name.get_value().value + ' Foo',
    }

    response = setUp.post(reverse_lazy('edit-person', kwargs={'slug': person.uuid}), post_data)

    assert response.status_code == 200

    assert '"biography" now has a value so it requires sources' in response.context['form'].errors['biography']


@pytest.mark.django_db
def test_no_source_multiple_value(setUp, base_people):
    person = base_people[0]

    post_data = {
        'aliases': ['Foo', 'Bar'],
    }

    response = setUp.post(reverse_lazy('edit-person', kwargs={'slug': person.uuid}), post_data)

    assert response.status_code == 200

    assert '"aliases" has new values so it requires sources' in response.context['form'].errors['aliases']
    assert 'This field is required.' in response.context['form'].errors['name']

    assert 'Foo' not in [p.get_value().value for p in person.aliases.get_list()]
    assert 'Bar' not in [p.get_value().value for p in person.aliases.get_list()]


@pytest.mark.django_db
def test_no_source_one_new_value(setUp, people):
    person = people[0]

    post_data = {
        'aliases': [p.get_value().id for p in person.aliases.get_list()] + ['Foo'],
    }

    response = setUp.post(reverse_lazy('edit-person', kwargs={'slug': person.uuid}), post_data)

    assert response.status_code == 200

    assert '"aliases" has new values so it requires sources' in response.context['form'].errors['aliases']
    assert 'This field is required.' in response.context['form'].errors['name']

    assert 'Foo' not in [p.get_value().value for p in person.aliases.get_list()]


@pytest.mark.django_db
def test_no_source_empty_start(setUp, base_people):
    person = base_people[0]
    sources = [s.uuid for s in person.name.get_sources()]

    post_data = {
        'name': person.name.get_value().value,
        'name_source': sources,
        'aliases': person.name.get_value(),
    }

    response = setUp.post(reverse_lazy('edit-person',
                                       kwargs={'slug': person.uuid}),
                          post_data)

    assert response.status_code == 200

    assert '"aliases" has new values so it requires sources' in response.context['form'].errors['aliases']


@pytest.mark.django_db
def test_remove_value(setUp, people, fake_signal):
    person = people[0]

    aliases = [a.get_value().id for a in person.aliases.get_list()]
    removed = aliases.pop()

    post_data = {
        'name': person.name.get_value().value,
        'name_source': [s.uuid for s in person.name.get_sources()],
        'aliases': aliases,
        'aliases_source': [s.uuid for s in person.aliases.get_list()[0].get_sources()],
    }

    response = setUp.post(reverse_lazy('edit-person', kwargs={'slug': person.uuid}), post_data)

    assert response.status_code == 302

    assert aliases == [a.get_value().id for a in person.aliases.get_list()]

    fake_signal.assert_called_with(object_id=person.uuid, sender=Person)


@pytest.mark.django_db
def test_remove_value_same_sources(setUp, people, fake_signal):
    person = people[1]

    aliases = [a.get_value().id for a in person.aliases.get_list()]
    removed = aliases.pop()

    sources = set()

    for alias in person.aliases.get_list():
        for source in alias.get_sources():
            sources.add(source.uuid)

    post_data = {
        'name': person.name.get_value().value,
        'name_source': list(sources),
        'aliases': aliases,
        'aliases_source': list(sources),
    }

    response = setUp.post(reverse_lazy('edit-person', kwargs={'slug': person.uuid}), post_data)

    assert response.status_code == 302

    assert aliases == [a.get_value().id for a in person.aliases.get_list()]

    fake_signal.assert_called_with(object_id=person.uuid, sender=Person)


@pytest.mark.django_db
def test_remove_all_values(setUp, people, fake_signal):
    person = people[2]

    sources = [s.uuid for s in person.name.get_sources()]

    post_data = {
        'name': person.name.get_value().value,
        'name_source': sources,
        'aliases_source': [s.uuid for s in person.aliases.get_list()[0].get_sources()]
    }

    response = setUp.post(reverse_lazy('edit-person', kwargs={'slug': person.uuid}), post_data)

    assert response.status_code == 302

    assert person.aliases.get_list() == []

    fake_signal.assert_called_with(object_id=person.uuid, sender=Person)


@pytest.mark.django_db
def test_duplicate_source(setUp, people, fake_signal):
    person = people[0]

    sources = [s.uuid for s in person.name.get_sources()]

    post_data = {
        'name': person.name.get_value().value,
        'name_source': sources + sources,
    }

    response = setUp.post(reverse_lazy('edit-person', kwargs={'slug': person.uuid}), post_data)

    assert response.status_code == 302

    assert len(person.name.get_sources()) == len(sources)
    fake_signal.assert_called_with(object_id=person.uuid, sender=Person)


@pytest.mark.django_db
def test_just_add_source(setUp, people, new_access_points, fake_signal):
    person = people[0]

    sources = [s.uuid for s in person.name.get_sources()]

    new_source = new_access_points[0]

    alias_sources = set()

    for alias in person.aliases.get_list():
        for source in alias.get_sources():
            alias_sources.add(source.uuid)

    external_link_sources = set()

    for external_link in person.external_links.get_list():
        for source in external_link.get_sources():
            external_link_sources.add(source.uuid)

    post_data = {
        'name': person.name.get_value().value,
        'name_source': [new_source.uuid],
    }

    response = setUp.post(reverse_lazy('edit-person', kwargs={'slug': person.uuid}), post_data)

    assert response.status_code == 302

    assert new_source in person.name.get_sources()
    fake_signal.assert_called_with(object_id=person.uuid, sender=Person)


@pytest.mark.django_db
def test_new_sources_required(setUp, base_people):
    person = base_people[1]
    sources = [s.uuid for s in person.name.get_sources()]

    post_data = {
        'name': person.name.get_value().value + ' Foo',
        'name_source': sources,
    }

    response = setUp.post(reverse_lazy('edit-person',
                                       kwargs={'slug': person.uuid}),
                          post_data)

    assert response.status_code == 200

    assert 'The value of "name" changed so it requires sources' in response.context['form'].errors['name']


@pytest.mark.django_db
def test_new_sources_required_multi(setUp, people):
    person = people[1]
    sources = [s.uuid for s in person.name.get_sources()]

    post_data = {
        'name': person.name.get_value().value,
        'name_source': sources,
        'aliases': [a.get_value().id for a in person.aliases.get_list()] + ['Foo'],
        'aliases_source': [s.uuid for s in person.aliases.get_list()[0].get_sources()],
        'gender': '',
    }

    response = setUp.post(reverse_lazy('edit-person',
                                       kwargs={'slug': person.uuid}),
                          post_data)

    assert response.status_code == 200

    assert '"aliases" has new values so it requires sources' in response.context['form'].errors['aliases']


@pytest.mark.django_db
def test_edit_posting(setUp,
                      membership_person,
                      new_access_points,
                      new_organizations,
                      fake_signal):

    membership = membership_person[0]
    person = membership.member.get_value().value
    response = setUp.get(reverse_lazy('edit-person-postings',
                                      kwargs={'person_id': person.uuid,
                                              'pk': membership.id}))

    assert response.status_code == 200

    sources = [s for s in membership.organization.get_sources()]

    new_source = new_access_points[0]

    new_organization = new_organizations[0]
    new_rank = Rank.objects.create(value='New Commander')
    new_role = Role.objects.create(value='New Honcho')

    post_data = {
        'member': person.id,
        'organization': new_organization.id,
        'organization_source': [new_source.uuid],
        'rank': new_rank.id,
        'rank_source': [new_source.uuid],
        'role': new_role.id,
        'role_source': [new_source.uuid],
        'title': 'Floober',
        'title_source': [new_source.uuid],
        'firstciteddate': '2007',
        'firstciteddate_source': [new_source.uuid],
        'lastciteddate': 'April 2012',
        'lastciteddate_source': [new_source.uuid],
        'realstart': True,
        'realstart_source': [new_source.uuid],
        'startcontext': 'Floop de doop',
        'startcontext_source': [new_source.uuid]
    }

    response = setUp.post(reverse_lazy('edit-person-postings',
                                       kwargs={'person_id': person.uuid,
                                               'pk': membership.id}),
                          post_data)

    assert response.status_code == 302

    assert membership.organization.get_value().value.uuid == new_organization.uuid
    assert new_source in membership.organization.get_sources()
    assert membership.rank.get_value().value == new_rank
    assert membership.role.get_value().value == new_role

    fake_signal.assert_called_with(object_id=membership.id,
                                   sender=MembershipPerson)


@pytest.mark.django_db
def test_boolean_none_to_true(setUp, membership_person, new_access_points, fake_signal):
    membership = membership_person[1]
    person = membership.member.get_value().value

    new_source = new_access_points[2]

    post_data = {
        'member': person.id,
        'organization': membership.organization.get_value().value.id,
        'organization_source': [str(s.uuid) for s in membership.organization.get_sources()],
        'realstart': 'on',
        'realstart_source': [new_source.uuid],
    }

    response = setUp.post(reverse_lazy('edit-person-postings',
                                       kwargs={'person_id': person.uuid,
                                               'pk': membership.id}),
                          post_data)

    assert response.status_code == 302

    assert membership.realstart.get_value().value == True

    fake_signal.assert_called_with(object_id=membership.id,
                                   sender=MembershipPerson)


@pytest.mark.django_db
def test_boolean_true_to_false(setUp, membership_person, new_access_points, fake_signal):
    membership = membership_person[1]
    person = membership.member.get_value().value

    new_source = new_access_points[1]

    post_data = {
        'member': person.id,
        'organization': membership.organization.get_value().value.id,
        'organization_source': [str(s.uuid) for s in membership.organization.get_sources()],
        'realstart_source': [new_source.uuid],
    }

    response = setUp.post(reverse_lazy('edit-person-postings',
                                       kwargs={'person_id': person.uuid,
                                               'pk': membership.id}),
                          post_data)

    assert response.status_code == 302

    assert membership.realstart.get_value().value == False

    fake_signal.assert_called_with(object_id=membership.id,
                                   sender=MembershipPerson)


@pytest.mark.django_db
def test_boolean_false_to_true(setUp, membership_person, fake_signal):
    membership = membership_person[0]
    person = membership.member.get_value().value

    post_data = {
        'member': person.id,
        'organization': membership.organization.get_value().value.id,
        'organization_source': [str(s.uuid) for s in membership.organization.get_sources()],
        'realend': 'on',
    }

    response = setUp.post(reverse_lazy('edit-person-postings',
                                       kwargs={'person_id': person.uuid,
                                               'pk': membership.id}),
                          post_data)

    assert response.status_code == 302

    assert membership.realend.get_value().value == True

    fake_signal.assert_called_with(object_id=membership.id,
                                   sender=MembershipPerson)


@pytest.mark.django_db
def test_boolean_true_no_sources(setUp, membership_person, fake_signal):
    membership = membership_person[1]
    person = membership.member.get_value().value

    post_data = {
        'member': person.id,
        'organization': membership.organization.get_value().value.id,
        'organization_source': [str(s.uuid) for s in membership.organization.get_sources()],
        'realstart': 'on',
    }

    response = setUp.post(reverse_lazy('edit-person-postings',
                                       kwargs={'person_id': person.uuid,
                                               'pk': membership.id}),
                          post_data)

    assert response.status_code == 302
    assert membership.realstart.get_value().value == True

    fake_signal.assert_called_with(object_id=membership.id,
                                   sender=MembershipPerson)


@pytest.mark.django_db
def test_no_existing_sources(setUp, membership_person):
    membership = membership_person[0]
    person = membership.member.get_value().value

    membership.rank.get_value().sources.set([])
    membership.rank.get_value().accesspoints.set([])

    post_data = {
        'member': person.id,
        'organization': membership.organization.get_value().value.id,
        'organization_source': [str(s.uuid) for s in membership.organization.get_sources()],
        'rank': membership.rank.get_value().value.id,
    }

    response = setUp.post(reverse_lazy('edit-person-postings',
                                       kwargs={'person_id': person.uuid,
                                               'pk': membership.id}),
                          post_data)

    assert response.status_code == 200
    assert 'Please add some sources to "rank"' in response.context['form'].errors['rank']


@pytest.mark.django_db
def test_create_person(setUp, new_access_points, fake_signal):

    response = setUp.get(reverse_lazy('create-person'))

    assert response.status_code == 200

    new_source_ids = [s.uuid for s in new_access_points]

    post_data = {
        'name': 'Someone Something',
        'name_source': new_source_ids,
        'aliases': ['Foo', 'Bar', 'Baz'],
        'aliases_source': new_source_ids,
        'division_id': 'ocd-division/country:us',
        'division_id_source': new_source_ids,
        'date_of_birth': '1976',
        'date_of_birth_source': new_source_ids,
        'date_of_death': '2012-02-14',
        'date_of_death_source': new_source_ids,
        'deceased': True,
        'deceased_source': new_source_ids,
    }

    response = setUp.post(reverse_lazy('create-person'), post_data)

    assert response.status_code == 302

    person = Person.objects.get(personname__value='Someone Something')

    assert 'Foo' in [p.get_value().value for p in person.aliases.get_list()]

    assert person.division_id.get_value().value == 'ocd-division/country:us'
    assert str(person.date_of_birth.get_value().value) == '1976'
    assert str(person.date_of_death.get_value().value) == '14th February 2012'
    assert person.deceased.get_value().value == True

    fake_signal.assert_called_with(object_id=str(person.uuid), sender=Person)


@pytest.mark.django_db
def test_create_posting(setUp,
                        people,
                        new_access_points,
                        new_organizations,
                        fake_signal):

    person = people[0]

    response = setUp.get(reverse_lazy('create-person-posting',
                                      kwargs={'person_id': person.uuid}))

    assert response.status_code == 200

    sources = [s for s in person.name.get_sources()]

    new_source = new_access_points[0]

    new_organization = new_organizations[0]
    new_rank = Rank.objects.create(value='New Commander')
    new_role = Role.objects.create(value='New Honcho')

    post_data = {
        'member': person.id,
        'organization': new_organization.id,
        'organization_source': [new_source.uuid],
        'rank': new_rank.id,
        'rank_source': [new_source.uuid],
        'role': new_role.id,
        'role_source': [new_source.uuid],
        'title': 'Floober',
        'title_source': [new_source.uuid],
        'firstciteddate': '2007',
        'firstciteddate_source': [new_source.uuid],
        'lastciteddate': 'April 2012',
        'lastciteddate_source': [new_source.uuid],
        'realstart': True,
        'realstart_source': [new_source.uuid],
        'startcontext': 'Floop de doop',
        'startcontext_source': [new_source.uuid]
    }

    response = setUp.post(reverse_lazy('create-person-posting',
                                       kwargs={'person_id': person.uuid}),
                          post_data)

    assert response.status_code == 302

    membership = MembershipPerson.objects.get(membershippersontitle__value='Floober')

    assert membership.organization.get_value().value.uuid == new_organization.uuid
    assert new_source in membership.organization.get_sources()
    assert membership.rank.get_value().value == new_rank
    assert membership.role.get_value().value == new_role

    fake_signal.assert_called_with(object_id=membership.id,
                                   sender=MembershipPerson)
