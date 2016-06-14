from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from .views import Dashboard, CreateSource, CreateOrgs, CreatePeople, \
    MembershipInfo, publications_autocomplete, organizations_autocomplete, \
    aliases_autocomplete, people_autocomplete, personalias_autocomplete
from organization.views import OrganizationCreate

urlpatterns = i18n_patterns(
    '',
    url(r'^composition/', include('composition.urls')),
    url(r'^organization/', include('organization.urls')),
    url(r'^membershipperson/', include('membershipperson.urls')),
    url(r'^person/', include('person.urls')),
    url(r'^modal/', include('modal.urls')),
    url(r'^translate/', include('translation.urls')),
    url(r'^version/', include('version.urls')),
    url(r'^source/', include('source.urls')),
    url(r'^create-source/', CreateSource.as_view(), name="create-source"),
    url(r'^create-orgs/', CreateOrgs.as_view(), name="create-orgs"),
    url(r'^create-people/', CreatePeople.as_view(), name="create-people"),
    url(r'^membership-info/', MembershipInfo.as_view(), name="membership-info"),
    url(r'^publications-autocomplete/', publications_autocomplete, name="publications-autocomplete"),
    url(r'^organizations-autocomplete/', organizations_autocomplete, name="organizations-autocomplete"),
    url(r'^aliases-autocomplete/', aliases_autocomplete, name="aliases-autocomplete"),
    url(r'^people-autocomplete/', people_autocomplete, name="people-autocomplete"),
    url(r'^personalias-autocomplete/', personalias_autocomplete, name="personalias-autocomplete"),
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
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', {'login_url': '/accounts/login'}),
)
