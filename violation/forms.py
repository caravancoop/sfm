from django import forms

from django.conf import settings
from django_date_extensions.fields import ApproximateDateFormField

from leaflet.forms.widgets import LeafletWidget
from .models import ViolationLocation


class ViolationForm(forms.Form):
    violation_id = forms.CharField(required=True)

    startdate = ApproximateDateFormField(required=True)
    startdate_confidence = forms.ChoiceField(choices=settings.CONFIDENCE_LEVELS)
    enddate = ApproximateDateFormField(required=True)
    enddate_confidence = forms.ChoiceField(choices=settings.CONFIDENCE_LEVELS)

    firstallegation = ApproximateDateFormField(required=False)
    firstallegation_confidence = forms.ChoiceField(required=False, choices=settings.CONFIDENCE_LEVELS)
    lastupdate = ApproximateDateFormField(required=False)
    lastupdate_confidence = forms.ChoiceField(required=False, choices=settings.CONFIDENCE_LEVELS)

    locationdescription = forms.CharField(required=False)
    locationdescription_confidence = forms.ChoiceField(required=False, choices=settings.CONFIDENCE_LEVELS)
    status = forms.CharField(required=False)
    status_confidence = forms.CharField(required=False)

    osm_id = forms.CharField(required=False)
    osm_id_text = forms.CharField(required=False)
    osm_confidence = forms.ChoiceField(required=False, choices=settings.CONFIDENCE_LEVELS)

    exactlocation_id = forms.CharField(required=False)
    exactlocation_confidence = forms.ChoiceField(required=False, choices=settings.CONFIDENCE_LEVELS)
    exactlocation_text = forms.CharField(required=False)

    description = forms.CharField(required=True)
    description_confidence = forms.ChoiceField(choices=settings.CONFIDENCE_LEVELS)

    perpetrators = forms.CharField(required=False)
    perp_confidence = forms.ChoiceField(required=False, choices=settings.CONFIDENCE_LEVELS)

    orgs = forms.CharField(required=False)
    orgs_confidence = forms.ChoiceField(required=False, choices=settings.CONFIDENCE_LEVELS)

    vtype = forms.CharField(required=False)
    type_confidence = forms.ChoiceField(required=False, choices=settings.CONFIDENCE_LEVELS)


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
