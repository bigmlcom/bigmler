# -*- coding: utf-8 -*-
#
# Copyright 2015 BigML
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""BigMLer - reify processing dispatching

"""
from __future__ import absolute_import

import sys

from bigmler.reify.restchain import RESTChain
from bigml.resourcehandler import get_resource_id

def reify_resources(args, api):
    """ Extracts the properties of the created resources and generates
        code to rebuild them

    """

    resource_id = get_resource_id(args.resource_id)
    if resource_id is None:
        sys.exit("Failed to match a valid resource ID. Please, check: %s"
                 % args.resource_id)
    api_calls = RESTChain(api, resource_id)
    api_calls.reify("python")
