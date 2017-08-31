from django import forms
from django.conf import settings

from django_date_extensions.fields import ApproximateDateFormField


class MembershipOrganizationForm(forms.Form):
    member = forms.CharField()
    organization = forms.CharField()
    organization_confidence = forms.ChoiceField(choices=settings.CONFIDENCE_LEVELS)

    firstciteddate = ApproximateDateFormField(required=False)
    lastciteddate = ApproximateDateFormField(required=False)
    date_confidence = forms.ChoiceField(choices=settings.CONFIDENCE_LEVELS)
