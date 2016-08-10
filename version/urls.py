from django.conf.urls import url

from version.views import get_versions, revert_field

urlpatterns = [
    url(r'revert/' +
        '(?P<object_type>[a-zA-Z]+)/' +
        '(?P<object_id>[0-9]+)/' +
        '(?P<field_name>[a-zA-Z0-9]+)/',
        revert_field,
        name="revert_field"),
    url(r'(?P<object_type>[a-zA-Z]+)/' +
        '(?P<object_id>[0-9]+)/' +
        '(?P<field_name>[a-zA-Z0-9]+)/' +
        '(?P<lang>[a-zA-Z_]+)/',
        get_versions,
        name="get_versions_lang"),
    url(r'(?P<object_type>[a-zA-Z]+)/' +
        '(?P<object_id>[0-9]+)/' +
        '(?P<field_name>[a-zA-Z0-9]+)/',
        get_versions,
        name="get_versions"),
]
