from django.conf.urls import patterns, url

from modal.views import SourceView, VersionView, TranslationView

urlpatterns = patterns(
    '',
    url(r'source/(?P<object_type>[a-zA-Z]+)/' +
        '(?P<object_id>[0-9]+)/' +
        '(?P<field_name>[a-zA-Z]+)/',
        SourceView.as_view(),
        name="source_modal"),
    url(r'translate/(?P<object_type>[a-zA-Z]+)/' +
        '(?P<object_id>[0-9]+)/' +
        '(?P<field_name>[a-zA-Z]+)/',
        TranslationView.as_view(),
        name="translate_modal"),
    url(r'version/(?P<object_type>[a-zA-Z]+)/' +
        '(?P<object_id>[0-9]+)/' +
        '(?P<field_name>[a-zA-Z]+)/',
        VersionView.as_view(),
        name="version_modal"),
)
