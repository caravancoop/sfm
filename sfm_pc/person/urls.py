# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url

from .views import PersonView, PersonCreate, PersonUpdate, PersonDelete, PpPersonCloseView, PpPersonCreate

urlpatterns = patterns('',
                       url(r'^$', PersonView.as_view(),
                           name='person'),



                       url(r'popup/add/$', PpPersonCreate.as_view(),
                           name='Pp_add_person'),
                       url(r'popup/(?P<pk>\d+)/close/$',
                           PpPersonCloseView.as_view(), name='Pp_close_person'),
                       url(r'(?P<pk>\d+)/$', PersonUpdate.as_view(),
                           name='edit_person'),
                       url(r'add/$', PersonCreate.as_view(),
                           name='add_person'),
                       url(r'(?P<pk>\d+)/delete/$',
                           PersonDelete.as_view(), name='delete_person'),
                       )
