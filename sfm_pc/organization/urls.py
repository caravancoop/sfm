from django.conf.urls import patterns, url

from .views import (OrganizationCreate, OrganizationView, OrganizationUpdate,
                    classification_autocomplete, organization_autocomplete,
                    organization_search)

urlpatterns = patterns(
    '',
    url(r'^$', OrganizationView.as_view(), name='organizations'),
    url(r'search/', organization_search, name='organization_search'),
    url(r'add/$', OrganizationCreate.as_view(), name="add_organization"),
    url(r'(?P<pk>\d+)/$', OrganizationUpdate.as_view(), name='edit_organization'),
    url(r'classification/autocomplete', classification_autocomplete,
        name="classification_autocomplete"),
    url(r'autocomplete', organization_autocomplete,
        name="organization_autocomplete"),
)
