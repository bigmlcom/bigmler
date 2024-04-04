# -*- coding: utf-8 -*-
#
# Copyright 2019-2024 BigML
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

"""BigMLer - cluster subcommand processing dispatching

"""


import sys
import os

import bigml.api

import bigmler.utils as u
import bigmler.processing.args as a
import bigmler.processing.sources as ps

from bigmler.defaults import DEFAULTS_FILE
from bigmler.command import get_context
from bigmler.dispatcher import SESSIONS_LOG, clear_log_files

COMMAND_LOG = ".bigmler_source"
DIRS_LOG = ".bigmler_source_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]
MINIMUM_MODEL = "full=false"

SETTINGS = {
    "command_log": COMMAND_LOG,
    "sessions_log": SESSIONS_LOG,
    "dirs_log": DIRS_LOG,
    "default_output": None,
    "defaults_file": DEFAULTS_FILE}


#pylint: disable=locally-disabled,dangerous-default-value
def source_dispatcher(args=sys.argv[1:]):
    """Parses command line and calls the different processing functions

    """

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        clear_log_files(LOG_FILES)

    command_args, _, api, session_file, resume = get_context(args,
                                                             SETTINGS)

    # Selects the action to perform
    if (a.has_train(command_args)
            or (hasattr(command_args, "sources") and
                command_args.sources is not None)
            or command_args.export_fields is not None):
        output_args = a.get_output_args(api, command_args, resume)
        compute_output(**output_args)
    u.log_message("_" * 80 + "\n", log_file=session_file)


def get_metadata(resource, key, default_value):
    """Retrieves from the user_metadata key in the resource the
       given key using default_value as a default

    """
    if ('object' in resource and 'user_metadata' in resource['object'] and
            key in resource['object']['user_metadata']):
        return resource['object']['user_metadata'][key]
    return default_value


def compute_output(api, args):
    """ Creates a dataset using the `training_set`.

    """


    source = None
    fields = None

    # variables from command-line options
    resume = args.resume_
    output = args.output

    path = u.check_dir(output)

    session_file = "%s%s%s" % (path, os.sep, SESSIONS_LOG)
    csv_properties = {}
    # If logging is required set the file for logging
    log = None
    if args.log_file:
        u.check_dir(args.log_file)
        log = args.log_file
        # If --clear_logs the log files are cleared
        clear_log_files([log])

    if args.source_file:
        # source is retrieved from the contents of the given local JSON file
        source, csv_properties, fields = u.read_local_resource(
            args.source_file,
            csv_properties=csv_properties)
    else:
        # source is retrieved from the remote object
        source, resume, csv_properties, fields = ps.source_processing(
            api, args, resume,
            csv_properties=csv_properties,
            session_file=session_file, path=path, log=log)
    if source is not None:
        args.source = bigml.api.get_source_id(source)
    if fields and args.export_fields:
        fields.summary_csv(os.path.join(path, args.export_fields))

    u.print_generated_files(path, log_file=session_file,
                            verbosity=args.verbosity)
