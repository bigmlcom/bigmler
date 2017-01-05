# -*- coding: utf-8 -*-
#
# Copyright 2014-2017 BigML
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

from bigmler.analyze.k_fold_cv import (create_kfold_cv,
                                       create_features_analysis,
                                       create_nodes_analysis,
                                       create_candidates_analysis)
from bigmler.dispatcher import (SESSIONS_LOG, command_handling,
                                clear_log_files)
from bigmler.command import get_stored_command


COMMAND_LOG = u".bigmler_analyze"
DIRS_LOG = u".bigmler_analyze_dir_stack"
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
        command_args, session_file, _ = get_stored_command(
            args, command_args.debug, command_log=COMMAND_LOG,
            dirs_log=DIRS_LOG, sessions_log=SESSIONS_LOG)
    else:
        if command_args.output_dir is None:
            command_args.output_dir = a.NOW
        session_file = os.path.join(command_args.output_dir,
                                    SESSIONS_LOG)
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
            command_args.model_fields_ = [model_field.strip()
                                          for model_field in model_fields]
        else:
            command_args.model_fields_ = {}
        u.sys_log_message(u"%s\n" % os.path.abspath(command_args.output_dir),
                          log_file=DIRS_LOG)
        session_file = os.path.join(command_args.output_dir, SESSIONS_LOG)
    # create api instance form args
    api = a.get_api_instance(command_args,
                             u.check_dir(session_file))

    # Creates the corresponding api instance
    api = a.get_api_instance(command_args, u.check_dir(session_file))
    a.transform_dataset_options(command_args, api)

    # --maximize flag will be deprecated. Use --optimize flag.
    if command_args.maximize is not None and command_args.optimize is None:
        command_args.optimize = command_args.maximize
    incompatible_flags = [command_args.cv, command_args.features,
                          command_args.nodes, command_args.random_fields]
    if sum([int(bool(flag)) for flag in incompatible_flags]) > 1:
        sys.exit("The following flags cannot be used together:\n    --features"
                 "\n    --cross-validation\n    --nodes\n    --random-fields")
    if (command_args.dataset is None and command_args.datasets is None and
            command_args.dataset_file is None):
        sys.exit("The analyze command needs an existing dataset ID. Please, "
                 "use the --dataset flag.")
    if not any(incompatible_flags):
        sys.exit("You need to specify the type of analysis: features, node "
                 "threshold, cross validation or random fields.")
    # k-fold cross-validation
    if command_args.cv and command_args.dataset is not None:
        create_kfold_cv(command_args, api, command.common_options,
                        resume=resume)

    # features analysis
    elif command_args.features:
        create_features_analysis(command_args, api, command.common_options,
                                 resume=resume)

    # node threshold analysis
    elif command_args.nodes:
        create_nodes_analysis(command_args, api, command.common_options,
                              resume=resume)

    # random fields analysis
    elif command_args.random_fields:
        create_candidates_analysis(command_args, api, command.common_options,
                                   resume=resume)
    else:
        sys.exit("You must choose one of the available analysis: --features,"
                 " --nodes, --random-fields or --cross-validation. Add"
                 " your prefered option to"
                 " the command line or type\n    bigmler analyze --help\n"
                 " to see all the available options.")
