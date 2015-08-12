# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.db.models import Count
from django.utils import translation
from django.core.urlresolvers import reverse_lazy
from jsonview.decorators import json_view
from libs.bonsoundapi.client import ApiBonsoundClient
from pressclipping.models import SavedPressClippingSearch
from .utils import id_generator
from pressclipping.models import PressClipping
from project.models import Project
from event.models import Event
from django.db.models import Count, Sum, Max, Min
from django.utils.translation import ugettext as _
from django.core import serializers

@json_view
def test(self, person_id):
    test = []
    return test

