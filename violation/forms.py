from django import forms

from django.conf import settings
from django_date_extensions.fields import ApproximateDateFormField

from sfm_pc.forms import BaseEditForm

from person.models import Person
from organization.models import Organization

from .models import Violation, ViolationStartDate, ViolationEndDate, \
    ViolationType, ViolationPerpetrator, ViolationPerpetratorOrganization, \
    ViolationPerpetratorClassification, ViolationDescription, ViolationDivisionId

class ViolationBasicsForm(BaseEditForm):
    class Meta:
        model = Violation
        fields = '__all__'

    edit_fields = [
        ('startdate', ViolationStartDate, False),
        ('enddate', ViolationEndDate, False),
        ('types', ViolationType, True),
        ('description', ViolationDescription, False),
        ('perpetrator', ViolationPerpetrator, True),
        ('perpetratororganization', ViolationPerpetratorOrganization, True),
        ('perpetratorclassification', ViolationPerpetratorClassification, False),
        ('division_id', ViolationDivisionId, False),
    ]

    startdate = ApproximateDateFormField(required=False)
    enddate = ApproximateDateFormField(required=False)
    types = forms.ModelMultipleChoiceField(queryset=ViolationType.objects.all())
    description = forms.CharField()
    perpetrator = forms.ModelMultipleChoiceField(queryset=Person.objects.all(), required=False)
    perpetratororganization = forms.ModelMultipleChoiceField(queryset=Organization.objects.all(), required=False)
    perpetratorclassification = forms.ModelChoiceField(queryset=ViolationPerpetratorClassification.objects.all(), required=False)
    division_id = forms.CharField(required=False)
