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

"""BigMLer - External data connectors

"""


import sys

import bigmler.utils as u
import bigmler.processing.externalconnector as pec

from bigmler.defaults import DEFAULTS_FILE
from bigmler.command import get_context
from bigmler.dispatcher import SESSIONS_LOG, clear_log_files

COMMAND_LOG = ".bigmler_connector"
DIRS_LOG = ".bigmler_connector_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]

SETTINGS = {
    "command_log": COMMAND_LOG,
    "sessions_log": SESSIONS_LOG,
    "dirs_log": DIRS_LOG,
    "defaults_file": DEFAULTS_FILE}



def connector_dispatcher(args=sys.argv[1:]):
    """Parses command line and calls the different processing functions

    """

    command_args, _, api, session_file, _ = get_context(args, SETTINGS)

    path = u.check_dir(command_args.output)
    log = None
    if command_args.log_file:
        u.check_dir(command_args.log_file)
        log = command_args.log_file
        # If --clear_logs the log files are cleared
        clear_log_files([log])
    if not command_args.external_connector_id and \
            u.has_connection_info(command_args):
        # create connector
        pec.connector_processing(
            api, command_args, command_args.resume, session_file=session_file,
            path=path, log=log)
    if command_args.external_connector_id and (
            command_args.connector_attributes or
            command_args.name or command_args.tag or command_args.description
            or command_args.category):
        # update connector's attributes
        pec.update_external_connector(command_args, api, command_args.resume, \
            session_file=session_file)

    u.log_message("_" * 80 + "\n", log_file=session_file)
    u.print_generated_files(command_args.output_dir, log_file=session_file,
                            verbosity=command_args.verbosity)
