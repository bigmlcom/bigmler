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

"""RESTCall class to store the REST API call definitions

"""

from __future__ import absolute_import

import pprint

from bigml.constants import RENAMED_RESOURCES
from bigml.resourcehandler import get_resource_type

INDENT = 4 * " "


def sort_lists(dict_structure):
    """Sorts the lists in a dict_structure

    """
    if dict_structure is not None and isinstance(dict_structure, dict):
        for key, value in dict_structure.items():
            if value is not None:
                if isinstance(value, list):
                    dict_structure[key] = sorted(value)
                elif isinstance(value, dict):
                    sort_lists(dict_structure[key])
    return dict_structure


class RESTCall(object):
    """Object to store the REST call definition

    """
    def __init__(self, action, origins=None, args=None,
                 resource_id=None, resource_type=None, suffix=None):
        """Constructor for the REST call definition

            resource_id: ID for the generated resource
            action: ["create" | "update" | "get"]
            origins: list of resouce IDs for the origin resources
            args: dict for the rest of arguments

        """
        self.action = action
        self.origins = [resource_id] if origins is None and \
                       action == "update" else origins
        self.args = args or {}
        input_data = self.args.get("input_data")
        if input_data:
            del self.args["input_data"]
        self.input_data = input_data
        self.resource_id = resource_id
        self.resource_type = resource_type
        self.suffix = suffix


    def reify(self, language=None, alias=None):
        """REST call command line

            language: computing language to write the output in
            alias: list of aliases for the related resources (e.g
                    {"source/55c4de8d1fa89c2dc70012d0": "source1"}
                    will cause the references to
                    "source/55c4de8d1fa89c2dc70012d0" to be renamed
                    as "source1")
        """
        out = ""
        if not language:
            out += "\n\n"
            out += "resource ID: %s\n" % self.resource_id
            out += "action: %s\n" % self.action
            out += "origins: %s\n" % self.origins
            out += "args: %s\n" % self.args
            out += "input data: %s\n" % self.input_data
            return out
        else:
            try:
                reify_handler = getattr(self, "reify_%s" % language)
            except AttributeError:
                reify_handler = self.reify
            return reify_handler(
                alias=alias)

    def reify_python(self, alias=None):
        """REST call command line in python. See ``reify`` method.

        """

        def resource_alias(resource_id):
            """Returns the alias if found

            """
            if isinstance(resource_id, basestring):
                return alias.get(resource_id, '"%s"' % resource_id)
            elif isinstance(resource_id, list):
                alias_names = []
                for resource_id_id in resource_id:
                    alias_names.append(
                        alias.get(resource_id_id, '"%s"' % resource_id_id))
                return repr(alias_names)

        resource_type = get_resource_type(self.resource_id)
        resource_name = resource_alias(self.resource_id)
        resource_method_suffix = RENAMED_RESOURCES.get(
            resource_type, resource_type)
        origin_names = [resource_alias(resource_id) for resource_id
                        in self.origins]

        arguments = ", ".join(origin_names)
        if self.suffix:
            arguments = "%s%s" % (arguments, self.suffix)
        if self.input_data:
            arguments = "%s, \\\n%s%s" % ( \
                arguments, INDENT,
                pprint.pformat(self.input_data).replace("\n", "\n%s" % INDENT))
        if self.args:
            sort_lists(self.args)
            arguments = "%s, \\\n%s%s" % (arguments, \
                INDENT, \
                pprint.pformat(self.args).replace( \
                    "\n", "\n%s" % INDENT))
        out = "%s = api.%s_%s(%s)\napi.ok(%s)\n\n" % (
            resource_name,
            self.action,
            resource_method_suffix,
            arguments,
            resource_name)
        return out
