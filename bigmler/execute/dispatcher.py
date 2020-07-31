# -*- coding: utf-8 -*-
#
# Copyright 2015-2018 BigML
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


import sys

import bigmler.utils as u
import bigmler.processing.whizzml as pw
import bigmler.resourcesapi.common as r

from bigmler.resourcesapi.executions import get_execution
from bigmler.defaults import DEFAULTS_FILE
from bigmler.command import get_context
from bigmler.dispatcher import SESSIONS_LOG, clear_log_files

COMMAND_LOG = ".bigmler_execute"
DIRS_LOG = ".bigmler_execute_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]

DEFAULT_OUTPUT = 'whizzml_results'

SETTINGS = {
    "command_log": COMMAND_LOG,
    "sessions_log": SESSIONS_LOG,
    "dirs_log": DIRS_LOG,
    "default_output": DEFAULT_OUTPUT,
    "defaults_file": DEFAULTS_FILE}


def execute_dispatcher(args=sys.argv[1:]):
    """Parses command line and calls the different processing functions

    """

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        clear_log_files(LOG_FILES)

    command_args, _, api, session_file, _ = get_context(args, SETTINGS)

    # process the command
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
            args.script = script if isinstance(script, str) else \
                script.get('resource')
            args.script_ids = scripts

        if (args.script or args.scripts) and not args.no_execute:
            execution = pw.execution_processing( \
                api, args, session_file=session_file, path=path, log=log)
            execution = get_execution( \
                execution, api, args.verbosity, session_file)
            r.save_txt_and_json(execution['object']['execution'],
                                args.output, api=api)
            args.execution = execution['resource']

    u.log_message("_" * 80 + "\n", log_file=session_file)
    u.print_generated_files(args.output_dir, log_file=session_file,
                            verbosity=args.verbosity)
