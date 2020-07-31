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

"""BigMLer retrain main processing

   Functions to retrain a modeling resource


"""


import sys

import bigmler.utils as u


from bigmler.defaults import DEFAULTS_FILE
from bigmler.retrain.retrain import retrain_model
from bigmler.dispatcher import (SESSIONS_LOG,
                                clear_log_files)
from bigmler.command import get_context


COMMAND_LOG = ".bigmler_retrain"
DIRS_LOG = ".bigmler_retrain_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]

DEFAULT_OUTPUT = "retrain_script"

SETTINGS = {
    "command_log": COMMAND_LOG,
    "sessions_log": SESSIONS_LOG,
    "dirs_log": DIRS_LOG,
    "default_output": DEFAULT_OUTPUT,
    "defaults_file": DEFAULTS_FILE}


def check_compulsory_options(flags, args):
    """Checks whether the id or a unique tag are provided

    """
    return args.resource_id is not None or \
        len([flag for flag in flags if flag.endswith("-tag")]) > 0


def retrain_dispatcher(args=sys.argv[1:]):
    """Main processing of the parsed options for BigMLer retrain

    """

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        clear_log_files(LOG_FILES)

    # parses the command line to get the context args and the log files to use
    command_args, command, api, session_file, _ = get_context(args, SETTINGS)

    # --id or --model-tag, --ensemble-tag, etc. is compulsory
    if check_compulsory_options(command.flags, command_args):
        retrain_model(command_args, api, command,
                      session_file=session_file)
        u.log_message("_" * 80 + "\n", log_file=session_file)
    else:
        sys.exit("You must provide the ID of the resource to be"
                 " retrained in the --id option or a unique tag"
                 " to retrieve such ID."
                 " Type bigmler retrain --help\n"
                 " to see all the available options.")
