from django.conf.urls import url

from location.views import LocationView, LocationList, LocationCreate

urlpatterns = [
    url(r'^view/(?P<pk>\d+)$', LocationView.as_view(), name="view-location"),
    url(r'list/$', LocationList.as_view(), name='list-location'),
    url(r'create/$', LocationCreate.as_view(), name='create-location'),
]
