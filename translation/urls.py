from django.conf.urls import patterns, url

from translation.views import translate, autocomplete_language

urlpatterns = [
    url(r'(?P<object_type>[a-zA-Z]+)/' +
        '(?P<object_id>[0-9]+)/' +
        '(?P<field_name>[a-zA-Z]+)/',
        translate,
        name="translate_field"),
    url(r'languages/autocomplete/',
        autocomplete_language,
        name="translate_field"),
]
