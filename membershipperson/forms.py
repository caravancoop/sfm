from django import forms

from django_date_extensions.fields import ApproximateDateFormField

from membershipperson.models import MembershipPerson


class MembershipPersonForm(forms.Form):
    membership = forms.ModelChoiceField(queryset=MembershipPerson.objects.all())
    role = forms.CharField(required=False)
    title = forms.CharField(required=False)
    rank = forms.CharField(required=False)
    realstart = forms.BooleanField(required=False)
    realend = forms.BooleanField(required=False)
    startcontext = forms.CharField(required=False)
    endcontext = forms.CharField(required=False)
    firstciteddate = ApproximateDateFormField(required=False)
    lastciteddate = ApproximateDateFormField(required=False)
    first = forms.BooleanField(required=False)
