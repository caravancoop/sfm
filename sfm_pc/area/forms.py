from django import forms

from leaflet.forms.widgets import LeafletWidget
from .models import AreaGeometry


class ZoneForm(forms.ModelForm):
    id = "Area_AreaGeometry"

    def __init__(self, *args, **kwargs):
        super(ZoneForm, self).__init__(*args, **kwargs)
        self.fields['value'].widget = LeafletWidget(attrs={
            "id": "Area_AreaGeometry"
        })

    class Meta:
        model = AreaGeometry
        fields = ('value',)
        widgets = {'value': LeafletWidget()}


