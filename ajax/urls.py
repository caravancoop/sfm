# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url

from .views import test

urlpatterns = [
    url(r'^person/(?P<artist_id>\d+)/test/',
        test, name='json_test'),
]
