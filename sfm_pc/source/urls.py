from django.conf.urls import patterns, url

from source.views import get_sources

urlpatterns = patterns(
    '',
    url(r'(?P<object_type>[a-zA-Z]+)/' +
        '(?P<object_id>[0-9]+)/' +
        '(?P<field_name>[a-zA-Z0-9]+)/',
        get_sources,
        name="get_sources"),
)
