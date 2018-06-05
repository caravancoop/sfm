from django.conf.urls import url
from django.views.decorators.cache import cache_page

from person.views import PersonCreate, person_autocomplete, \
    alias_autocomplete, PersonUpdate, PersonDetail, PersonList

urlpatterns = [
    url(r'^create/$',
        PersonCreate.as_view(),
        name="create-person"),
    url(r'name/autocomplete/', person_autocomplete, name='person-autocomplete'),
    url(r'alias/autocomplete/', alias_autocomplete, name='person-alias-autocomplete'),
    url(r'update/(?P<pk>\d+)/$', PersonUpdate.as_view(), name='update-person'),
    url(r'view/(?P<pk>\d+)/$', cache_page(60 * 60 * 24)(PersonDetail.as_view()), name='view-person'),
    url(r'list/$', PersonList.as_view(), name='list-person'),
]
