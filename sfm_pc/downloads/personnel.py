from collections import OrderedDict

from django.conf import settings
from django.db import models
from django.contrib.postgres import fields as pg_fields
from django_date_extensions.fields import ApproximateDateField

from .base import BaseDownload
from organization.models import Organization
from person.models import Person
from personextra.models import PersonExtra
from personbiography.models import PersonBiography
from membershipperson.models import MembershipPerson


class MembershipPersonDownload(BaseDownload):
    # Class metadata
    download_type = 'personnel'

    # Download fields
    org_id = models.UUIDField()
    name = models.TextField()
    name_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    name_confidence = models.CharField(max_length=1)
    division_id = models.TextField()
    division_id_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    division_id_confidence = models.CharField(max_length=1)
    classifications = pg_fields.ArrayField(models.TextField(), default=list)
    classifications_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    classifications_confidence = models.CharField(max_length=1)
    aliases = pg_fields.ArrayField(models.TextField(), default=list)
    aliases_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    aliases_confidence = models.CharField(max_length=1)
    firstciteddate = ApproximateDateField()
    firstciteddate_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    firstciteddate_confidence = models.CharField(max_length=1)
    lastciteddate = ApproximateDateField()
    lastciteddate_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    lastciteddate_confidence = models.CharField(max_length=1)
    realstart = models.NullBooleanField(default=None)
    realstart_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    realstart_confidence = models.CharField(max_length=1)
    open_ended = models.CharField(max_length=1, default='N', choices=settings.OPEN_ENDED_CHOICES)
    open_ended_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    open_ended_confidence = models.CharField(max_length=1)
    person_id = models.UUIDField()
    person_id_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    person_id_confidence = models.CharField(max_length=1)
    person_name = models.TextField()
    person_name_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    person_name_confidence = models.CharField(max_length=1)
    person_aliases = pg_fields.ArrayField(models.TextField(), default=list)
    person_aliases_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    person_aliases_confidence = models.CharField(max_length=1)
    person_division_id = models.TextField()
    person_division_id_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    person_division_id_confidence = models.CharField(max_length=1)
    person_date_of_birth = ApproximateDateField()
    person_date_of_birth_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    person_date_of_birth_confidence = models.CharField(max_length=1)
    person_date_of_death = ApproximateDateField()
    person_date_of_death_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    person_date_of_death_confidence = models.CharField(max_length=1)
    person_deceased = models.BooleanField()
    person_deceased_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    person_deceased_confidence = models.CharField(max_length=1)
    person_account_types = pg_fields.ArrayField(models.TextField(), default=list)
    person_account_types_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    person_account_types_confidence = models.CharField(max_length=1)
    person_accounts = pg_fields.ArrayField(models.TextField(), default=list)
    person_accounts_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    person_accounts_confidence = models.CharField(max_length=1)
    person_external_link_descriptions = pg_fields.ArrayField(models.TextField(), default=list)
    person_external_link_descriptions_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    person_external_link_descriptions_confidence = models.CharField(max_length=1)
    person_media_descriptions = pg_fields.ArrayField(models.TextField(), default=list)
    person_media_descriptions_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    person_media_descriptions_confidence = models.CharField(max_length=1)
    person_notes = pg_fields.ArrayField(models.TextField(), default=list)
    person_notes_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    person_notes_confidence = models.CharField(max_length=1)
    person_role = models.TextField()
    person_role_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    person_role_confidence = models.CharField(max_length=1)
    person_rank = models.TextField()
    person_rank_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    person_rank_confidence = models.CharField(max_length=1)
    person_title = models.TextField()
    person_title_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    person_title_confidence = models.CharField(max_length=1)
    person_firstciteddate = ApproximateDateField()
    person_firstciteddate_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    person_firstciteddate_confidence = models.CharField(max_length=1)
    person_firstciteddate_year = models.IntegerField()
    person_firstciteddate_month = models.IntegerField()
    person_firstciteddate_day = models.IntegerField()
    person_firstciteddate_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    person_firstciteddate_confidence = models.CharField(max_length=1)
    person_realstart = models.NullBooleanField(default=None)
    person_realstart_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    person_realstart_confidence = models.CharField(max_length=1)
    person_startcontext = models.TextField()
    person_startcontext_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    person_startcontext_confidence = models.CharField(max_length=1)
    person_lastciteddate = ApproximateDateField()
    person_lastciteddate_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    person_lastciteddate_confidence = models.CharField(max_length=1)
    person_lastciteddate_year = models.IntegerField()
    person_lastciteddate_month = models.IntegerField()
    person_lastciteddate_day = models.IntegerField()
    person_realend = models.NullBooleanField(default=None)
    person_realend_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    person_realend_confidence = models.CharField(max_length=1)
    person_endcontext = models.TextField()
    person_endcontext_sources = pg_fields.ArrayField(models.UUIDField(), default=list)
    person_endcontext_confidence = models.CharField(max_length=1)

    @classmethod
    def _get_field_map(cls):
        """
        Return metadata for each field defined on this model, to aid in serializing
        and exporing data.
        """
        return OrderedDict([
            ('org_id', {
                'sql': 'organization.uuid',
                'label': 'unit:id:admin',
                'serializer': cls.serializers['string'],
            }),
            ('name', {
                'sql': 'organization.name',
                'label': Organization.get_spreadsheet_field_name('name'),
                'serializer': cls.serializers['identity'],
            }),
            ('name_sources', {
                'sql': 'organization.name_sources',
                'label': Organization.get_spreadsheet_source_field_name('name'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('name_confidence', {
                'sql': 'organization.name_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('name'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('division_id', {
                'sql': 'organization.division_id',
                'label': Organization.get_spreadsheet_field_name('division_id'),
                'serializer': cls.serializers['division_id'],
            }),
            ('division_id_sources', {
                'sql': 'organization.division_id_sources',
                'label': Organization.get_spreadsheet_source_field_name('division_id'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('division_id_confidence', {
                'sql': 'organization.division_id_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('division_id'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('classifications', {
                'sql': 'organization.classifications',
                'label': Organization.get_spreadsheet_field_name('classification'),
                'serializer': cls.serializers['list'],
            }),
            ('classifications_sources', {
                'sql': 'organization.classifications_sources',
                'label': Organization.get_spreadsheet_source_field_name('classification'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('classifications_confidence', {
                'sql': 'organization.classifications_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('classification'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('aliases', {
                'sql': 'organization.aliases',
                'label': Organization.get_spreadsheet_field_name('aliases'),
                'serializer': cls.serializers['list'],
            }),
            ('aliases_sources', {
                'sql': 'organization.aliases_sources',
                'label': Organization.get_spreadsheet_source_field_name('aliases'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('aliases_confidence', {
                'sql': 'organization.aliases_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('aliases'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('firstciteddate', {
                'sql': 'organization.first_cited_date',
                'label': Organization.get_spreadsheet_field_name('firstciteddate'),
                'serializer': cls.serializers['identity'],
            }),
            ('firstciteddate_sources', {
                'sql': 'organization.first_cited_date_sources',
                'label': Organization.get_spreadsheet_source_field_name('firstciteddate'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('firstciteddate_confidence', {
                'sql': 'organization.first_cited_date_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('firstciteddate'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('lastciteddate', {
                'sql': 'organization.last_cited_date',
                'label': Organization.get_spreadsheet_field_name('lastciteddate'),
                'serializer': cls.serializers['identity'],
            }),
            ('lastciteddate_sources', {
                'sql': 'organization.last_cited_date_sources',
                'label': Organization.get_spreadsheet_source_field_name('lastciteddate'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('lastciteddate_confidence', {
                'sql': 'organization.last_cited_date_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('lastciteddate'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('realstart', {
                'sql': 'organization.real_start',
                'label': Organization.get_spreadsheet_field_name('realstart'),
                'serializer': cls.serializers['identity'],
            }),
            ('realstart_sources', {
                'sql': 'organization.real_start_sources',
                'label': Organization.get_spreadsheet_source_field_name('realstart'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('realstart_confidence', {
                'sql': 'organization.real_start_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('realstart'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('open_ended', {
                'sql': 'organization.open_ended',
                'label': Organization.get_spreadsheet_field_name('open_ended'),
                'serializer': cls.serializers['identity'],
            }),
            ('open_ended_sources', {
                'sql': 'organization.open_ended_sources',
                'label': Organization.get_spreadsheet_source_field_name('open_ended'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('open_ended_confidence', {
                'sql': 'organization.open_ended_confidence',
                'label': Organization.get_spreadsheet_confidence_field_name('open_ended'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('person_id', {
                'sql': 'person.uuid',
                'label': 'person:admin:id',
                'serializer': cls.serializers['string'],
            }),
            ('person_id_sources', {
                'sql': 'membership.person_id_sources',
                'label': 'person:posting:source',
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('person_id_confidence', {
                'sql': 'membership.person_id_confidence',
                'label': 'person:posting:confidence',
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('person_name', {
                'sql': 'person.name',
                'label': Person.get_spreadsheet_field_name('name'),
                'serializer': cls.serializers['identity'],
            }),
            ('person_name_sources', {
                'sql': 'person.name_sources',
                'label': Person.get_spreadsheet_source_field_name('name'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('person_name_confidence', {
                'sql': 'person.name_confidence',
                'label': Person.get_spreadsheet_confidence_field_name('name'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('person_aliases', {
                'sql': 'person.aliases',
                'label': Person.get_spreadsheet_field_name('aliases'),
                'serializer': cls.serializers['list'],
            }),
            ('person_aliases_sources', {
                'sql': 'person.aliases_sources',
                'label': Person.get_spreadsheet_source_field_name('aliases'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('person_aliases_confidence', {
                'sql': 'person.aliases_confidence',
                'label': Person.get_spreadsheet_confidence_field_name('aliases'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('person_division_id', {
                'sql': 'person.division_id',
                'label': Person.get_spreadsheet_field_name('division_id'),
                'serializer': cls.serializers['division_id'],
            }),
            ('person_division_id_sources', {
                'sql': 'person.division_id_sources',
                'label': Person.get_spreadsheet_source_field_name('division_id'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('person_division_id_confidence', {
                'sql': 'person.division_id_confidence',
                'label': Person.get_spreadsheet_confidence_field_name('division_id'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('person_date_of_birth', {
                'sql': 'person.date_of_birth',
                'label': PersonBiography.get_spreadsheet_field_name('date_of_birth'),
                'serializer': cls.serializers['list'],
            }),
            ('person_date_of_birth_sources', {
                'sql': 'person.date_of_birth_sources',
                'label': PersonBiography.get_spreadsheet_source_field_name('date_of_birth'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('person_date_of_birth_confidence', {
                'sql': 'person.date_of_birth_confidence',
                'label': PersonBiography.get_spreadsheet_confidence_field_name('date_of_birth'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('person_date_of_death', {
                'sql': 'person.date_of_death',
                'label': PersonBiography.get_spreadsheet_field_name('date_of_death'),
                'serializer': cls.serializers['list'],
            }),
            ('person_date_of_death_sources', {
                'sql': 'person.date_of_death_sources',
                'label': PersonBiography.get_spreadsheet_source_field_name('date_of_death'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('person_date_of_death_confidence', {
                'sql': 'person.date_of_death_confidence',
                'label': PersonBiography.get_spreadsheet_confidence_field_name('date_of_death'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('person_deceased', {
                'sql': 'person.deceased',
                'label': PersonBiography.get_spreadsheet_field_name('deceased'),
                'serializer': cls.serializers['list'],
            }),
            ('person_deceased_sources', {
                'sql': 'person.deceased_sources',
                'label': PersonBiography.get_spreadsheet_source_field_name('deceased'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('person_deceased_confidence', {
                'sql': 'person.deceased_confidence',
                'label': PersonBiography.get_spreadsheet_confidence_field_name('deceased'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('person_account_types', {
                'sql': 'person.account_types',
                'label': PersonExtra.get_spreadsheet_field_name('account_type'),
                'serializer': cls.serializers['list'],
            }),
            ('person_account_types_sources', {
                'sql': 'person.account_types_sources',
                'label': PersonExtra.get_spreadsheet_source_field_name('account_type'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('person_account_types_confidence', {
                'sql': 'person.account_types_confidence',
                'label': PersonExtra.get_spreadsheet_confidence_field_name('account_type'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('person_accounts', {
                'sql': 'person.accounts',
                'label': PersonExtra.get_spreadsheet_field_name('account'),
                'serializer': cls.serializers['list'],
            }),
            ('person_accounts_sources', {
                'sql': 'person.accounts_sources',
                'label': PersonExtra.get_spreadsheet_source_field_name('account'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('person_accounts_confidence', {
                'sql': 'person.accounts_confidence',
                'label': PersonExtra.get_spreadsheet_confidence_field_name('account'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('person_external_link_descriptions', {
                'sql': 'person.external_link_descriptions',
                'label': PersonExtra.get_spreadsheet_field_name('external_link_description'),
                'serializer': cls.serializers['list'],
            }),
            ('person_external_link_descriptions_sources', {
                'sql': 'person.external_link_descriptions_sources',
                'label': PersonExtra.get_spreadsheet_source_field_name('external_link_description'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('person_external_link_descriptions_confidence', {
                'sql': 'person.external_link_descriptions_confidence',
                'label': PersonExtra.get_spreadsheet_confidence_field_name('external_link_description'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('person_media_descriptions', {
                'sql': 'person.media_descriptions',
                'label': PersonExtra.get_spreadsheet_field_name('media_description'),
                'serializer': cls.serializers['list'],
            }),
            ('person_media_descriptions_sources', {
                'sql': 'person.media_descriptions_sources',
                'label': PersonExtra.get_spreadsheet_source_field_name('media_description'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('person_media_descriptions_confidence', {
                'sql': 'person.media_descriptions_confidence',
                'label': PersonExtra.get_spreadsheet_confidence_field_name('media_description'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('person_notes', {
                'sql': 'person.notes',
                'label': PersonExtra.get_spreadsheet_field_name('notes'),
                'serializer': cls.serializers['list'],
            }),
            ('person_notes_sources', {
                'sql': 'person.notes_sources',
                'label': PersonExtra.get_spreadsheet_source_field_name('notes'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('person_notes_confidence', {
                'sql': 'person.notes_confidence',
                'label': PersonExtra.get_spreadsheet_confidence_field_name('notes'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('person_role', {
                'sql': 'membership.role',
                'label': MembershipPerson.get_spreadsheet_field_name('role'),
                'serializer': cls.serializers['identity'],
            }),
            ('person_role_sources', {
                'sql': 'membership.role_sources',
                'label': MembershipPerson.get_spreadsheet_source_field_name('role'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('person_role_confidence', {
                'sql': 'membership.role_confidence',
                'label': MembershipPerson.get_spreadsheet_confidence_field_name('role'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('person_rank', {
                'sql': 'membership.rank',
                'label': MembershipPerson.get_spreadsheet_field_name('rank'),
                'serializer': cls.serializers['identity'],
            }),
            ('person_rank_sources', {
                'sql': 'membership.rank_sources',
                'label': MembershipPerson.get_spreadsheet_source_field_name('rank'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('person_rank_confidence', {
                'sql': 'membership.rank_confidence',
                'label': MembershipPerson.get_spreadsheet_confidence_field_name('rank'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('person_title', {
                'sql': 'membership.title',
                'label': MembershipPerson.get_spreadsheet_field_name('title'),
                'serializer': cls.serializers['identity'],
            }),
            ('person_title_sources', {
                'sql': 'membership.title_sources',
                'label': MembershipPerson.get_spreadsheet_source_field_name('title'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('person_title_confidence', {
                'sql': 'membership.title_confidence',
                'label': MembershipPerson.get_spreadsheet_confidence_field_name('title'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('person_firstciteddate', {
                'sql': 'membership.first_cited_date',
                'label': MembershipPerson.get_spreadsheet_field_name('firstciteddate'),
                'serializer': cls.serializers['identity'],
            }),
            ('person_firstciteddate_year', {
                'sql': 'membership.first_cited_date_year',
                'label': MembershipPerson.get_spreadsheet_field_name('firstciteddate') + ':year',
                'serializer': cls.serializers['identity'],
            }),
            ('person_firstciteddate_month', {
                'sql': 'membership.first_cited_date_month',
                'label': MembershipPerson.get_spreadsheet_field_name('firstciteddate') + ':month',
                'serializer': cls.serializers['identity'],
            }),
            ('person_firstciteddate_day', {
                'sql': 'membership.first_cited_date_day',
                'label': MembershipPerson.get_spreadsheet_field_name('firstciteddate') + ':day',
                'serializer': cls.serializers['identity'],
            }),
            ('person_firstciteddate_sources', {
                'sql': 'membership.first_cited_date_sources',
                'label': MembershipPerson.get_spreadsheet_source_field_name('firstciteddate'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('person_firstciteddate_confidence', {
                'sql': 'membership.first_cited_date_confidence',
                'label': MembershipPerson.get_spreadsheet_confidence_field_name('firstciteddate'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('person_realstart', {
                'sql': 'membership.real_start',
                'label': MembershipPerson.get_spreadsheet_field_name('realstart'),
                'serializer': cls.serializers['identity'],
            }),
            ('person_realstart_sources', {
                'sql': 'membership.real_start_sources',
                'label': MembershipPerson.get_spreadsheet_source_field_name('realstart'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('person_realstart_confidence', {
                'sql': 'membership.real_start_confidence',
                'label': MembershipPerson.get_spreadsheet_confidence_field_name('realstart'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('person_startcontext', {
                'sql': 'membership.start_context',
                'label': MembershipPerson.get_spreadsheet_field_name('startcontext'),
                'serializer': cls.serializers['identity'],
            }),
            ('person_startcontext_sources', {
                'sql': 'membership.start_context_sources',
                'label': MembershipPerson.get_spreadsheet_source_field_name('startcontext'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('person_startcontext_confidence', {
                'sql': 'membership.start_context_confidence',
                'label': MembershipPerson.get_spreadsheet_confidence_field_name('startcontext'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('person_lastciteddate', {
                'sql': 'membership.last_cited_date',
                'label': MembershipPerson.get_spreadsheet_field_name('lastciteddate'),
                'serializer': cls.serializers['identity'],
            }),
            ('person_lastciteddate_year', {
                'sql': 'membership.last_cited_date_year',
                'label': MembershipPerson.get_spreadsheet_field_name('lastciteddate') + ':year',
                'serializer': cls.serializers['identity'],
            }),
            ('person_lastciteddate_month', {
                'sql': 'membership.last_cited_date_month',
                'label': MembershipPerson.get_spreadsheet_field_name('lastciteddate') + ':month',
                'serializer': cls.serializers['identity'],
            }),
            ('person_lastciteddate_day', {
                'sql': 'membership.last_cited_date_day',
                'label': MembershipPerson.get_spreadsheet_field_name('lastciteddate') + ':day',
                'serializer': cls.serializers['identity'],
            }),
            ('person_lastciteddate_sources', {
                'sql': 'membership.last_cited_date_sources',
                'label': MembershipPerson.get_spreadsheet_source_field_name('lastciteddate'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('person_lastciteddate_confidence', {
                'sql': 'membership.last_cited_date_confidence',
                'label': MembershipPerson.get_spreadsheet_confidence_field_name('lastciteddate'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('person_realend', {
                'sql': 'membership.real_end',
                'label': MembershipPerson.get_spreadsheet_field_name('realend'),
                'serializer': cls.serializers['identity'],
            }),
            ('person_realend_sources', {
                'sql': 'membership.real_end_sources',
                'label': MembershipPerson.get_spreadsheet_source_field_name('realend'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('person_realend_confidence', {
                'sql': 'membership.real_end_confidence',
                'label': MembershipPerson.get_spreadsheet_confidence_field_name('realend'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
            ('person_endcontext', {
                'sql': 'membership.end_context',
                'label': MembershipPerson.get_spreadsheet_field_name('endcontext'),
                'serializer': cls.serializers['identity'],
            }),
            ('person_endcontext_sources', {
                'sql': 'membership.end_context_sources',
                'label': MembershipPerson.get_spreadsheet_source_field_name('endcontext'),
                'source': True,
                'serializer': cls.serializers['list'],
            }),
            ('person_endcontext_confidence', {
                'sql': 'membership.end_context_confidence',
                'label': MembershipPerson.get_spreadsheet_confidence_field_name('endcontext'),
                'confidence': True,
                'serializer': cls.serializers['identity'],
            }),
        ])
