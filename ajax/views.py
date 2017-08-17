# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from jsonview.decorators import json_view

from sfm_pc.utils import chain_of_command

@json_view
def test(self, person_id):
    test = []
    return test

@json_view
def chain(self, org_id):
    return chain_of_command(org_id)
