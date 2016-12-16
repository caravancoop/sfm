from django import forms

from django_date_extensions.fields import ApproximateDateFormField


class MembershipOrganizationForm(forms.Form):
    member = forms.CharField()
    organization = forms.CharField()
    firstciteddate = ApproximateDateFormField(required=False)
    lastciteddate = ApproximateDateFormField(required=False)
