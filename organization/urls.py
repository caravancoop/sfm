from django.conf.urls import url
from django.views.decorators.cache import cache_page

from organization.views import organization_autocomplete, OrganizationDetail, \
    OrganizationEditBasicsView, OrganizationEditCompositionView, \
    OrganizationEditPersonnelView, OrganizationEditEmplacementView, \
    OrganizationEditAssociationView, OrganizationCreateBasicsView, \
    OrganizationCreateCompositionView, OrganizationCreatePersonnelView, \
    OrganizationCreateEmplacementView, OrganizationCreateAssociationView, \
    OrganizationEditMembershipView, OrganizationCreateMembershipView, \
    OrganizationDeletePersonnelView, OrganizationDeleteCompositionView, \
    OrganizationDeleteMembershipView, OrganizationDeleteEmplacementView


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
    url(r'create/$',
        OrganizationCreateBasicsView.as_view(),
        name='create-organization'),

    url(r'edit/composition/(?P<organization_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>\d+)/$',
        OrganizationEditCompositionView.as_view(),
        name='edit-organization-composition'),
    url(r'create/composition/(?P<organization_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        OrganizationCreateCompositionView.as_view(),
        name='create-organization-composition'),
    url(r'delete/composition/(?P<organization_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>\d+)/$',
        OrganizationDeleteCompositionView.as_view(),
        name='delete-organization-composition'),

    url(r'edit/membership/(?P<organization_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>\d+)/$',
        OrganizationEditMembershipView.as_view(),
        name='edit-organization-membership'),
    url(r'create/membership/(?P<organization_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        OrganizationCreateMembershipView.as_view(),
        name='create-organization-membership'),
    url(r'delete/membership/(?P<organization_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>\d+)/$',
        OrganizationDeleteMembershipView.as_view(),
        name='delete-organization-membership'),

    url(r'edit/personnel/(?P<organization_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>\d+)/$',
        OrganizationEditPersonnelView.as_view(),
        name='edit-organization-personnel'),
    url(r'create/personnel/(?P<organization_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        OrganizationCreatePersonnelView.as_view(),
        name='create-organization-personnel'),
    url(r'delete/personnel/(?P<organization_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>\d+)/$',
        OrganizationDeletePersonnelView.as_view(),
        name='delete-organization-personnel'),

    url(r'edit/emplacement/(?P<organization_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>\d+)/$',
        OrganizationEditEmplacementView.as_view(),
        name='edit-organization-emplacement'),
    url(r'create/emplacement/(?P<organization_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        OrganizationCreateEmplacementView.as_view(),
        name='create-organization-emplacement'),
    url(r'delete/emplacement/(?P<organization_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>\d+)/$',
        OrganizationDeleteEmplacementView.as_view(),
        name='delete-organization-emplacement'),

    url(r'edit/association/(?P<organization_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>\d+)/$',
        OrganizationEditAssociationView.as_view(),
        name='edit-organization-association'),
    url(r'create/association/(?P<organization_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        OrganizationCreateAssociationView.as_view(),
        name='create-organization-association'),
]
