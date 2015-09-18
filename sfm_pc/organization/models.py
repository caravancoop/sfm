from django.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from source.models import Source

from complex_fields.model_decorators import versioned, translated, sourced
from complex_fields.models import ComplexField, ComplexFieldContainer


class Organization(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_organization = ComplexFieldContainer(self, ParentOrganization)

        self.complex_fields = [self.parent_organization]

    @classmethod
    def create(cls, dict_values, lang=get_language()):
        org = cls()
        org.save()
        org.update(dict_values, lang)
        return org


@versioned
@sourced
class ParentOrganization(ComplexField):
    object_ref = models.ForeignKey('Organization', related_name="child_org")
    #value = models.TextField()
    value = models.ForeignKey(
        'Organization',
        related_name="parent_org",
        default=None,
        blank=True,
        null=True
    )
    field_name = _("Parent organization")
