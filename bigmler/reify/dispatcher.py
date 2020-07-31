# -*- coding: utf-8 -*-
#
# Copyright 2015-2020 BigML
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


import sys

import bigmler.utils as u

from bigmler.defaults import DEFAULTS_FILE
from bigmler.command import get_context
from bigmler.dispatcher import SESSIONS_LOG, clear_log_files
from bigmler.reify.reify import reify_resources

COMMAND_LOG = ".bigmler_reify"
DIRS_LOG = ".bigmler_reify_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]
DEFAULT_OUTPUT = "reify.py"

SETTINGS = {
    "command_log": COMMAND_LOG,
    "sessions_log": SESSIONS_LOG,
    "dirs_log": DIRS_LOG,
    "default_output": DEFAULT_OUTPUT,
    "defaults_file": DEFAULTS_FILE}


def reify_dispatcher(args=sys.argv[1:]):
    """Parses command line and calls the different processing functions

    """

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        clear_log_files(LOG_FILES)

    command_args, _, api, session_file, _ = get_context(args, SETTINGS)

    def logger(message):
        """Partial to log messages according to args.verbosity

        """
        u.log_message(u.dated(message), \
            log_file=session_file, console=command_args.verbosity)

    message = "Starting reification for %s\n\n" % command_args.resource_id
    u.log_message(message, \
        log_file=session_file, console=command_args.verbosity)
    reify_resources(command_args, api)
    message = "\nReification complete. See the results in %s\n\n" % \
        command_args.output
    u.log_message(message, \
        log_file=session_file, console=command_args.verbosity)
    u.log_message("_" * 80 + "\n", log_file=session_file)

    u.print_generated_files(command_args.output_dir, log_file=session_file,
                            verbosity=command_args.verbosity)
