from django.conf.urls import url

from location.views import LocationView, LocationList, LocationCreate, \
    LocationDelete

urlpatterns = [
    url(r'^delete/(?P<pk>\d+)$', LocationDelete.as_view(), name="delete-location"),
    url(r'^view/(?P<pk>\d+)$', LocationView.as_view(), name="view-location"),
    url(r'^create/$', LocationCreate.as_view(), name='create-location'),
    url(r'^$', LocationList.as_view(), name='list-location'),
]
