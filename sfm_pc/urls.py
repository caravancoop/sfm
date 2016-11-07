from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import logout_then_login
from sfm_pc.views import Dashboard, osm_autocomplete, division_autocomplete, \
    search, SetConfidence, EntityMergeView

urlpatterns = i18n_patterns(
    url(r'^composition/', include('composition.urls')),
    url(r'^organization/', include('organization.urls')),
    url(r'^membershipperson/', include('membershipperson.urls')),
    url(r'^person/', include('person.urls')),
    url(r'^modal/', include('modal.urls')),
    url(r'^translate/', include('translation.urls')),
    url(r'^version/', include('version.urls')),
    url(r'^source/', include('source.urls')),
    url(r'^area/', include('area.urls')),
    url(r'^association/', include('association.urls')),
    url(r'^geosite/', include('geosite.urls')),
    url(r'^emplacement/', include('emplacement.urls')),
    url(r'^violation/', include('violation.urls')),
    url(r'^search/', search, name="search"),
    
    url(r'^osm-autocomplete/$', osm_autocomplete, name="osm-autocomplete"),
    url(r'^division-autocomplete/$', division_autocomplete, name="division-autocomplete"),
    
    url(r'^set-confidence/$', SetConfidence.as_view(), name='set-confidence'),
    # Dashboard
    url(r'^$', Dashboard.as_view(), name='dashboard'),
    
    # Merge entities
    url(r'^merge/$', EntityMergeView.as_view(), name='merge'),

    # Admin panel
    url(r'^admin/', include(admin.site.urls)),

    # Ajax calls
    url(r'^ajax/', include('ajax.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^logout/$', logout_then_login, {'login_url': '/accounts/login'}, name="logout"),
    
)

urlpatterns += (
    # API endpoints
    url(r'^api/', include('api.urls')),
)
