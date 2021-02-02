from django.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from django.conf import settings

from django_date_extensions.fields import ApproximateDateField

from complex_fields.model_decorators import versioned, sourced, sourced_optional

from complex_fields.models import ComplexField, ComplexFieldContainer
from complex_fields.base_models import BaseModel
from organization.models import Organization
from sfm_pc.models import GetComplexFieldNameMixin


class MembershipOrganization(models.Model, BaseModel, GetComplexFieldNameMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.member = ComplexFieldContainer(self, MembershipOrganizationMember)
        self.organization = ComplexFieldContainer(self, MembershipOrganizationOrganization)
        self.firstciteddate = ComplexFieldContainer(self, MembershipOrganizationFirstCitedDate)
        self.realstart = ComplexFieldContainer(self, MembershipOrganizationRealStart)
        self.lastciteddate = ComplexFieldContainer(self, MembershipOrganizationLastCitedDate)
        self.open_ended = ComplexFieldContainer(self, MembershipOrganizationOpenEnded)

        self.complex_fields = [self.member, self.organization,
                               self.firstciteddate, self.lastciteddate,
                               self.realstart, self.open_ended]

        self.complex_lists = []

        self.required_fields = [
            "MembershipOrganization_MembershipOrganizationMember",
            "MembershipOrganization_MembershipOrganizationOrganization",
        ]

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
class MembershipOrganizationMember(ComplexField):
    object_ref = models.ForeignKey('MembershipOrganization')
    value = models.ForeignKey(Organization, default=None, blank=True, null=True)
    field_name = _("Member Unit")

    class Meta:
        db_table = 'membershiporganization_m'


@versioned
@sourced
class MembershipOrganizationOrganization(ComplexField):
    object_ref = models.ForeignKey('MembershipOrganization')
    value = models.ForeignKey(Organization)
    field_name = _("Membership")
    shortcode = 'u_ru'
    spreadsheet_field_name = 'unit:related_unit'

    class Meta:
        db_table = 'membershiporganization_moo'


@versioned
@sourced
class MembershipOrganizationFirstCitedDate(ComplexField):
    object_ref = models.ForeignKey('MembershipOrganization')
    value = ApproximateDateField()
    field_name = _("First Cited Date")
    shortcode = 'u_rufcd'
    spreadsheet_field_name = 'unit:related_unit_first_cited_date'

    class Meta:
        db_table = 'membershiporganization_fcd'


@versioned
@sourced
class MembershipOrganizationLastCitedDate(ComplexField):
    object_ref = models.ForeignKey('MembershipOrganization')
    value = ApproximateDateField()
    field_name = _("Last Cited Date")
    shortcode = 'u_rulcd'
    spreadsheet_field_name = 'unit:related_unit_last_cited_date'

    class Meta:
        db_table = 'membershiporganization_lcd'


@versioned
@sourced_optional
class MembershipOrganizationRealStart(ComplexField):
    object_ref = models.ForeignKey('MembershipOrganization')
    value = models.NullBooleanField(default=None)
    field_name = _("Start Date?")
    shortcode = 'u_rufcds'
    spreadsheet_field_name = 'unit:related_unit_first_cited_date_start'


@versioned
@sourced_optional
class MembershipOrganizationOpenEnded(ComplexField):
    object_ref = models.ForeignKey('MembershipOrganization')
    value = models.CharField(default='N', max_length=1, choices=settings.OPEN_ENDED_CHOICES)
    field_name = _("Is Open Ended?")
    shortcode = 'u_ruo'
    spreadsheet_field_name = 'unit:related_unit_open'
