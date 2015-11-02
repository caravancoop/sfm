from django import forms

from leaflet.forms.widgets import LeafletWidget
from .models import GeositeCoordinates


class ZoneForm(forms.ModelForm):
    id = "Geosite_GeositeCoordinates"

    def __init__(self, *args, **kwargs):
        super(ZoneForm, self).__init__(*args, **kwargs)
        self.fields['value'].widget = LeafletWidget(attrs={
            "id": "Geosite_GeositeCoordinates"
        })

    class Meta:
        model = GeositeCoordinates
        fields = ('value',)
        widgets = {'value': LeafletWidget()}
