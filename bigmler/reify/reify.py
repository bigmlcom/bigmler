# -*- coding: utf-8 -*-
#
# Copyright 2015-2016 BigML
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
import os
import stat

from bigml.resourcehandler import get_resource_id

from bigmler.utils import PYTHON3
from bigmler.reify.restchain import RESTChain


def reify_resources(args, api, logger):
    """ Extracts the properties of the created resources and generates
        code to rebuild them

    """

    resource_id = get_resource_id(args.resource_id)
    if resource_id is None:
        sys.exit("Failed to match a valid resource ID. Please, check: %s"
                 % args.resource_id)

    api_calls = RESTChain(api, resource_id, args.add_fields,
                          logger, args.output_dir)
    output = api_calls.reify(args.language)
    if PYTHON3:
        with open(args.output, "w", encoding="utf-8") as reify_file:
            reify_file.write(output)
    else:
        with open(args.output, "w") as reify_file:
            reify_file.write(output.encode("utf-8"))

    sts = os.stat(args.output)
    os.chmod(args.output, sts.st_mode | stat.S_IEXEC)
