from django import forms
from django.utils.translation import ugettext as _

from django_date_extensions.fields import ApproximateDateFormField

from composition.models import Classification
from organization.models import Organization

class CompositionForm(forms.Form):
    related_organization = forms.ModelChoiceField(queryset=Organization.objects.all())
    relationship_type = forms.ChoiceField(choices=(('parent', 'Parent',), ('child', 'Child',)))
    classification = forms.ModelChoiceField(queryset=Classification.objects.all())
    startdate = ApproximateDateFormField(required=False)
    enddate = ApproximateDateFormField(required=False)
    
