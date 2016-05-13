from django.conf.urls import patterns, url

from source.views import get_sources, CreateSource, publications_autocomplete

urlpatterns = patterns(
    '',
    url(r'^create-source/', CreateSource.as_view(), name="create-source"),
    url(r'^publications-autocomplete/', publications_autocomplete, name="publications-autocomplete"),
    url(r'(?P<object_type>[a-zA-Z]+)/' +
        '(?P<object_id>[0-9]+)/' +
        '(?P<field_name>[a-zA-Z0-9]+)/',
        get_sources,
        name="get_sources"),
)
