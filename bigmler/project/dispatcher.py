# -*- coding: utf-8 -*-
#
# Copyright 2015-2016 BigML
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

"""BigMLer - project creation and update

"""
from __future__ import absolute_import

import sys
import os
import shutil

import bigmler.utils as u
import bigmler.processing.args as a
import bigmler.processing.projects as pp

from bigmler.defaults import DEFAULTS_FILE
from bigmler.command import get_stored_command
from bigmler.dispatcher import (SESSIONS_LOG, command_handling,
                                clear_log_files)

COMMAND_LOG = u".bigmler_project"
DIRS_LOG = u".bigmler_project_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]


def project_dispatcher(args=sys.argv[1:]):
    """Parses command line and calls the different processing functions

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
        directory = u.check_dir("%s/x.txt" % command_args.output_dir)
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


    path = u.check_dir("%s/x.txt" % command_args.output_dir)
    session_file = u"%s%s%s" % (path, os.sep, SESSIONS_LOG)
    # If logging is required set the file for logging
    log = None
    if command_args.log_file:
        u.check_dir(command_args.log_file)
        log = command_args.log_file
        # If --clear_logs the log files are cleared
        clear_log_files([log])


    # Creates the corresponding api instance
    api = a.get_api_instance(command_args, u.check_dir(session_file))
    a.get_output_args(api, command_args, command_args.resume)
    a.attribute_args(command_args)


    if not command_args.project_id and command_args.name:
        command_args.project = command_args.name
    if command_args.project:
        # create project
        pp.project_processing(
            api, command_args, command_args.resume, session_file=session_file,
            path=path, log=log, create=True)
    if command_args.project_id and (
            command_args.project_attributes or
            command_args.name or command_args.tag or command_args.description
            or command_args.category):
        # update project's attributes
        pp.update_project(command_args, api, command_args.resume, \
            session_file=session_file)

    u.log_message("_" * 80 + "\n", log_file=session_file)
    u.print_generated_files(command_args.output_dir, log_file=session_file,
                            verbosity=command_args.verbosity)
