from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import logout_then_login
from django.views.decorators.cache import cache_page

from sfm_pc.views import (Dashboard, osm_autocomplete, division_autocomplete,
                          Countries, command_chain,
                          download_zip, Help, About, country_background)

urlpatterns = i18n_patterns(
    url(r'^organization/', include('organization.urls')),
    url(r'^person/', include('person.urls')),
    url(r'^source/', include('source.urls')),
    url(r'^violation/', include('violation.urls')),
    url(r'^location/', include('location.urls')),
    url(r'^countries/(?P<country>[a-zA-Z-]+)/background/$', country_background, name="background"),
    url(r'^countries/', Countries.as_view(), name="countries"),
    url(r'^help/', Help.as_view(), name="help"),
    url(r'^about/', About.as_view(), name="about"),
    url(r'^search/', include('search.urls')),

    url(r'^osm-autocomplete/$', osm_autocomplete, name="osm-autocomplete"),
    url(r'^division-autocomplete/$', division_autocomplete, name="division-autocomplete"),
    url(r'^command-chain/(?P<org_id>[0-9a-f-]+)/$', cache_page(60 * 60 * 24)(command_chain), name="command-chain"),
    url(r'^command-chain/(?P<org_id>[0-9a-f-]+)/(?P<when>[0-9-]+)/$', cache_page(60 * 60 * 24)(command_chain), name="command-chain-bounded"),

    # Dashboard
    url(r'^$', Dashboard.as_view(), name='dashboard'),

    # Admin panel
    url(r'^admin/', include(admin.site.urls)),

    # Downloads
    url(r'^download/', cache_page(60 * 60 * 24)(download_zip), name='download'),

    # Authentication
    url(r'^logout/$', logout_then_login, {'login_url': '/accounts/login'}, name="logout"),

    # API endpoints
    url(r'^api/', include('api.urls')),

)

# Rosetta translation app
if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += (
        url(r'^rosetta/', include('rosetta.urls')),
    )

# Django debug toolbar (for local development only)
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = i18n_patterns(
            # Django debug toolbar plugin
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ) + urlpatterns
    except ImportError:
        pass
