from django.conf.urls import patterns, url

from version.views import get_versions, revert_field

urlpatterns = patterns(
    url(r'(?P<object_type>[a-zA-Z]+)/' +
        '(?P<object_id>[0-9]+)/' +
        '(?P<field_name>[a-zA-Z]+)/',
        get_versions,
        name="get_versions"),
    url(r'(?P<object_type>[a-zA-Z]+)/' +
        '(?P<object_id>[0-9]+)/' +
        '(?P<field_name>[a-zA-Z]+)/' +
        '(?P<lang>[a-zA-Z_]+)/',
        get_versions,
        name="get_versions_lang"),
    url(r'revert/' +
        '(?P<object_type>[a-zA-Z]+)/' +
        '(?P<object_id>[0-9]+)/' +
        '(?P<field_name>[a-zA-Z]+)/',
        revert_field,
        name="revert_field"),
)
