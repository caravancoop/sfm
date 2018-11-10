from django import forms

from django.conf import settings
from django_date_extensions.fields import ApproximateDateFormField
from django.utils.translation import ugettext as _

from sfm_pc.forms import BaseUpdateForm, BaseCreateForm

from person.models import Person
from organization.models import Organization

from location.models import Location

from .models import Violation, ViolationStartDate, ViolationEndDate, \
    ViolationType, ViolationPerpetrator, ViolationPerpetratorOrganization, \
    ViolationPerpetratorClassification, ViolationDescription, ViolationDivisionId, \
    ViolationLocationDescription, ViolationAdminLevel1, ViolationAdminLevel2, \
    ViolationLocation

class ViolationBasicsForm(BaseUpdateForm):
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

    startdate = ApproximateDateFormField(label=_("Start date"), required=False)
    enddate = ApproximateDateFormField(label=_("End date"), required=False)
    types = forms.ModelMultipleChoiceField(label=_("Violation type"), queryset=ViolationType.objects.all())
    description = forms.CharField(label=_("Description"))
    perpetrator = forms.ModelMultipleChoiceField(label=_("Perpetrator"), queryset=Person.objects.all(), required=False)
    perpetratororganization = forms.ModelMultipleChoiceField(label=_("Perpetrator unit"), queryset=Organization.objects.all(), required=False)
    perpetratorclassification = forms.ModelChoiceField(label=_("Perpetrator classification"), queryset=ViolationPerpetratorClassification.objects.all(), required=False)
    division_id = forms.CharField(label=_("Country"), required=False)


class ViolationCreateBasicsForm(BaseCreateForm, ViolationBasicsForm):
    pass


class ViolationLocationsForm(BaseUpdateForm):
    class Meta:
        model = Violation
        fields = '__all__'

    edit_fields = [
        ('locationdescription', ViolationLocationDescription, False),
        ('adminlevel1', ViolationAdminLevel1, False),
        ('adminlevel2', ViolationAdminLevel2, False),
        ('location', ViolationDescription, False),
    ]

    locationdescription = forms.CharField(label=_("Location Description"))
    adminlevel1 = forms.ModelMultipleChoiceField(label=_("Settlement"), queryset=Location.objects.all(), required=False)
    adminlevel2 = forms.ModelMultipleChoiceField(label=_("Top administrative area"), queryset=Location.objects.all(), required=False)
    location = forms.ModelMultipleChoiceField(label=_("Exact Location"), queryset=Location.objects.all(), required=False)
