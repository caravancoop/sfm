import pytest

from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User
from django.db.models import Count

from source.models import Source
from person.models import Person
from organization.models import Organization
from membershipperson.models import MembershipPerson, Rank, Role


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
def test_view_person(setUp):

    them = Person.objects.order_by('?')[:10]

    for person in them:
        response = setUp.get(reverse_lazy('view-person', args=[person.uuid]))
        assert response.status_code == 200


@pytest.mark.django_db
def test_edit_person(setUp, fake_signal):
    person = Person.objects.exclude(personalias__isnull=True).order_by('?').first()
    new_sources = Source.objects.order_by('?')[:2]

    response = setUp.get(reverse_lazy('edit-person', kwargs={'slug': person.uuid}))

    assert response.status_code == 200

    new_source_ids = [s.uuid for s in new_sources]

    post_data = {
        'name': person.name.get_value(),
        'name_source': [s.uuid for s in person.name.get_sources()],
        'aliases': [p.get_value().id for p in person.aliases.get_list()] + ['Foo'],
        'aliases_source': new_source_ids + [s.uuid for s in person.aliases.get_list()[0].get_sources()],
        'division_id': 'ocd-division/country:us',
        'division_id_source': new_source_ids + [s.uuid for s in person.division_id.get_sources()],
        'date_of_birth': '1976',
        'date_of_birth_source': new_source_ids,
        'date_of_death': '2012-02-14',
        'date_of_death_source': new_source_ids,
        'deceased': True,
        'deceased_source': new_source_ids,
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

    fake_signal.assert_called_with(object_id=person.uuid, sender=Person)


@pytest.mark.django_db
def test_no_source_one_value(setUp):
    person = Person.objects.exclude(personalias__isnull=True).order_by('?').first()

    post_data = {
        'name': person.name.get_value().value,
        'biography': person.name.get_value().value + ' Foo',
    }

    response = setUp.post(reverse_lazy('edit-person', kwargs={'slug': person.uuid}), post_data)

    assert response.status_code == 200

    assert '"biography" now has a value so it requires sources' in response.context['form'].errors['biography']


@pytest.mark.django_db
def test_no_source_multiple_value(setUp):
    person = Person.objects.exclude(personalias__isnull=True).order_by('?').first()

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
def test_no_source_one_new_value(setUp):
    person = Person.objects.exclude(personalias__isnull=True).order_by('?').first()

    post_data = {
        'aliases': [p.get_value().id for p in person.aliases.get_list()] + ['Foo'],
    }

    response = setUp.post(reverse_lazy('edit-person', kwargs={'slug': person.uuid}), post_data)

    assert response.status_code == 200

    assert '"aliases" has new values so it requires sources' in response.context['form'].errors['aliases']
    assert 'This field is required.' in response.context['form'].errors['name']

    assert 'Foo' not in [p.get_value().value for p in person.aliases.get_list()]


@pytest.mark.django_db
def test_no_source_empty_start(setUp):
    person = Person.objects.filter(personalias__isnull=True).order_by('?').first()
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
def test_remove_value(setUp, fake_signal):
    person = Person.objects\
                   .annotate(alias_count=Count('personalias'))\
                   .filter(alias_count__gte=2)[0]

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
def test_remove_value_same_sources(setUp, fake_signal):
    person = Person.objects.exclude(personalias__isnull=True).order_by('?').first()

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
def test_remove_all_values(setUp, fake_signal):
    person = Person.objects.exclude(personalias__isnull=True).order_by('?').first()

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
def test_duplicate_source(setUp, fake_signal):
    person = Person.objects.exclude(personalias__isnull=True).order_by('?').first()

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
def test_just_add_source(setUp, fake_signal):
    person = Person.objects.order_by('?').first()

    sources = [s.uuid for s in person.name.get_sources()]

    new_source = Source.objects.exclude(uuid__in=sources).first()

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
def test_new_sources_required(setUp):
    person = Person.objects.filter(personalias__isnull=True).order_by('?').first()
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
def test_new_sources_required_multi(setUp):
    person = Person.objects.exclude(personalias__isnull=True).order_by('?').first()
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
def test_edit_posting(setUp, fake_signal):
    membership = MembershipPerson.objects.order_by('?').first()
    person = membership.member.get_value().value
    response = setUp.get(reverse_lazy('edit-person-postings',
                                      kwargs={'person_id': person.uuid,
                                              'pk': membership.id}))

    assert response.status_code == 200

    sources = [s for s in membership.organization.get_sources()]

    new_source = Source.objects.exclude(uuid__in=[s.uuid for s in sources]).first()

    new_organization = Organization.objects.exclude(organizationname__isnull=True).order_by('?').first()
    new_rank = Rank.objects.order_by('?').first()
    new_role = Role.objects.order_by('?').first()

    post_data = {
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
def test_boolean_none_to_true(setUp, fake_signal):
    membership = MembershipPerson.objects.filter(membershippersonrealstart__value__isnull=True).first()
    person = membership.member.get_value().value

    new_source = Source.objects.order_by('?').first()

    post_data = {
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
def test_boolean_true_to_false(setUp, fake_signal):
    membership = MembershipPerson.objects.filter(membershippersonrealstart__value=True).first()
    person = membership.member.get_value().value

    new_source = Source.objects.order_by('?').first()

    post_data = {
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
def test_boolean_false_to_true(setUp, fake_signal):
    membership = MembershipPerson.objects.filter(membershippersonrealstart__value=False).first()
    person = membership.member.get_value().value

    new_source = Source.objects.order_by('?').first()

    post_data = {
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
def test_boolean_true_no_sources(setUp):
    membership = MembershipPerson.objects.filter(membershippersonrealstart__value=False).first()
    person = membership.member.get_value().value

    post_data = {
        'organization': membership.organization.get_value().value.id,
        'organization_source': [str(s.uuid) for s in membership.organization.get_sources()],
        'realstart': 'on',
    }

    response = setUp.post(reverse_lazy('edit-person-postings',
                                       kwargs={'person_id': person.uuid,
                                               'pk': membership.id}),
                          post_data)

    assert response.status_code == 200
    assert '"realstart" now has a value so it requires sources' in response.context['form'].errors['realstart']


@pytest.mark.django_db
def test_no_existing_sources(setUp):
    membership = MembershipPerson.objects.filter(membershippersonrealstart__value=False).first()
    person = membership.member.get_value().value

    membership.rank.get_value().sources.set([])

    post_data = {
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
