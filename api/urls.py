from django.conf.urls import url

from api.views import EventDetailView, OSMAutoView, OrganizationMapView, \
    OrganizationChartView, OrganizationDetailView, PersonDetailView

from api.country_views import CountryListView, CountryDetailView, CountryZipView, \
    CountryTxtView, CountryMapView, CountryEventsView, CountryGeoJSONView, \
    CountryGeometryView 

from api.search_views import OrganizationSearchView, PeopleSearchView, \
    EventSearchView

urlpatterns = [
    url(r'^countries/$', CountryListView.as_view(), name="country-list"),
    url(r'^countries/(?P<id>\w+)/$', CountryDetailView.as_view(), name="country-detail"),
    url(r'^countries/(?P<id>\w+).zip$', CountryZipView.as_view(), name="country-zip"),
    url(r'^countries/(?P<id>\w+).txt$', CountryTxtView.as_view(), name="country-txt"),
    url(r'^countries/(?P<id>\w+)/map/$', CountryMapView.as_view(), name="country-map"),
    url(r'^countries/(?P<id>\w+)/events/$', CountryEventsView.as_view(), name="country-events"),
    url(r'^countries/(?P<id>\w+)/geometries/$', CountryGeometryView.as_view(), name="country-geometry"),
    url(r'^countries/(?P<id>\w+)/autocomplete/osm/$', OSMAutoView.as_view(), name="osm-auto"),
    url(r'^countries/(?P<id>\w+)/search/organizations/$', OrganizationSearchView.as_view(), name="organization-search"),
    url(r'^countries/(?P<id>\w+)/search/people/$', PeopleSearchView.as_view(), name="people-search"),
    url(r'^countries/(?P<id>\w+)/search/events/$', EventSearchView.as_view(), name="event-search"),
    
    url(r'^geometries/(?P<id>\S+).geojson', CountryGeoJSONView.as_view(), name='country-geojson'),
    
    url(r'^events/(?P<id>\S+)/$', EventDetailView.as_view(), name="event-detail"),
    
    url(r'^organizations/(?P<id>\S+)/map/$', OrganizationMapView.as_view(), name="organization-map"),
    url(r'^organizations/(?P<id>\S+)/chart/$', OrganizationChartView.as_view(), name="organization-chart"),
    url(r'^organizations/(?P<id>\S+)/$', OrganizationDetailView.as_view(), name="organization-detail"),
    
    url(r'^people/(?P<id>\S+)/$', PersonDetailView.as_view(), name="person-detail"),
]
