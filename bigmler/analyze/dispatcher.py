# -*- coding: utf-8 -*-
#
# Copyright 2012-2014 BigML
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

"""BigMLer analyze main processing

   Functions to process the analyze options


"""
from __future__ import absolute_import

import sys
import os

import bigmler.processing.args as a
import bigmler.utils as u

from bigml.multivote import PLURALITY

from bigmler.defaults import DEFAULTS_FILE
from bigmler.prediction import (MAX_MODELS, OTHER, COMBINATION,
                                THRESHOLD_CODE)
from bigmler.defaults import get_user_defaults
from bigmler.analyze.k_fold_cv import (create_kfold_cv,
                                       create_features_analysis,
                                       create_nodes_analysis)
from bigmler.utils import check_dir
from bigmler.dispatcher import (SESSIONS_LOG, command_handling)
from bigmler.command import Command, StoredCommand


COMMAND_LOG = ".bigmler_analyze"
DIRS_LOG = ".bigmler_analyze_dir_stack"
SESSIONS_LOG = "bigmler_sessions"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]


def analyze_dispatcher(args=sys.argv[1:]):
    """Main processing of the parsed options for BigMLer analyze

    """

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        clear_log_files(LOG_FILES)

    command = command_handling(args, COMMAND_LOG)

    # Parses command line arguments.
    command_args = command.parser.parse_args(command.args)
    resume = command_args.resume
    if resume:
        # Keep the debug option if set
        debug = command_args.debug
        # Restore the args of the call to resume from the command log file
        stored_command = StoredCommand(args, COMMAND_LOG, DIRS_LOG)
        command = Command(None, stored_command=stored_command)
        # Logs the issued command and the resumed command
        session_file = os.path.join(stored_command.output_dir, SESSIONS_LOG)
        stored_command.log_command(session_file=session_file)
        # Parses resumed arguments.
        command_args = command.parser.parse_args(command.args)
    else:
        if command_args.output_dir is None:
            command_args.output_dir = a.NOW
        session_file = os.path.join(command_args.output_dir,
                                    SESSIONS_LOG)
        csv_properties = {}
        # If logging is required, open the file for logging
        log = None
        if command_args.log_file:
            u.check_dir(command_args.log_file)
            log = command_args.log_file
            # If --clear_logs the log files are cleared
            if command_args.clear_logs:
                clear_log_files([log])

        if command_args.model_fields:
            model_fields = command_args.model_fields.split(',')
            command_args.model_fields_ = map(str.strip, model_fields)
        else:
            command_args.model_fields_ = {}
        with open(DIRS_LOG, "a", 0) as directory_log:
            directory_log.write("%s\n" %
                                os.path.abspath(command_args.output_dir))
        session_file = os.path.join(command_args.output_dir, SESSIONS_LOG)
    # create api instance form args
    api = a.get_api_instance(command_args,
                             u.check_dir(session_file))

    # k-fold cross-validation
    if (command_args.cv and command_args.dataset is not None):
        create_kfold_cv(command_args, api, command.common_options,
                        resume=resume)

    # features analysis
    if command_args.features:
        create_features_analysis(command_args, api, command.common_options,
                                 resume=resume)

    # node threshold analysis
    if command_args.nodes:
        create_nodes_analysis(command_args, api, command.common_options,
                              resume=resume)
