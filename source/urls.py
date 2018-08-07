from django.conf.urls import url

from source.views import get_sources, SourceCreate, source_autocomplete, \
    SourceView, SourceUpdate, SourceRevertView, StashSourceView, \
    AccessPointUpdate, AccessPointCreate, AccessPointDetail, get_citation

urlpatterns = [
    url(r'^get/$', get_sources, name="get-sources"),
    url(r'^create/$', SourceCreate.as_view(), name="create-source"),
    url(r'^update/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', SourceUpdate.as_view(), name="update-source"),
    url(r'^update-access-point/(?P<source_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', AccessPointUpdate.as_view(), name="update-access-point"),
    url(r'^add-access-point/(?P<source_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', AccessPointCreate.as_view(), name="add-access-point"),
    url(r'^view-access-point/(?P<source_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', AccessPointDetail.as_view(), name="view-access-point"),
    url(r'^view/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', SourceView.as_view(), name="view-source"),
    url(r'^revert/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', SourceRevertView.as_view(), name="revert-source"),
    url(r'^autocomplete/$', source_autocomplete, name="source-autocomplete"),
    url(r'^stash/$', StashSourceView.as_view(), name="stash-source"),
    url(r'^get-citation/$', get_citation, name="get-citation"),
]
