from collections import namedtuple

from django.forms import ModelForm

from django.db import connection
from django.contrib.gis.forms.widgets import BaseGeometryWidget

from .models import Location


class LocationForm(ModelForm):

    class Meta:
        model = Location
        fields = '__all__'
        widgets = {
            'geometry': BaseGeometryWidget()
        }

    def save(self, commit=True):
        location = super().save()

        relations = Location.objects.filter(geometry__overlaps=location.geometry).exclude(id=location.id)

        for relation in relations:

            # check if the relation is bigger than the current location

            if relation.geometry.area > location.geometry.area:

                if relation.adminlevel == '4':
                    location.adminlevel2 = relation
                elif relation.adminlevel == '6':
                    location.adminlevel1 = relation

            elif location.adminlevel == '4':
                relation.adminlevel2 = location
            elif location.adminlevel == '6':
                relation.adminlevel1 = location

            relation.save()

        location.save()

        return location
