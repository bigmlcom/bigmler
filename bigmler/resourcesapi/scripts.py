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


def set_script_args(args, name=None):
    """Returns a script arguments dict

    """

    if name is None:
        name = args.name
    script_args = set_basic_args(args, name)
    if args.project_id is not None:
        script_args.update({"project": args.project_id})
    if args.imports is not None:
        script_args.update({"imports": args.imports_})
    if args.parameters_ is not None:
        script_args.update({"inputs": args.parameters_})
    if args.declare_outputs_:
        script_args.update({"outputs": args.declare_outputs_})
    update_attributes(script_args, args.json_args.get('script'))
    return script_args


def create_script(source_code, script_args, args, api=None, path=None,
                  session_file=None, log=None):
    """Creates remote script

    """

    if api is None:
        api = bigml.api.BigML()
    message = dated("Creating script \"%s\".\n" % script_args["name"])
    log_message(message, log_file=session_file, console=args.verbosity)
    script = api.create_script(source_code, script_args)
    log_created_resources("scripts", path,
                          bigml.api.get_script_id(script), mode='a')
    script_id = check_resource_error(script, "Failed to create script: ")
    try:
        script = check_resource(script, api.get_script, raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a compiled script: %s" % str(exception))
    message = dated("Script created: %s\n" % get_url(script))
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % script_id, log_file=log)
    return script


def get_script(script, api=None, verbosity=True,
               session_file=None):
    """Retrieves the script in its actual state

    """
    if api is None:
        api = bigml.api.BigML()
    if (isinstance(script, str) or
            bigml.api.get_status(script)['code'] != bigml.api.FINISHED):
        message = dated("Retrieving script. %s\n" %
                        get_url(script))
        log_message(message, log_file=session_file,
                    console=verbosity)
        try:
            script = check_resource(script, api.get_script,
                                    raise_on_error=True)
        except Exception as exception:
            sys.exit("Failed to get a compiled script: %s" % str(exception))
    return script
