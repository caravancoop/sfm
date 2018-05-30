from django.conf.urls import url

from source.views import get_sources, SourceCreate, source_autocomplete, \
    publication_autocomplete, SourceView, SourceUpdate, SourceRevertView

urlpatterns = [
    url(r'(?P<object_type>[a-zA-Z]+)/' +
        '(?P<object_id>[0-9]+)/' +
        '(?P<field_name>[a-zA-Z0-9]+)/',
        get_sources,
        name="get_sources"),
    url(r'^create/$', SourceCreate.as_view(), name="create-source"),
    url(r'^update/(?P<pk>\d+)/$', SourceUpdate.as_view(), name="update-source"),
    url(r'^view/(?P<pk>\d+)/$', SourceView.as_view(), name="view-source"),
    url(r'^revert/(?P<pk>\d+)/$', SourceRevertView.as_view(), name="revert-source"),
    url(r'^publication/autocomplete/$', publication_autocomplete, name="publications-autocomplete"),
    url(r'^autocomplete/$', source_autocomplete, name="source-autocomplete"),
]
