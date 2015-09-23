from django.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import get_language

from django_date_extensions.fields import ApproximateDateField
from source.models import Source

from complex_fields.model_decorators import versioned, translated, sourced
from complex_fields.models import (ComplexField, ComplexFieldContainer,
                                   ComplexFieldListContainer)
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

        self.date = ComplexFieldListContainer(self, MembershipDate)

    @property
    def start_date(self):
        if self.real_start.get_value():
            dates = MembershipDate.objects.filter(object_ref=self).order_by("value")
            return dates[0].value
        return None

    @property
    def end_date(self):
        if self.real_end.get_value():
            dates = MembershipDate.objects.filter(object_ref=self).order_by("-value")
            return dates[0].value
        return None

    @classmethod
    def from_id(cls, id_):
        try:
            membership = cls.objects.get(id=id_)
            return membership
        except cls.DoesNotExist:
            return None


    def validate(self, dict_values, lang):
        errors = {}
        for field in self.complex_fields:
            field_name = field.get_field_str_id()
            sources = dict_values[field_name].get('sources', [])

            error = field.validate(dict_values[field_name], lang, sources)
            if error is not None:
                errors[field_name] = error

        return errors

    def update(self, dict_values, lang=get_language()):
        # Add dates treatment
        errors = self.validate(dict_values, lang)
        if len(errors):
            return errors

        for field in self.complex_fields:
            field_name = field.get_field_str_id()

            source = Source.create_sources(dict_values[field_name].get('sources', []))
            field.update(dict_values[field_name]['values'], lang, sources)

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

    @property
    def field_name(self):
        name = ""
        if self.object_ref_id:
            if self.value == self.object_ref.start_date:
                name = _("Real start")
            if self.value == self.object_ref.end_date:
                name = _("Real end")
        return name



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
