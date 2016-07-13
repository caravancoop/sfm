from django.conf.urls import patterns, url

from source.views import get_sources, SourceCreate, source_autocomplete, \
    publication_autocomplete, view_source

urlpatterns = [
    url(r'(?P<object_type>[a-zA-Z]+)/' +
        '(?P<object_id>[0-9]+)/' +
        '(?P<field_name>[a-zA-Z0-9]+)/',
        get_sources,
        name="get_sources"),
    url(r'^create/$', SourceCreate.as_view(), name="create-source"),
    url(r'^view/(?P<source_id>\d+)/$', view_source, name="view-source"),
    url(r'^publication/autocomplete/$', publication_autocomplete, name="publications-autocomplete"),
    url(r'^autocomplete/$', source_autocomplete, name="source-autocomplete"),
]
