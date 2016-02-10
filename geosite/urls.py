from django.conf.urls import patterns, url

from .views import (SiteCreate, SiteUpdate, SiteView, site_search, site_autocomplete,
                    geosite_csv, GeositeDelete)

urlpatterns = patterns(
    '',
    url(r'add/$', SiteCreate.as_view(), name='add_site'),
    url(r'search/', site_search, name='site_search'),
    url(r'csv/', geosite_csv, name='geosite_csv'),
    url(r'delete/(?P<pk>\d+)/$',
        GeositeDelete.as_view(success_url="/geosite/"),
        name='delete_geosite'),
    url(r'(?P<pk>\d+)/$', SiteUpdate.as_view(), name='edit_site'),
    url(r'^$', SiteView.as_view(), name='site'),
    url(r'autocomplete', site_autocomplete,
        name="site_autocomplete"),
)
