# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from .views import test

urlpatterns = [
    url(r'^person/(?P<artist_id>\d+)/test/',
        test, name='json_test'),
]
