from django import forms

from leaflet.forms.widgets import LeafletWidget
from .models import ViolationLocation


class ZoneForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ZoneForm, self).__init__(*args, **kwargs)
        self.fields['value'].widget = LeafletWidget(attrs={
            "id": "Violation_ViolationLocation"
        })

    class Meta:
        model = ViolationLocation
        fields = ('value',)
        widgets = {'value': LeafletWidget()}
