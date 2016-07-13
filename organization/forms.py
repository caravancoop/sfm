from django import forms

from django_date_extensions.fields import ApproximateDateFormField
from django.utils.translation import ugettext as _

from organization.models import Classification

class OrganizationForm(forms.Form):
    name = forms.CharField(error_messages={'required': _('Name is required')})
    name_text = forms.CharField()
    classification = forms.ModelChoiceField(queryset=Classification.objects.all())
    alias = forms.CharField(required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.empty_permitted = False

class OrganizationGeographyForm(forms.Form):
    geography_type = forms.ChoiceField(choices=(('Site','Site'),('Area','Area'),), error_messages={'required': _('Geography type is required')})
    name = forms.CharField(error_messages={'required': _('Name is required')})
    geoname = forms.CharField(error_messages={'required': _('Geoname is required')})
    geoname_text = forms.CharField()
    startdate = ApproximateDateFormField(required=False)
    enddate = ApproximateDateFormField(required=False)
    org = forms.CharField()
    geotype = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.empty_permitted = False
