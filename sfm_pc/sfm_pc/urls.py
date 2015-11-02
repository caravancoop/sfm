
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.core.urlresolvers import reverse_lazy
from django.contrib import admin
from .views import *
from person.views import *
# from field.views import *


urlpatterns = i18n_patterns(
    '',
    url(r'^composition/', include('composition.urls')),
    url(r'^organization/', include('organization.urls')),
    url(r'^membership/', include('membership.urls')),
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

    # Dashboard
    url(r'^$', Dashboard.as_view(), name='dashboard'),

    # Admin panel
    url(r'^admin/', include(admin.site.urls)),

    # Ajax calls
    url(r'^ajax/', include('ajax.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', {'login_url'\
        : '/login'}),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
