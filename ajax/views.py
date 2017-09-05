# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from jsonview.decorators import json_view

from sfm_pc.utils import chain_of_command, get_org_hierarchy_by_id

@json_view
def test(self, person_id):
    test = []
    return test

@json_view
def chain(self, org_id):
    # Get edge list
    node_list = get_org_hierarchy_by_id(org_id)
    return node_list

    # Get nodes
    # edge_list = get_command_edges(org.uuid)
    # context['edge_list'] = json.dumps(edge_list)
    # return chain_of_command(org_id)
