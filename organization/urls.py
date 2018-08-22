from django.conf.urls import url
from django.views.decorators.cache import cache_page

from organization.views import organization_autocomplete, alias_autocomplete, \
    classification_autocomplete, OrganizationDetail, \
    OrganizationEditBasicsView, OrganizationEditRelationshipsView


urlpatterns = [
    url(r'^view/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        OrganizationDetail.as_view(),
        name="view-organization"),
    url(r'name/autocomplete',
        organization_autocomplete,
        name="organization-autocomplete"),
    url(r'^alias/autocomplete/$', alias_autocomplete, name="org-alias-autocomplete"),
    url(r'^classification/autocomplete/$',
        classification_autocomplete,
        name="org-classification-autocomplete"),
    url(r'edit/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        OrganizationEditBasicsView.as_view(),
        name='edit-organization'),
    url(r'edit/relationships/(?P<organization_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>\d+)/$', OrganizationEditRelationshipsView.as_view(), name='edit-organization-relationships'),
]
