from django.urls import re_path

from source import views

urlpatterns = [
    re_path(r'^get/$', views.get_sources, name="get-sources"),
    re_path(r'^create/$', views.SourceCreate.as_view(), name="create-source"),
    re_path(r'^update/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.SourceUpdate.as_view(), name="update-source"),
    re_path(r'^update-access-point/(?P<source_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.AccessPointUpdate.as_view(), name="update-access-point"),
    re_path(r'^add-access-point/(?P<source_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.AccessPointCreate.as_view(), name="add-access-point"),
    re_path(r'^view-access-point/(?P<source_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.AccessPointDetail.as_view(), name="view-access-point"),
    re_path(r'^view/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.SourceView.as_view(), name="view-source"),
    re_path(r'^view/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<access_point_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.SourceEvidenceView.as_view(), name="view-source-with-evidence"),
    re_path(r'^delete/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.SourceDeleteView.as_view(), name="delete-source"),
    re_path(r'^delete/(?P<source_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.AccessPointDelete.as_view(), name="delete-access-point"),
    re_path(r'^revert/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.SourceRevertView.as_view(), name="revert-source"),
    re_path(r'^autocomplete/$', views.source_autocomplete, name="source-autocomplete"),
    re_path(r'^stash/$', views.StashSourceView.as_view(), name="stash-source"),
    re_path(r'^get-citation/$', views.get_citation, name="get-citation"),
    re_path(r'^publication/autocomplete/$', views.publication_autocomplete, name="publications-autocomplete"),
]
