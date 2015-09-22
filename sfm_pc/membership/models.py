from django.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import get_language

from django_date_extensions.fields import ApproximateDateField
from source.models import Source

from complex_fields.model_decorators import versioned, translated, sourced
from complex_fields.models import ComplexField, ComplexFieldContainer
from person.models import Person
from organization.models import Organization


class Membership(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.person = ComplexFieldContainer(self, MembershipPerson)
        self.organization = ComplexFieldContainer(self, MembershipOrganization)
        self.role = ComplexFieldContainer(self, MembershipRole)
        self.title = ComplexFieldContainer(self, MembershipTitle)
        self.rank = ComplexFieldContainer(self, MembershipRank)
        self.real_start = ComplexFieldContainer(self, MembershipRealStart)
        self.real_end = ComplexFieldContainer(self, MembershipRealEnd)
        self.start_context = ComplexFieldContainer(self, MembershipStartContext)
        self.end_context = ComplexFieldContainer(self, MembershipEndContext)

        self.complex_fields = [self.person, self.organization, self.role,
                               self.title, self.rank]


@versioned
@sourced
class MembershipPerson(ComplexField):
    object_ref = models.ForeignKey('Membership')
    value = models.ForeignKey(Person)
    field_name = _("Person")


@versioned
@sourced
class MembershipOrganization(ComplexField):
    object_ref = models.ForeignKey('Membership')
    value = models.ForeignKey(Organization)
    field_name = _("Organization")


@versioned
@sourced
class MembershipRole(ComplexField):
    object_ref = models.ForeignKey('Membership')
    value = models.ForeignKey('Role', default=None, blank=True, null=True)
    field_name = _("Role")


@translated
@versioned
@sourced
class MembershipTitle(ComplexField):
    object_ref = models.ForeignKey('Membership')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Title")


@versioned
@sourced
class MembershipRank(ComplexField):
    object_ref = models.ForeignKey('Membership')
    value = models.ForeignKey('Rank', default=None, blank=True, null=True)
    field_name = _("Rank")


@versioned
@sourced
class MembershipDate(ComplexField):
    object_ref = models.ForeignKey('Membership')
    value = ApproximateDateField()
    field_name = _("Dates")


@versioned
@sourced
class MembershipRealStart(ComplexField):
    object_ref = models.ForeignKey('Membership')
    value = models.BooleanField(default=None)
    field_name = _("Real start date")


@versioned
@sourced
class MembershipRealEnd(ComplexField):
    object_ref = models.ForeignKey('Membership')
    value = models.BooleanField(default=None)
    field_name = _("Real end date")


@versioned
@sourced
class MembershipStartContext(ComplexField):
    object_ref = models.ForeignKey('Membership')
    value = models.ForeignKey('Context')
    field_name = _("Start context")


@versioned
@sourced
class MembershipEndContext(ComplexField):
    object_ref = models.ForeignKey('Membership')
    value = models.ForeignKey('Context')
    field_name = _("End context")


class Role(models.Model):
    value = models.TextField()

class Rank(models.Model):
    value = models.TextField()

class Context(models.Model):
    value = models.TextField()
