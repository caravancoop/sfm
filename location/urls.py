from django.urls import re_path

from location.views import LocationView, LocationList, LocationCreate, \
    LocationDelete, LocationAutoComplete

urlpatterns = [
    re_path(r'^delete/(?P<pk>-?\d+)$', LocationDelete.as_view(), name="delete-location"),
    re_path(r'^view/(?P<pk>-?\d+)$', LocationView.as_view(), name="view-location"),
    re_path(r'^create/$', LocationCreate.as_view(), name='create-location'),
    re_path(r'^autocomplete/$', LocationAutoComplete.as_view(), name='location-autocomplete'),
    re_path(r'^$', LocationList.as_view(), name='list-location'),
]
