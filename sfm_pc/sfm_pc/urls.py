from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.core.urlresolvers import reverse_lazy
from django.contrib import admin
from .views import *
from person.views import *


urlpatterns = patterns('',
                       (r'^localeurl/', include('localeurl.urls')),

                       url(r'^person/', include('person.urls')),
                       # Authentification & account settings
                       url(r'^login/$', 'django.contrib.auth.views.login', {'template_name'\
                                                                            : 'account/login.html'}, name='auth_login'),

                       url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', {'login_url'\
                                                                                         : '/login'}),

                       # Admin panel
                       url(r'^admin/', include(admin.site.urls)),



                       # Ajax calls
                       url(r'^ajax/', include('ajax.urls')),
                       # Dashboard
                       url(r'^$', Dashboard.as_view(),
                           name='dashboard'),
                       ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
