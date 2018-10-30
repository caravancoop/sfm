from django.conf.urls import url
from django.views.decorators.cache import cache_page

from organization.views import organization_autocomplete, OrganizationDetail, \
    OrganizationEditBasicsView, OrganizationEditRelationshipsView, \
    OrganizationEditPersonnelView, OrganizationEditEmplacementView, \
    OrganizationEditAssociationView


urlpatterns = [
    url(r'^view/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        OrganizationDetail.as_view(),
        name="view-organization"),
    url(r'name/autocomplete',
        organization_autocomplete,
        name="organization-autocomplete"),
    url(r'edit/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        OrganizationEditBasicsView.as_view(),
        name='edit-organization'),
    url(r'edit/relationships/(?P<organization_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>\d+)/$', OrganizationEditRelationshipsView.as_view(), name='edit-organization-relationships'),
    url(r'edit/personnel/(?P<organization_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>\d+)/$', OrganizationEditPersonnelView.as_view(), name='edit-organization-personnel'),
    url(r'edit/emplacement/(?P<organization_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>\d+)/$', OrganizationEditEmplacementView.as_view(), name='edit-organization-emplacement'),
    url(r'edit/association/(?P<organization_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>\d+)/$', OrganizationEditAssociationView.as_view(), name='edit-organization-association'),
]
