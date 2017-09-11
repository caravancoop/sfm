from django import forms
from django.conf import settings

from django_date_extensions.fields import ApproximateDateFormField

from membershipperson.models import MembershipPerson


class MembershipPersonForm(forms.Form):
    membership = forms.ModelChoiceField(queryset=MembershipPerson.objects.all())
    first = forms.BooleanField(required=False)

    title = forms.CharField(required=False)
    title_confidence = forms.ChoiceField(choices=settings.CONFIDENCE_LEVELS)

    role = forms.CharField(required=False)
    rank = forms.CharField(required=False)
    role_rank_confidence = forms.ChoiceField(required=False, choices=settings.CONFIDENCE_LEVELS)

    startcontext = forms.CharField(required=False)
    startcontext_confidence = forms.ChoiceField(required=False, choices=settings.CONFIDENCE_LEVELS)

    endcontext = forms.CharField(required=False)
    endcontext_confidence = forms.ChoiceField(required=False, choices=settings.CONFIDENCE_LEVELS)

    firstciteddate = ApproximateDateFormField(required=False)
    realstart = forms.BooleanField(required=False)
    firstciteddate_confidence = forms.ChoiceField(required=False, choices=settings.CONFIDENCE_LEVELS)

    lastciteddate = ApproximateDateFormField(required=False)
    realend = forms.BooleanField(required=False)
    lastciteddate_confidence = forms.ChoiceField(required=False, choices=settings.CONFIDENCE_LEVELS)
