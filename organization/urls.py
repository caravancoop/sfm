from django.conf.urls import url
from django.views.decorators.cache import cache_page

from organization.views import OrganizationCreate, OrganizationUpdate, \
    organization_autocomplete, alias_autocomplete, \
    OrganizationCreateGeography, classification_autocomplete, OrganizationDetail, \
    OrganizationList

urlpatterns = [
    url(r'^create/$',
        OrganizationCreate.as_view(),
        name="create-organization"),
    url(r'edit/(?P<pk>\d+)/$', OrganizationUpdate.as_view(), name='edit_organization'),
    url(r'detail/(?P<pk>\d+)/$', cache_page(60 * 60 * 24)(OrganizationDetail.as_view()), name='detail_organization'),
    url(r'list/$', OrganizationList.as_view(), name='list-organization'),
    url(r'name/autocomplete',
        organization_autocomplete,
        name="organization-autocomplete"),
    url(r'^alias/autocomplete/$', alias_autocomplete, name="org-alias-autocomplete"),
    url(r'^classification/autocomplete/$',
        classification_autocomplete,
        name="org-classification-autocomplete"),
    url(r'^create/geography/$', OrganizationCreateGeography.as_view(), name="create-geography"),
]
