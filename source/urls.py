from django.conf.urls import url

from source import views

urlpatterns = [
    url(r'^get/$', views.get_sources, name="get-sources"),
    url(r'^create/$', views.SourceCreate.as_view(), name="create-source"),
    url(r'^update/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.SourceUpdate.as_view(), name="update-source"),
    url(r'^update-access-point/(?P<source_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.AccessPointUpdate.as_view(), name="update-access-point"),
    url(r'^add-access-point/(?P<source_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.AccessPointCreate.as_view(), name="add-access-point"),
    url(r'^view-access-point/(?P<source_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.AccessPointDetail.as_view(), name="view-access-point"),
    url(r'^view/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.SourceView.as_view(), name="view-source"),
    url(r'^view/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<access_point_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.SourceEvidenceView.as_view(), name="view-source-with-evidence"),
    url(r'^delete/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.SourceDeleteView.as_view(), name="delete-source"),
    url(r'^delete/(?P<source_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.AccessPointDelete.as_view(), name="delete-access-point"),
    url(r'^revert/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.SourceRevertView.as_view(), name="revert-source"),
    url(r'^autocomplete/$', views.source_autocomplete, name="source-autocomplete"),
    url(r'^stash/$', views.StashSourceView.as_view(), name="stash-source"),
    url(r'^get-citation/$', views.get_citation, name="get-citation"),
    url(r'^publication/autocomplete/$', views.publication_autocomplete, name="publications-autocomplete"),
]
