from django.conf.urls import patterns, url

from organization.views import OrganizationCreate, OrganizationUpdate, \
    organization_autocomplete, organization_csv, alias_autocomplete, \
    OrganizationCreateGeography, classification_autocomplete

urlpatterns = [
    url(r'^create/$', 
        OrganizationCreate.as_view(), 
        name="create-organization"),
    url(r'csv/', organization_csv, name='organization_csv'),
    url(r'(?P<pk>\d+)/$', OrganizationUpdate.as_view(), name='edit_organization'),
    url(r'name/autocomplete', 
        organization_autocomplete,
        name="organization-autocomplete"),
    url(r'^alias/autocomplete/$', alias_autocomplete, name="org-alias-autocomplete"),
    url(r'^classification/autocomplete/$', 
        classification_autocomplete, 
        name="org-classification-autocomplete"),
    url(r'^create/geography/$', OrganizationCreateGeography.as_view(), name="create-geography"),
]
