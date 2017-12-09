# -*- coding: utf-8 -*-
#
# Copyright 2017 BigML
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

"""BigMLer retrain models


"""

import os
import sys
import json

import bigmler.resources as r
import bigmler.processing.args as a

from bigmler.whizzml.dispatcher import whizzml_dispatcher
from bigmler.execute.dispatcher import execute_whizzml
from bigmler.execute.dispatcher import SETTINGS as EXE_SETTINGS
from bigmler.dispatcher import SETTINGS as MAIN_SETTINGS, compute_output
from bigmler.utils import get_last_resource
from bigmler.reports import BIGMLER_SCRIPT
from bigmler.command import get_context


INCREMENTAL_PACKAGE_PATH = os.path.join(BIGMLER_SCRIPT, "static", "scripts",
                                        "incremental")
INCREMENTAL_RETRAIN_PATH = os.path.join(INCREMENTAL_PACKAGE_PATH, "retrain",
                                        "script")


def get_script_id(path):
    """Returns the script id stored in the file in path

    """
    try:
        with open(path) as file_handler:
            return file_handler.read().strip()
    except IOError:
        return None


def extract_retrain_id(args, api, session_file):
    """Extracting the id of the script that has to be used to retrain
    the modeling resource.

    """
    execution = r.get_execution(args.execution, api=api,
                                verbosity=args.verbosity,
                                session_file=session_file)
    return execution['object']['execution']['result']


def retrain_model(args, api, common_options, session_file=None):
    """Retrieve or create the retrain script for a model and
    execute it with the new provided data

    """

    resource_id = args.resource_id
    # check for the last script used to retrain the model
    query_string = "tags__in=retrain:%s" % resource_id
    script_id = get_last_resource( \
        "script",
        api=api,
        query_string=query_string)

    if script_id is None:
        # if the script to retrain does not exist,
        # look for the script that creates it.
        reify_script = get_script_id(INCREMENTAL_RETRAIN_PATH)
        if reify_script is None:
            # new bigmler command: creating the scriptify scripts
            whizzml_command = ['whizzml',
                               '--package-dir', INCREMENTAL_PACKAGE_PATH,
                               '--output-dir', args.output_dir]
            whizzml_dispatcher(args=whizzml_command)
            reify_script = get_script_id(args.output_dir)

        # new bigmler command: creating the retrain script
        execute_command = ['execute',
                           '--script', reify_script]
        command_args, _, _, exe_session_file, _ = get_context(execute_command,
                                                              EXE_SETTINGS)
        command_args.arguments_ = [["model-resource", resource_id]]
        command_args.inputs = json.dumps(command_args.arguments_)
        # process the command
        execute_whizzml(command_args, api, session_file)
        script_id = extract_retrain_id(command_args, api, session_file)

    # apply the retrain script to the new data:
    # create a source with the new data
    if args.add:
        source_command = ["main", "--train", args.add, "--no-dataset"]
        command_args, _, _, main_session_file, _ = get_context(source_command,
                                                               MAIN_SETTINGS)
        command_args.predictions = command_args.output
        a.get_output_args(api, command_args, False)
        compute_output(api, command_args)
        source_id = command_args.source
        # apply the retrain script to the new source
        execute_command = ['execute',
                           '--script', script_id]
        command_args, _, _, exe_session_file, _ = get_context(execute_command,
                                                              EXE_SETTINGS)
        command_args.arguments_ = [["source1", source_id]]
        command_args.inputs = json.dumps(command_args.arguments_)
        # process the command
        execute_whizzml(command_args, api, session_file)
        with open("%s.json" % command_args.output) as file_handler:
            print "New Model: ", json.load(file_handler)['result']
