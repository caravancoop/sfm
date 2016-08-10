from django.conf.urls import url

from modal.views import SourceView, TranslationView, VersionView

urlpatterns = [
    url(r'source/(?P<object_type>[a-zA-Z]+)/' +
        '(?P<object_id>[0-9]+)/' +
        '(?P<field_name>[a-zA-Z0-9]+)/' +
        '(?P<field_id>[0-9]+)/',
        SourceView.as_view(),
        name="source_modal"),
    url(r'source/(?P<object_type>[a-zA-Z]+)/' +
        '(?P<object_id>[0-9]+)/' +
        '(?P<field_name>[a-zA-Z0-9]+)/',
        SourceView.as_view(),
        name="source_modal"),
    url(r'translate/(?P<object_type>[a-zA-Z]+)/' +
        '(?P<object_id>[0-9]+)/' +
        '(?P<field_name>[a-zA-Z0-9]+)/' +
        '(?P<field_id>[0-9]+)/',
        TranslationView.as_view(),
        name="translate_modal"),
    url(r'translate/(?P<object_type>[a-zA-Z]+)/' +
        '(?P<object_id>[0-9]+)/' +
        '(?P<field_name>[a-zA-Z0-9]+)/',
        TranslationView.as_view(),
        name="translate_modal"),
    url(r'version/(?P<object_type>[a-zA-Z]+)/' +
        '(?P<object_id>[0-9]+)/' +
        '(?P<field_name>[a-zA-Z0-9]+)/' +
        '(?P<field_id>[0-9]+)/',
        VersionView.as_view(),
        name="translate_modal"),
    url(r'version/(?P<object_type>[a-zA-Z]+)/' +
        '(?P<object_id>[0-9]+)/' +
        '(?P<field_name>[a-zA-Z0-9]+)/',
        VersionView.as_view(),
        name="translate_modal"),
]
