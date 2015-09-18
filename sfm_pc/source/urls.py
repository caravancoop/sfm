from django.conf.urls import patterns, url

from source.views import get_sources, get_confidences

urlpatterns = patterns(
    '',
    url(r'(?P<object_type>[a-zA-Z]+)/' +
        '(?P<object_id>[0-9]+)/' +
        '(?P<field_name>[a-zA-Z]+)/',
        get_sources,
        name="get_sources"),
    url(r'confidences/',
        get_confidences,
        name="get_confidences"),
)
