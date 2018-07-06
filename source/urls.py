from django.conf.urls import url

from source.views import get_sources, SourceCreate, source_autocomplete, \
    publication_autocomplete, SourceView, SourceUpdate, SourceRevertView, \
    AccessPointUpdate, AccessPointCreate, AccessPointDetail

urlpatterns = [
    url(r'(?P<object_type>[a-zA-Z]+)/' +
        '(?P<object_id>[0-9]+)/' +
        '(?P<field_name>[a-zA-Z0-9]+)/',
        get_sources,
        name="get_sources"),
    url(r'^create/$', SourceCreate.as_view(), name="create-source"),
    url(r'^update/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', SourceUpdate.as_view(), name="update-source"),
    url(r'^update-access-point/(?P<source_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', AccessPointUpdate.as_view(), name="update-access-point"),
    url(r'^add-access-point/(?P<source_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', AccessPointCreate.as_view(), name="add-access-point"),
    url(r'^view-access-point/(?P<source_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', AccessPointDetail.as_view(), name="view-access-point"),
    url(r'^view/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', SourceView.as_view(), name="view-source"),
    url(r'^revert/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', SourceRevertView.as_view(), name="revert-source"),
    url(r'^publication/autocomplete/$', publication_autocomplete, name="publications-autocomplete"),
    url(r'^autocomplete/$', source_autocomplete, name="source-autocomplete"),
]
