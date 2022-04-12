from django.urls import re_path

from api.views import EventDetailView, OSMAutoView, OrganizationMapView, \
    OrganizationChartView, OrganizationDetailView, PersonDetailView

from api.country_views import CountryListView, CountryDetailView, CountryZipView, \
    CountryTxtView, CountryMapView, CountryEventsView, CountryGeoJSONView, \
    CountryGeometryView

from api.search_views import OrganizationSearchView, PeopleSearchView, \
    EventSearchView

urlpatterns = [
    re_path(r'^countries/$', CountryListView.as_view(), name="country-list"),
    re_path(r'^countries/(?P<id>\w+)/$', CountryDetailView.as_view(), name="country-detail"),
    re_path(r'^countries/(?P<id>\w+).zip$', CountryZipView.as_view(), name="country-zip"),
    re_path(r'^countries/(?P<id>\w+).txt$', CountryTxtView.as_view(), name="country-txt"),
    re_path(r'^countries/(?P<id>\w+)/map/$', CountryMapView.as_view(), name="country-map"),
    re_path(r'^countries/(?P<id>\w+)/events/$', CountryEventsView.as_view(), name="country-events"),
    re_path(r'^countries/(?P<id>\w+)/geometries/$', CountryGeometryView.as_view(), name="country-geometry"),
    re_path(r'^countries/(?P<id>\w+)/autocomplete/osm/$', OSMAutoView.as_view(), name="osm-auto"),
    re_path(r'^countries/(?P<id>\w+)/search/organizations/$', OrganizationSearchView.as_view(), name="organization-search"),
    re_path(r'^countries/(?P<id>\w+)/search/people/$', PeopleSearchView.as_view(), name="people-search"),
    re_path(r'^countries/(?P<id>\w+)/search/events/$', EventSearchView.as_view(), name="event-search"),

    re_path(r'^geometries/(?P<id>\S+).geojson', CountryGeoJSONView.as_view(), name='country-geojson'),

    re_path(r'^events/(?P<id>\S+)/$', EventDetailView.as_view(), name="event-detail"),

    re_path(r'^organizations/(?P<id>\S+)/map/$', OrganizationMapView.as_view(), name="organization-map"),
    re_path(r'^organizations/(?P<id>\S+)/chart/$', OrganizationChartView.as_view(), name="organization-chart"),
    re_path(r'^organizations/(?P<id>\S+)/$', OrganizationDetailView.as_view(), name="organization-detail"),

    re_path(r'^people/(?P<id>\S+)/$', PersonDetailView.as_view(), name="person-detail"),
]
