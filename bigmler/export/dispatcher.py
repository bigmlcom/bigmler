# -*- coding: utf-8 -*-
#
# Copyright 2017 BigML
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

"""BigMLer - generates code to use models locally

"""
from __future__ import absolute_import

import sys
import os
import shutil

import bigmler.processing.args as a
import bigmler.utils as u


from bigmler.defaults import DEFAULTS_FILE
from bigmler.command import get_stored_command
from bigmler.dispatcher import (SESSIONS_LOG, command_handling,
                                clear_log_files)
from bigmler.export.out_model.jsmodel import JsModel
from bigmler.export.out_model.pythonmodel import PythonModel
from bigmler.export.out_model.tableaumodel import TableauModel
from bigmler.export.out_model.mysqlmodel import MySQLModel
from bigmler.export.out_model.rmodel import RModel
from bigmler.export.out_model.pythonlr import PythonLR


COMMAND_LOG = u".bigmler_export"
DIRS_LOG = u".bigmler_export_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]

EXPORTS = {
    "javascript": JsModel,
    "python": PythonModel,
    "tableau": TableauModel,
    "mysql": MySQLModel,
    "r": RModel}

EXTENSIONS = {
    "javascript": "js",
    "python": "py",
    "tableau": "tb",
    "mysql": "sql",
    "r": "R"}

LR_EXPORTS   = {
    "python": PythonLR
}

SEPARATE_OUTPUT = ['tableau', 'mysql']


def export_dispatcher(args=sys.argv[1:]):
    """Parses command line and calls the different export functions

    """

    command = command_handling(args, COMMAND_LOG)

    # Parses command line arguments.
    command_args = a.parse_and_check(command)
    if command_args.resume:
        command_args, session_file, _ = get_stored_command(
            args, command_args.debug, command_log=COMMAND_LOG,
            dirs_log=DIRS_LOG, sessions_log=SESSIONS_LOG)
    else:
        if command_args.output_dir is None:
            command_args.output_dir = a.NOW
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

    # Creates the corresponding api instance
    api = a.get_api_instance(command_args, u.check_dir(session_file))
    message = "Generating %s code for %s\n\n" % (command_args.language,
                                                 command_args.model)
    u.log_message(message, \
        log_file=session_file, console=command_args.verbosity)
    export_code(command_args, api)
    u.log_message("_" * 80 + "\n", log_file=session_file)

    u.print_generated_files(command_args.output_dir, log_file=session_file,
                            verbosity=command_args.verbosity)


def generate_output(local_model, args, model_type="model", attr="confidence"):
    """Generates the output for the prediction (and confidence) function

    """
    with open(os.path.join(args.output_dir, \
        "%s.%s") % (getattr(args, model_type).replace("/", "_"),
                    EXTENSIONS[args.language]), "w") as handler:
        local_model.plug_in(out=handler)
    # creating a separate file to predict confidence
    if args.language in SEPARATE_OUTPUT:
        with open(os.path.join(args.output_dir, \
            "%s_confidence.%s") % (getattr(args, model_type).replace("/", "_"),
                        EXTENSIONS[args.language]), "w") as handler:
            local_model.plug_in(out=handler, attr=attr)


def export_code(args, api=None):
    """Generates the plugin code in the language required by the user

    """
    args.language = args.language or "javascript"

    if args.model is not None and args.language in EXPORTS:

        local_model = EXPORTS[args.language](args.model, api=api)
        generate_output(local_model, args, model_type="model")

    """
    if args.logistic_regression is not None:
        if args.language not in LR_EXPORTS:
            sys.exit("Exporting to %s is not yet supported for this kind of "
                     "models." % args.language)
        local_logistic = LR_EXPORTS[args.language]( \
            args.logistic_regression, api=api)
        generate_output(local_logistic, args, model_type="logistic_regression",
                        attr="probability")
    """
