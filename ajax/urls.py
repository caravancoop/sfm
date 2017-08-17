# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from .views import test, chain

urlpatterns = [
    url(r'^person/(?P<artist_id>\d+)/test/',
        test, name='json_test'),
    url(r'^chain/(?P<org_id>[0-9a-f-]+)', chain, name='chain-of-command'),
]
