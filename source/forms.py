from django import forms
from django.utils.translation import ugettext as _


class SourceForm(forms.Form):
    title = forms.CharField(error_messages={'required': _('Title is required')})
    publication = forms.CharField(error_messages={'required': _('Publication is required')})
    published_on = forms.DateField(error_messages={'required': _('Date published is required')})
    source_url = forms.URLField(required=False)
    accessed_on = forms.DateField(required=False)
    page_number = forms.CharField(required=False)
