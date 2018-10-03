from django.forms import ModelForm

from .models import Location

from django.contrib.gis.forms.widgets import BaseGeometryWidget


class LocationForm(ModelForm):

    class Meta:
        model = Location
        fields = '__all__'
        widgets = {
            'geometry': BaseGeometryWidget()
        }
