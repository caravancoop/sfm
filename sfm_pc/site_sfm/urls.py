from django.conf.urls import patterns, url

from .views import SiteCreate, SiteUpdate, SiteView, site_autocomplete

urlpatterns = patterns(
    '',
    url(r'add/$', SiteCreate.as_view(), name='add_site'),
    url(r'(?P<pk>\d+)/$', SiteUpdate.as_view(), name='edit_site'),
    url(r'^$', SiteView.as_view(), name='site'),
    url(r'autocomplete', site_autocomplete,
        name="site_autocomplete"),
)
