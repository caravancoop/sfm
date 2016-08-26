from django.conf.urls import url

from person.views import PersonCreate, person_autocomplete, \
    alias_autocomplete, PersonUpdate, PersonDetail, PersonList

urlpatterns = [
    url(r'^create/$', 
        PersonCreate.as_view(), 
        name="create-person"),
    url(r'name/autocomplete/', person_autocomplete, name='person-autocomplete'),
    url(r'alias/autocomplete/', alias_autocomplete, name='person-alias-autocomplete'),
    url(r'edit/(?P<pk>\d+)/$', PersonUpdate.as_view(), name='edit-person'),
    url(r'detail/(?P<pk>\d+)/$', PersonDetail.as_view(), name='detail-person'),
    url(r'list/$', PersonList.as_view(), name='list-person'),
]
