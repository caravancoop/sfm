from django.db import models
from django.contrib.gis.geos import Point
from django.utils.translation import ugettext as _
from django.db.models import Max

from django_date_extensions.fields import ApproximateDateField

from complex_fields.model_decorators import versioned, translated, sourced
from complex_fields.models import ComplexField, ComplexFieldContainer, \
    ComplexFieldListContainer
from complex_fields.base_models import BaseModel


class Person(models.Model, BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ComplexFieldContainer(self, PersonName)
        self.aliases = ComplexFieldListContainer(self, PersonAlias)
        self.division_id = ComplexFieldContainer(self, PersonDivisionId)
        
        self.complex_fields = [self.name]

        self.required_fields = [
            "Person_PersonName",
        ]

    def get_value(self):
        return self.name.get_value()

    def __str__(self):
        return str(self.name)

    @classmethod
    def search(cls, terms):
        order_by = terms.get('orderby')
        if not order_by:
            order_by = 'personname__value'
        elif order_by in ['name']:
            order_by = 'person' + order_by + '__value'

        direction = terms.get('direction')
        if not direction:
            direction = 'ASC'

        dirsym = ''
        if direction == 'DESC':
            dirsym = '-'

        person_query = (cls.objects
                        .annotate(Max(order_by))
                        .order_by(dirsym + order_by + "__max"))

        name = terms.get('name')
        if name:
            person_query = person_query.filter(personname__value__icontains=name)

        alias_val = terms.get('alias')
        if alias_val:
            person_query = person_query.filter(personalias__value__icontains=alias_val)

        role = terms.get('role_membership')
        if role:
            person_query = person_query.filter(
                membershippersonmember__object_ref__membershiprole__value__value=role
            )

        latitude = terms.get('latitude')
        longitude = terms.get('longitude')
        if latitude and longitude:
            try:
                latitude = float(latitude)
                longitude = float(longitude)
            except ValueError:
                latitude = 0
                longitude = 0

            point = Point(latitude, longitude)
            radius = terms.get('radius')
            if radius:
                try:
                    radius = float(radius)
                except ValueError:
                    radius = 0
                person_query = person_query.filter(
                    membershippersonmember__object_ref__membershiporganization__value__associationorganization__object_ref__associationarea__value__areageometry__value__dwithin=(point, radius)
                )
            else:
                person_query = person_query.filter(
                    membershippersonmember__object_ref__membershiporganization__value__associationorganization__object_ref__associationarea__value__areageometry__value__bbcontains=point
                )

        return person_query


@translated
@versioned
@sourced
class PersonName(ComplexField):
    object_ref = models.ForeignKey('Person')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Name")


@translated
@versioned
@sourced
class PersonAlias(ComplexField):
    object_ref = models.ForeignKey('Person')
    value = models.ForeignKey('Alias', default=None, blank=True, null=True)
    field_name = _("Alias")

class Alias(models.Model):
    value = models.TextField()
    
    def __str__(self):
        return self.value

@versioned
@sourced
class PersonDivisionId(ComplexField):
    object_ref = models.ForeignKey('Person')
    value = models.TextField(default=None, blank=True, null=True)

    field_name = _('Division ID')
