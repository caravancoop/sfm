from django.conf.urls import patterns, url

from .views import (OrganizationCreate, OrganizationView, OrganizationUpdate,
                    classification_autocomplete)

urlpatterns = patterns(
    '',
    url(r'^$', OrganizationView.as_view(), name='organizations'),
    url(r'add/$', OrganizationCreate.as_view(), name="add_organization"),
    url(r'(?P<pk>\d+)/$', OrganizationUpdate.as_view(), name='edit_organization'),

    url(r'classification/autocomplete', classification_autocomplete,
        name="classification_autocomplete")
)
