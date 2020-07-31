# -*- coding: utf-8 -*-
#
# Copyright 2017-2020 BigML
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
import shutil

from bigml.api import get_resource_type

import bigml.api
import bigmler.resourcesapi.executions as r
import bigmler.processing.args as a


from bigmler.whizzml.dispatcher import whizzml_dispatcher
from bigmler.execute.dispatcher import execute_whizzml
from bigmler.execute.dispatcher import SETTINGS as EXE_SETTINGS
from bigmler.dispatcher import SETTINGS as MAIN_SETTINGS, compute_output
from bigmler.utils import get_last_resource, get_first_resource, \
    log_message, last_resource_url, get_script_id, add_api_context
from bigmler.reports import BIGMLER_SCRIPT, HOME
from bigmler.command import get_context


INCREMENTAL_PACKAGE_PATH = os.path.join(BIGMLER_SCRIPT, "static", "scripts",
                                        "incremental")
BIGMLER_SCRIPTS_DIRECTORY = os.path.join(HOME, "bigmler", "scripts")

UPGRADE_FILE = os.path.join(INCREMENTAL_PACKAGE_PATH, ".upgrade_version.json")


MODEL_TYPES = ["model", "ensemble", "logistic_regression", "deepnet",
               "cluster", "anomaly", "association", "topic_model",
               "time_series"]


STOP_WORKFLOW = {"source-id": "--no-dataset",
                 "dataset-id": "--no-model"}




def extract_retrain_id(args, api, session_file):
    """Extracting the id of the script that has to be used to retrain
    the modeling resource.

    """
    execution = r.get_execution(args.execution, api=api,
                                verbosity=args.verbosity,
                                session_file=session_file)
    return execution['object']['execution']['result']


def create_input(args, api, input_type, script_id, command):
    """ Creates the resources used as input for the retrain script when adding
        new data.
        When remote sources are used, the input is usually the remote url.
        If a local source is used, then the input should be a source-id
        or a dataset-id

    """
    if input_type in ['source-id', 'dataset-id']:

        source_command = ["main", "--train", args.add,
                          "--output-dir", args.output_dir,
                          STOP_WORKFLOW[input_type]]
        command.propagate(source_command)
        command_args, _, _, _, _ = get_context( \
            source_command, MAIN_SETTINGS)
        command_args.predictions = command_args.output
        a.get_output_args(api, command_args, False)
        compute_output(api, command_args)
        resource_type = input_type[:-3]
        resource_id = getattr(command_args, resource_type)
    else:
        resource_type = "source-url"
        resource_id = args.add
    # apply the retrain script to the new resource
    execute_command = ['execute',
                       '--script', script_id,
                       '--output-dir', args.output_dir]
    command.propagate(execute_command)
    command_args, _, _, exe_session_file, _ = get_context( \
        execute_command, EXE_SETTINGS)
    command_args.arguments_ = [["%s1" % resource_type, resource_id],
                               ["datasets-limit", args.window_size]]
    command_args.inputs = json.dumps(command_args.arguments_)

    return command_args, api, exe_session_file


def retrain_model(args, api, command, session_file=None):
    """Retrieve or create the retrain script for a model and
    execute it with the new provided data

    """

    retrain_file = os.path.join(BIGMLER_SCRIPTS_DIRECTORY,
                                "retrain",
                                "scripts")
    try:
        os.remove(UPGRADE_FILE)
        reify_script = None
        try:
            shutil.rmtree(BIGMLER_SCRIPTS_DIRECTORY)
        except OSError:
            pass
    except OSError:
        # look for the script that creates the rebuild script.
        reify_script = get_script_id(retrain_file)

    if reify_script is None:
        # new bigmler command: creating the scriptify scripts
        whizzml_command = ['whizzml',
                           '--package-dir', INCREMENTAL_PACKAGE_PATH,
                           '--output-dir', BIGMLER_SCRIPTS_DIRECTORY]
        add_api_context(whizzml_command, args)
        whizzml_dispatcher(args=whizzml_command)
        reify_script = get_script_id(retrain_file)

    # retrieve the modeling resource to be retrained by tag or id
    if args.resource_id:
        resource_id = args.resource_id
        reference_tag = "retrain:%s" % resource_id
    else:
        for model_type in MODEL_TYPES:
            if hasattr(args, "%s_tag" % model_type) and \
                    getattr(args, "%s_tag" % model_type) is not None:
                tag = getattr(args, "%s_tag" % model_type)
                query_string = "tags=%s" % tag
                resource_id = get_first_resource( \
                    model_type.replace("_", ""),
                    api=api,
                    query_string=query_string)
                if resource_id is None:
                    sys.exit("Failed to find the %s with tag %s. "
                             "Please, check the tag and"
                             " the connection info (domain and credentials)." %
                             (model_type.replace("_", " "), tag))
                reference_tag = tag
                break
    # updating the dataset that generated the model with the reference tag
    model = api.getters[get_resource_type(resource_id)](resource_id)
    dataset_id = model["object"]["dataset"]
    dataset = api.get_dataset(dataset_id)
    tags = dataset["object"]["tags"]
    if reference_tag not in tags:
        tags.append(reference_tag)
        api.update_dataset(dataset_id, {"tags": tags})

    # if --upgrade, we force rebuilding the scriptified script
    if args.upgrade:
        script_id = None
    else:
        # check for the last script used to retrain the model
        query_string = "tags=%s" % reference_tag
        script_id = get_last_resource( \
            "script",
            api=api,
            query_string=query_string)

    if script_id is None:
        # if the script to retrain does not exist:

        # check whether the model exists
        try:
            bigml.api.check_resource(resource_id, raise_on_error=True, api=api)
        except Exception:
            sys.exit("Failed to find the model %s. Please, check its ID and"
                     " the connection info (domain and credentials)." %
                     resource_id)

        # new bigmler command: creating the retrain script
        execute_command = ['execute',
                           '--script', reify_script,
                           '--tag', reference_tag,
                           '--output-dir', args.output_dir]
        command.propagate(execute_command)
        command_args, _, _, exe_session_file, _ = get_context(execute_command,
                                                              EXE_SETTINGS)
        command_args.arguments_ = [["model-resource", resource_id]]
        command_args.inputs = json.dumps(command_args.arguments_)

        # process the command
        execute_whizzml(command_args, api, session_file)
        script_id = extract_retrain_id(command_args, api, session_file)

    # apply the retrain script to the new data:
    # add new data: depending on the script we will need to use
    # a source-url, a source or a dataset
    if args.add:
        script_inputs = api.get_script(script_id)['object']['inputs']
        input_type = script_inputs[0]['type']
        command_args, api, exe_session_file = \
            create_input(args, api, input_type, script_id, command)

        # process the command
        execute_whizzml(command_args, api, exe_session_file)

        with open("%s.json" % command_args.output) as file_handler:
            model_resource_id = json.load(file_handler)['result']
            message = ('The new retrained model is: %s.\n'
                       'You can use the\n\n%s\n\nquery to retrieve the latest'
                       ' retrained model.\n\n') % \
                (model_resource_id, last_resource_url( \
                resource_id, api, \
                "limit=1;full=yes;tags=%s" % reference_tag))
            log_message(message, log_file=session_file, console=1)
