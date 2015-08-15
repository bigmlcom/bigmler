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

"""RESTCall class to store the REST API call definitions

"""

from __future__ import absolute_import

import sys


from bigml.resourcehandler import RESOURCE_RE, RENAMED_RESOURCES
from bigml.resourcehandler import get_resource_type

PREFIXES = {
    "python": "from bigml.api import BigML\napi = BigML()\n\n"
}


def get_method_suffix(resource_type):
    """Returns the suffix used in the REST method

    """
    if RESOURCE_RE.get(resource_type):
        return RENAMED_RESOURCES.get(resource_type, resource_type)
    else:
        sys.exit('Non allowed resource type. Check the provided resource ID')


class RESTCall():
    """Object to store the REST call definition

    """
    def __init__(self, action, origins=None, args=None, resource_id=None):
        """Constructor for the REST call definition

            resource_id: ID for the generated resource
            action: ["create" | "update"]
            origins: list of resouce IDs for the origin resources
            args: dict for the rest of arguments

        """
        self.action = action
        self.origins = [resource_id] if origins is None and \
                       action == "update" else origins
        self.args = args or {}
        self.resource_id = resource_id


    def reify(self, language=None, alias=None, out=sys.stdout):

        if not language:
            out.write("\n\n")
            out.write("resource ID: %s\n" % self.resource_id)
            out.write("action: %s\n" % self.action)
            out.write("origins: %s\n" % self.origins)
            out.write("args: %s\n" % self.args)
        else:
            try:
                reify_handler = getattr(self, "reify_%s" % language)
            except Exception:
                reify_handler = self.reify
            reify_handler(
                alias=alias, out=sys.stdout)

    def reify_python(self, alias=None, out=sys.stdout):

        def resource_alias(resource_id):
            return alias.get(resource_id, '"%s"' % resource_id)

        resource_type = get_resource_type(self.resource_id)
        resource_name = resource_alias(self.resource_id)
        origin_names = [resource_alias(resource_id) for resource_id
                        in self.origins]
        command = "%s = api.%s_%s(%s, %s)\napi.ok(%s)\n\n" % (
            resource_name,
            self.action,
            get_method_suffix(resource_type),
            ", ".join(origin_names),
            repr(self.args),
            resource_name)
        out.write(command)
