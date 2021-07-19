from django.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from django.core.urlresolvers import reverse
from django_date_extensions.fields import ApproximateDateField

from complex_fields.model_decorators import (versioned, translated, sourced,
                                             sourced_optional)
from complex_fields.models import ComplexField, ComplexFieldContainer
from complex_fields.base_models import BaseModel

from person.models import Person
from organization.models import Organization
from sfm_pc.models import GetComplexFieldNameMixin
from source.mixins import SourcesMixin


class MembershipPerson(models.Model, BaseModel, SourcesMixin, GetComplexFieldNameMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.member = ComplexFieldContainer(self, MembershipPersonMember)
        self.organization = ComplexFieldContainer(self, MembershipPersonOrganization)
        self.role = ComplexFieldContainer(self, MembershipPersonRole)
        self.title = ComplexFieldContainer(self, MembershipPersonTitle)
        self.rank = ComplexFieldContainer(self, MembershipPersonRank)
        self.realstart = ComplexFieldContainer(self, MembershipPersonRealStart)
        self.realend = ComplexFieldContainer(self, MembershipPersonRealEnd)
        self.startcontext = ComplexFieldContainer(self, MembershipPersonStartContext)
        self.endcontext = ComplexFieldContainer(self, MembershipPersonEndContext)
        self.firstciteddate = ComplexFieldContainer(self, MembershipPersonFirstCitedDate)
        self.lastciteddate = ComplexFieldContainer(self, MembershipPersonLastCitedDate)

        self.complex_fields = [self.member, self.organization, self.role,
                               self.title, self.rank, self.realstart, self.realend,
                               self.startcontext, self.endcontext,
                               self.firstciteddate, self.lastciteddate]

        self.complex_lists = []

        self.required_fields = [
            "MembershipPerson_MembershipPersonMember",
            "MembershipPerson_MembershipPersonOrganization",
        ]

    @property
    def short_description(self):
        '''
        Get a description string (as HTML) for information on this membership,
        such as:

        "General Officer Commanding, Major General, Commander of 82 Division
        (Military/Army, Nigeria) on 1st January 2013"
        '''

        obj = self

        # Start with the epithets (title, rank, and role)
        description = '<strong>'

        epithets = [obj.title.get_value(),
                    obj.rank.get_value(),
                    obj.role.get_value()]

        epithets = [str(ep.value) for ep in epithets if ep is not None]

        if len(epithets) == 1:
            description += epithets[0] + '</strong>'

        elif len(epithets) == 2 or len(epithets) == 3:
            separator = '</strong>, <strong>'
            description += separator.join(epithets) + '</strong>'

        else:
            # Length must be 0, so use a generic title
            description = _('Member')

        # Member organization
        description += ' '

        organization = obj.organization.get_value().value

        href = reverse('view-organization', args=(organization.uuid,))

        # Translators: This is part of the string "{Rank} of {unit}"
        joiner = _('of')

        org_string = joiner + ' <strong><a href="{href}">{org}</a></strong>'

        description += org_string.format(org=organization,
                                         href=href)

        # Classifications
        description += ' '

        classifications = organization.classification.get_list()
        if classifications:
            classifications = '/'.join(str(clss) for clss in classifications
                                       if clss is not None)

            description += '(%s)' % classifications

        # Last cited date
        description += ' '

        last_cited = obj.lastciteddate.get_value()
        if last_cited:
            # Translators: This is part of the "Last seen as" string for a person,
            # as in "last seen as {rank} of {unit} on {date}"
            date_joiner = _('on')
            date_string = date_joiner + ' <strong>%s</strong>' % last_cited
            description += date_string

        return description

    @classmethod
    def from_id(cls, id_):
        try:
            membership = cls.objects.get(id=id_)
            return membership
        except cls.DoesNotExist:
            return None

    def get_value(self):
        return '{0} member of {1}'.format(self.member.get_value(),
                                          self.organization.get_value())

    @classmethod
    def create(cls, dict_values, lang=get_language()):
        membership = cls()
        membership.update(dict_values, lang)
        return membership


@versioned
@sourced
class MembershipPersonMember(ComplexField):

    object_ref = models.ForeignKey('MembershipPerson')
    value = models.ForeignKey(Person, default=None, blank=True, null=True)
    field_name = _("Member")


@versioned
@sourced
class MembershipPersonOrganization(ComplexField):
    object_ref = models.ForeignKey('MembershipPerson')
    value = models.ForeignKey(Organization)
    field_name = _("Unit")
    shortcode = 'p_puid_a'
    spreadsheet_field_name = 'person:posting_unit_id:admin'


@versioned
@sourced
class MembershipPersonRole(ComplexField):
    object_ref = models.ForeignKey('MembershipPerson')
    value = models.ForeignKey('Role', default=None, blank=True, null=True)
    field_name = _("Role")
    shortcode = 'p_pro'
    spreadsheet_field_name = 'person:posting_role'


@translated
@versioned
@sourced
class MembershipPersonTitle(ComplexField):
    object_ref = models.ForeignKey('MembershipPerson')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Official Title")
    shortcode = 'p_pt'
    spreadsheet_field_name = 'person:posting_title'


@versioned
@sourced
class MembershipPersonRank(ComplexField):
    object_ref = models.ForeignKey('MembershipPerson')
    value = models.ForeignKey('Rank', default=None, blank=True, null=True)
    field_name = _("Rank")
    shortcode = 'p_pra'
    spreadsheet_field_name = 'person:posting_rank'


@versioned
@sourced
class MembershipPersonFirstCitedDate(ComplexField):
    object_ref = models.ForeignKey('MembershipPerson')
    value = ApproximateDateField()
    field_name = _("First Cited Date")
    shortcode = 'p_pfcd'
    spreadsheet_field_name = 'person:posting_first_cited_date'


@versioned
@sourced
class MembershipPersonLastCitedDate(ComplexField):
    object_ref = models.ForeignKey('MembershipPerson')
    value = ApproximateDateField()
    field_name = _("Last Cited Date")
    shortcode = 'p_plcd'
    spreadsheet_field_name = 'person:posting_last_cited_date'


@versioned
@sourced_optional
class MembershipPersonRealStart(ComplexField):
    object_ref = models.ForeignKey('MembershipPerson')
    value = models.BooleanField(default=None)
    field_name = _("Start Date?")
    shortcode = 'p_pfcds'
    spreadsheet_field_name = 'person:posting_first_cited_date_start'


@versioned
@sourced_optional
class MembershipPersonRealEnd(ComplexField):
    object_ref = models.ForeignKey('MembershipPerson')
    value = models.BooleanField(default=None)
    field_name = _("End Date?")
    shortcode = 'p_plcde'
    spreadsheet_field_name = 'person:posting_last_cited_date_end'


@versioned
@sourced
class MembershipPersonStartContext(ComplexField):
    object_ref = models.ForeignKey('MembershipPerson')
    value = models.TextField()
    field_name = _("Start Date Context")
    shortcode = 'p_pfcdsc'
    spreadsheet_field_name = 'person:posting_first_cited_date_start_context'


@versioned
@sourced
class MembershipPersonEndContext(ComplexField):
    object_ref = models.ForeignKey('MembershipPerson')
    value = models.TextField()
    field_name = _("End Date Context")
    shortcode = 'p_plcdec'
    spreadsheet_field_name = 'person:posting_last_cited_date_end_context'


class Role(models.Model):
    value = models.TextField()

    @classmethod
    def get_role_list(cls):
        roles = cls.objects.all()
        roles = [
            role.value
            for role in roles
        ]

        return roles

    def __str__(self):
        return self.value


class Rank(models.Model):
    value = models.TextField()

    def __str__(self):
        return self.value
