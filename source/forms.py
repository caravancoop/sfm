from django import forms
from django.utils.translation import gettext as _


class SourceForm(forms.Form):
    title = forms.CharField(error_messages={'required': _('Title is required')})
    publication = forms.CharField(error_messages={'required': _('Publication is required')})
    published_date = forms.DateField(error_messages={'required': _('Date published is required')})
    source_url = forms.URLField(required=False)
    accessed_on = forms.DateField(required=False)
    trigger = forms.CharField(required=False)
