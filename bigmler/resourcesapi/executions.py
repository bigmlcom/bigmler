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


def set_execution_args(args, name=None):
    """Returns an execution arguments dict

    """

    if name is None:
        name = args.name
    execution_args = set_basic_args(args, name)
    if args.project_id is not None:
        execution_args.update({"project": args.project_id})
    if args.arguments_:
        execution_args.update({"inputs": args.arguments_})
    if args.creation_defaults is not None:
        execution_args.update({"creation_defaults": args.creation_defaults_})
    if args.outputs_:
        execution_args.update({"outputs": args.outputs_})
    if args.input_maps_:
        execution_args.update({"input_maps_": args.input_maps_})
    update_attributes(execution_args, args.json_args.get('execution'))
    return execution_args


def create_execution(execution_args, args, api=None, path=None,
                     session_file=None, log=None):
    """Creates remote execution

    """
    message = dated("Creating execution.\n")
    log_message(message, log_file=session_file, console=args.verbosity)
    scripts = args.script_ids if args.script_ids else args.script
    execution = api.create_execution(scripts, execution_args)
    log_created_resources("execution", path,
                          bigml.api.get_execution_id(execution), mode='a')
    execution_id = check_resource_error(execution,
                                        "Failed to create execution: ")
    try:
        execution = check_resource(execution, api.get_execution,
                                   raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a finished execution: %s" % str(exception))
    message = dated("Execution created: %s\n" % get_url(execution))
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % execution_id, log_file=log)
    return execution


def get_execution(execution, api=None, verbosity=True,
                  session_file=None):
    """Retrieves the execution in its actual state

    """
    if api is None:
        api = bigml.api.BigML()

    if (isinstance(execution, str) or
            bigml.api.get_status(execution)['code'] != bigml.api.FINISHED):
        message = dated("Retrieving execution. %s\n" %
                        get_url(execution))
        log_message(message, log_file=session_file,
                    console=verbosity)
        try:
            execution = check_resource(execution, api.get_execution,
                                       raise_on_error=True)
        except Exception as exception:
            sys.exit("Failed to get a finished execution: %s" % str(exception))
    return execution
