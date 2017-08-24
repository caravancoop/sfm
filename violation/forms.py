from django import forms

from django_date_extensions.fields import ApproximateDateFormField

from leaflet.forms.widgets import LeafletWidget
from .models import ViolationLocation

class ViolationForm(forms.Form):
    startdate = ApproximateDateFormField(required=True)
    enddate = ApproximateDateFormField(required=True)
    locationdescription = forms.CharField(required=False)
    osm_id = forms.CharField(required=False)
    osm_id_text = forms.CharField(required=False)
    description = forms.CharField(required=True)
    perpetrators = forms.CharField(required=False)
    orgs = forms.CharField(required=False)
    vtype = forms.CharField(required=False)
    geotype = forms.CharField(required=False)
    # also has source and confidence

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
