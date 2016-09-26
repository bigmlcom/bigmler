# -*- coding: utf-8 -*-
#
# Copyright 2015 BigML
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

"""BigMLer - execute processing dispatching

"""
from __future__ import absolute_import

import sys
import os
import shutil

import bigmler.utils as u
import bigmler.processing.args as a
import bigmler.processing.whizzml as pw
import bigmler.resources as r

from bigmler.defaults import DEFAULTS_FILE
from bigmler.command import get_stored_command
from bigmler.dispatcher import (SESSIONS_LOG, command_handling,
                                clear_log_files)

COMMAND_LOG = u".bigmler_execute"
DIRS_LOG = u".bigmler_execute_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]


def execute_dispatcher(args=sys.argv[1:]):
    """Parses command line and calls the different processing functions

    """

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        clear_log_files(LOG_FILES)

    command = command_handling(args, COMMAND_LOG)
    default_output = 'whizzml_results'
    # Parses command line arguments.
    command_args = a.parse_and_check(command)
    resume = command_args.resume
    if command_args.resume:
        command_args, session_file, output_dir = get_stored_command(
            args, command_args.debug, command_log=COMMAND_LOG,
            dirs_log=DIRS_LOG, sessions_log=SESSIONS_LOG)
        if command_args.output is None:
            command_args.output = os.path.join(output_dir,
                                               default_output)
    else:
        if command_args.output_dir is None:
            command_args.output_dir = a.NOW
        if command_args.output is None:
            command_args.output = os.path.join(command_args.output_dir,
                                               default_output)
        if len(os.path.dirname(command_args.output).strip()) == 0:
            command_args.output = os.path.join(command_args.output_dir,
                                               command_args.output)
        directory = u.check_dir(command_args.output)
        session_file = os.path.join(directory, SESSIONS_LOG)
        u.log_message(command.command + "\n", log_file=session_file)
        try:
            shutil.copy(DEFAULTS_FILE, os.path.join(directory, DEFAULTS_FILE))
        except IOError:
            pass
        u.sys_log_message(u"%s\n" % os.path.abspath(directory),
                          log_file=DIRS_LOG)

    # Creates the corresponding api instance
    api = a.get_api_instance(command_args, u.check_dir(session_file))
    _ = a.get_output_args(api, command_args, resume)
    a.transform_args(command_args, command.flags, api,
                     command.user_defaults)
    execute_whizzml(command_args, api, session_file)
    u.log_message("_" * 80 + "\n", log_file=session_file)


def execute_whizzml(args, api, session_file):
    """executes the code in a script or a source code file

    """

    # If logging is required set the file for logging
    log = None
    if args.log_file:
        u.check_dir(args.log_file)
        log = args.log_file
        # If --clear_logs the log files are cleared
        clear_log_files([log])
    path = args.output_dir
    if args.to_library:
        pw.library_processing( \
            api, args, session_file=session_file, path=path, log=log)
    else:
        if args.script_file:
            # script is retrieved from the contents of the given local file
            script, _, _ = u.read_local_resource(args.script_file)
            args.script = script['resource']
            args.script_ids = [args.script]
        elif args.code_file or args.code:
            script, scripts = pw.script_processing( \
                api, args, session_file=session_file, path=path, log=log)
            args.script = script['resource']
            args.script_ids = scripts


        if (args.script or args.scripts) and not args.no_execute:
            execution = pw.execution_processing( \
                api, args, session_file=session_file, path=path, log=log)
            execution = r.get_execution( \
                execution, api, args.verbosity, session_file)
            r.save_txt_and_json(execution['object']['execution'],
                                args.output, api=api)
            args.execution = execution['resource']

    u.log_message("_" * 80 + "\n", log_file=session_file)
    u.print_generated_files(args.output_dir, log_file=session_file,
                            verbosity=args.verbosity)
