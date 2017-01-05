# -*- coding: utf-8 -*-
#
# Copyright 2015-2017 BigML
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
from __future__ import absolute_import

import sys
import os
import shutil

import bigmler.utils as u
import bigmler.processing.args as a

from bigmler.defaults import DEFAULTS_FILE
from bigmler.command import get_stored_command
from bigmler.dispatcher import (SESSIONS_LOG, command_handling,
                                clear_log_files)
from bigmler.reify.reify import reify_resources

COMMAND_LOG = u".bigmler_reify"
DIRS_LOG = u".bigmler_reify_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]
DEFAULT_OUTPUT = "reify.py"


def reify_dispatcher(args=sys.argv[1:]):
    """Parses command line and calls the different processing functions

    """

    command = command_handling(args, COMMAND_LOG)

    # Parses command line arguments.
    command_args = a.parse_and_check(command)
    if command_args.resume:
        command_args, session_file, _ = get_stored_command(
            args, command_args.debug, command_log=COMMAND_LOG,
            dirs_log=DIRS_LOG, sessions_log=SESSIONS_LOG)
        if command_args.output is None:
            command_args.output = os.path.join(command_args.output_dir,
                                               DEFAULT_OUTPUT)
    else:
        if command_args.output_dir is None:
            command_args.output_dir = a.NOW
        if command_args.output is None:
            command_args.output = os.path.join(command_args.output_dir,
                                               DEFAULT_OUTPUT)
        if len(os.path.dirname(command_args.output).strip()) == 0:
            command_args.output = os.path.join(command_args.output_dir,
                                               command_args.output)
        directory = u.check_dir(command_args.output)
        command_args.output_dir = directory
        session_file = os.path.join(directory, SESSIONS_LOG)
        u.log_message(command.command + "\n", log_file=session_file)


        directory = u.check_dir(os.path.join(command_args.output_dir, "tmp"))
        session_file = os.path.join(directory, SESSIONS_LOG)
        u.log_message(command.command + "\n", log_file=session_file)
        try:
            shutil.copy(DEFAULTS_FILE, os.path.join(directory, DEFAULTS_FILE))
        except IOError:
            pass
        u.sys_log_message(u"%s\n" % os.path.abspath(directory),
                          log_file=DIRS_LOG)

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        clear_log_files(LOG_FILES)

    def logger(message):
        """Partial to log messages according to args.verbosity

        """
        u.log_message(u.dated(message), \
            log_file=session_file, console=command_args.verbosity)

    # Creates the corresponding api instance
    api = a.get_api_instance(command_args, u.check_dir(session_file))
    message = "Starting reification for %s\n\n" % command_args.resource_id
    u.log_message(message, \
        log_file=session_file, console=command_args.verbosity)
    reify_resources(command_args, api, logger)
    message = "\nReification complete. See the results in %s\n\n" % \
        command_args.output
    u.log_message(message, \
        log_file=session_file, console=command_args.verbosity)
    u.log_message("_" * 80 + "\n", log_file=session_file)

    u.print_generated_files(command_args.output_dir, log_file=session_file,
                            verbosity=command_args.verbosity)
