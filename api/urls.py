from django.conf.urls import url

from api.views import CountryListView, CountryDetailView, CountryZipView, \
    CountryTxtView, CountryMapView, CountryEventsView, EventDetailView

urlpatterns = [
    url(r'^countries/$', CountryListView.as_view(), name="country-list"),
    url(r'^countries/(?P<id>\w+)/$', CountryDetailView.as_view(), name="country-detail"),
    url(r'^countries/(?P<id>\w+).zip$', CountryZipView.as_view(), name="country-zip"),
    url(r'^countries/(?P<id>\w+).txt$', CountryTxtView.as_view(), name="country-txt"),
    url(r'^countries/(?P<id>\w+)/map/$', CountryMapView.as_view(), name="country-map"),
    url(r'^countries/(?P<id>\w+)/events/$', CountryEventsView.as_view(), name="country-events"),
    url(r'^events/(?P<id>\S+)/$', EventDetailView.as_view(), name="event-detail"),
    
]
