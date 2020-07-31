# -*- coding: utf-8 -*-
#
# Copyright 2020 BigML
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
"""Resources management functions

"""


import sys

import bigml.api

from bigmler.utils import (dated, get_url, log_message, check_resource,
                           check_resource_error, log_created_resources)

from bigmler.resourcesapi.common import set_basic_args, \
    update_attributes



def set_library_args(args, name=None):
    """Returns a library arguments dict

    """

    if name is None:
        name = args.name
    library_args = set_basic_args(args, name)
    if args.project_id is not None:
        library_args.update({"project": args.project_id})
    if args.imports is not None:
        library_args.update({"imports": args.imports_})
    update_attributes(library_args, args.json_args.get('library'))
    return library_args


def create_library(source_code, library_args, args, api=None, path=None,
                   session_file=None, log=None):
    """Creates remote library

    """
    if api is None:
        api = bigml.api.BigML()

    message = dated("Creating library \"%s\".\n" % library_args["name"])
    log_message(message, log_file=session_file, console=args.verbosity)
    library = api.create_library(source_code, library_args)
    log_created_resources("library", path,
                          bigml.api.get_library_id(library), mode='a')
    library_id = check_resource_error(library, "Failed to create library: ")
    try:
        library = check_resource(library, api.get_library, raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a compiled library: %s" % str(exception))
    message = dated("Library created: %s\n" % get_url(library))
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % library_id, log_file=log)
    return library
