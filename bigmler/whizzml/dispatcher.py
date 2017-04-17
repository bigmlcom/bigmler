# -*- coding: utf-8 -*-
#
# Copyright 2016-2017 BigML
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

"""BigMLer whizzml main processing

   Functions to process the whizzml options


"""
from __future__ import absolute_import

import sys
import os

import bigmler.processing.args as a
import bigmler.utils as u

from bigmler.whizzml.package import create_package
from bigmler.dispatcher import (SESSIONS_LOG, command_handling,
                                clear_log_files)
from bigmler.command import get_stored_command


COMMAND_LOG = u".bigmler_whizzml"
DIRS_LOG = u".bigmler_whizzml_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]


def whizzml_dispatcher(args=sys.argv[1:]):
    """Main processing of the parsed options for BigMLer whizzml

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

        u.sys_log_message(u"%s\n" % os.path.abspath(command_args.output_dir),
                          log_file=DIRS_LOG)
        session_file = os.path.join(command_args.output_dir, SESSIONS_LOG)
    # create api instance form args
    api = a.get_api_instance(command_args,
                             u.check_dir(session_file))

    # Creates the corresponding api instance
    api = a.get_api_instance(command_args, u.check_dir(session_file))
    a.transform_dataset_options(command_args, api)


    # package_dir
    if command_args.package_dir is not None:
        command_args.package_dir = os.path.expanduser(command_args.package_dir)
        create_package(command_args, api, command.common_options,
                       resume=resume)
    else:
        sys.exit("You must use the --package-dir flag pointing to the"
                 " directory where the metadata.json file is. Type\n"
                 "    bigmler whizzml --help\n"
                 " to see all the available options.")
