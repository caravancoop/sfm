from django.conf.urls import patterns, url

from modal.views import SourceView, TranslationView

urlpatterns = patterns(
    '',
    url(r'source/(?P<object_type>[a-zA-Z]+)/' +
        '(?P<object_id>[0-9]+)/' +
        '(?P<field_name>[a-zA-Z]+)/',
        SourceView.as_view(),
        name="source_modal"),
)
