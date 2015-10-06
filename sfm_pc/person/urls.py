from django.conf.urls import patterns, url

from .views import (PersonView, PersonUpdate, PersonCreate, person_autocomplete,
                    person_search)

urlpatterns = patterns(
    '',
    url(r'add/$', PersonCreate.as_view(), name='add_person'),
    url(r'^$', PersonView.as_view(), name='person'),
    url(r'search/', person_search, name='person_search'),
    url(r'name/autocomplete/', person_autocomplete, name='person_autocomplete'),
    url(r'(?P<pk>\d+)/$', PersonUpdate.as_view(), name='edit_person'),
)
