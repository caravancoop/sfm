from django.conf import settings
from django.urls import include, re_path
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import logout_then_login
from django.contrib.sitemaps import views as sitemap_views, Sitemap
from django.views.decorators.cache import cache_page
from django.urls import reverse, reverse_lazy

from organization.views import OrganizationSitemap
from person.views import PersonSitemap
from violation.views import ViolationSitemap

from sfm_pc.views import (Dashboard, osm_autocomplete, division_autocomplete,
                          command_chain, DownloadData, DumpChangeLog,
                          About, about_redirect)


class StaticViewSitemap(Sitemap):
    i18n = True
    protocol = 'http' if settings.DEBUG else 'https'

    def items(self):
        return ['dashboard', 'about', 'download']

    def location(self, item):
        return reverse(item)

sitemaps = {
    'organization': OrganizationSitemap,
    'person': PersonSitemap,
    'violation': ViolationSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    # sitemap
    re_path(r'^sitemap\.xml$', sitemap_views.index, {'sitemaps': sitemaps}),
    re_path(r'^sitemap-(?P<section>.+)\.xml$', sitemap_views.sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
]

urlpatterns += i18n_patterns(
    re_path(r'^organization/', include('organization.urls')),
    re_path(r'^person/', include('person.urls')),
    re_path(r'^source/', include('source.urls')),
    re_path(r'^violation/', include('violation.urls')),
    re_path(r'^location/', include('location.urls')),
    re_path(r'^countries/(?P<country>[a-zA-Z-]+)/background/$', about_redirect, name="background"),
    re_path(r'^countries/', about_redirect, name="countries"),
    re_path(r'^help/', about_redirect, name="help"),
    re_path(r'^about/', About.as_view(), name="about"),
    re_path(r'^search/', include('search.urls')),
    re_path(r'^download/', DownloadData.as_view(), name="download"),
    re_path(r'^changelog/', DumpChangeLog.as_view(), name="changelog"),

    re_path(r'^osm-autocomplete/$', osm_autocomplete, name="osm-autocomplete"),
    re_path(r'^division-autocomplete/$', division_autocomplete, name="division-autocomplete"),
    re_path(r'^command-chain/(?P<org_id>[0-9a-f-]+)/$', cache_page(60 * 60 * 24)(command_chain), name="command-chain"),
    re_path(r'^command-chain/(?P<org_id>[0-9a-f-]+)/(?P<when>[0-9-]+)/$', cache_page(60 * 60 * 24)(command_chain), name="command-chain-bounded"),

    # Dashboard
    re_path(r'^$', cache_page(60 * 60 * 24)(Dashboard.as_view()), name='dashboard'),

    # Admin panel
    re_path(r'^admin/', admin.site.urls),

    # Authentication
    re_path(r'^logout/$', logout_then_login, {'login_url': reverse_lazy('login')}, name="logout"),

    # API endpoints
    re_path(r'^api/', include('api.urls')),

    # auth
    re_path('^', include('django.contrib.auth.urls')),
)

# Rosetta translation app
if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += (
        re_path(r'^rosetta/', include('rosetta.urls')),
    )

# Django debug toolbar (for local development only)
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = i18n_patterns(
            # Django debug toolbar plugin
            re_path(r'^__debug__/', include(debug_toolbar.urls)),
        ) + urlpatterns
    except ImportError:
        pass

# Custom 500 error handler
handler500 = 'sfm_pc.views.server_error'
