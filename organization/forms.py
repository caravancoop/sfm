from django import forms

from django.conf import settings
from django_date_extensions.fields import ApproximateDateFormField
from django.utils.translation import ugettext as _


class OrganizationForm(forms.Form):
    name = forms.CharField(error_messages={'required': _('Unit name is required')})
    name_text = forms.CharField()
    name_confidence = forms.ChoiceField(choices=settings.CONFIDENCE_LEVELS)

    classification = forms.CharField(error_messages={'required': _('Classification is required')})
    classification_text = forms.CharField()
    classification_confidence = forms.ChoiceField(choices=settings.CONFIDENCE_LEVELS)

    alias = forms.CharField(required=False)
    alias_confidence = forms.ChoiceField(required=False, choices=settings.CONFIDENCE_LEVELS)

    division_id = forms.CharField(error_messages={'required': _('Division ID is required')})
    division_confidence = forms.ChoiceField(choices=settings.CONFIDENCE_LEVELS)

    headquarters = forms.CharField(required=False)
    headquarters_confidence = forms.ChoiceField(required=False, choices=settings.CONFIDENCE_LEVELS)

    firstciteddate = ApproximateDateFormField(required=False)
    realstart = forms.BooleanField(required=False)
    firstciteddate_confidence = forms.ChoiceField(required=False, choices=settings.CONFIDENCE_LEVELS)

    lastciteddate = ApproximateDateFormField(required=False)
    open_ended = forms.ChoiceField(required=False, choices=settings.OPEN_ENDED_CHOICES)
    lastciteddate_confidence = forms.ChoiceField(required=False, choices=settings.CONFIDENCE_LEVELS)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.empty_permitted = False


class BaseOrganizationFormSet(forms.BaseFormSet):

    def clean(self):

        if self.errors:
            return

        for form in self.forms:
            # Check end date/open-ended pair
            open_ended = form.cleaned_data.get('open_ended')
            if open_ended == 'E':

                try:
                    # An end date must exist if the value of open_ended is "exact"
                    assert form.cleaned_data.get('lastciteddate')
                except AssertionError:
                    msg = _('If the value of open-ended is "Exact", a last cited date is required.')
                    form.add_error('lastciteddate', msg)


class OrganizationGeographyForm(forms.Form):
    geography_type = forms.ChoiceField(choices=(('Site', 'Site'), ('Area', 'Area'), ),
                                       error_messages={'required': _('Geography type is required')})
    name = forms.CharField(error_messages={'required': _('Name is required')})
    osm_id = forms.CharField(error_messages={'required': _('OSM ID is required')})
    osm_id_text = forms.CharField()
    startdate = ApproximateDateFormField(required=False)
    enddate = ApproximateDateFormField(required=False)
    org = forms.CharField()
    geotype = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.empty_permitted = False
