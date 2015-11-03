from django.conf.urls import patterns, url

from .views import (EmplacementCreate, EmplacementUpdate, EmplacementView,
                    emplacement_search)

urlpatterns = patterns(
    '',
    url(r'add/$', EmplacementCreate.as_view(), name='add_emplacement'),
    url(r'search/', emplacement_search, name='emplacement_search'),
    url(r'(?P<pk>\d+)/$', EmplacementUpdate.as_view(), name='edit_emplacement'),
    url(r'^$', EmplacementView.as_view(), name='emplacement'),
)
