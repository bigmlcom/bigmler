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

"""BigMLer - Resources processing: creation, update and retrieval of scripts
             and executions

"""
from __future__ import absolute_import

import sys

import bigml.api
import bigmler.utils as u
import bigmler.resources as r
import bigmler.checkpoint as c
import bigmler.processing.projects as pp


def script_processing(api, args,
                      session_file=None, path=None, log=None):
    """Creating or retrieving a script

    """
    script = None
    resume = args.resume
    if args.code_file or args.code:
        # If resuming, try to extract args.script form log files

        if resume:
            message = u.dated("Script not found. Resuming.\n")
            resume, args.script = c.checkpoint(
                c.are_scripts_created, path, debug=args.debug, message=message,
                log_file=session_file, console=args.verbosity)
            script = args.script
        if not resume:
            args.resume = resume
            if args.code_file:
                try:
                    with open(args.code_file) as code_file:
                        source_code = code_file.read()
                except IOError:
                    sys.exit("Failed to find the source code file: %s" %
                             args.code_file)
            else:
                source_code = args.code
            # Check if there's a created project for it
            args.project_id = pp.project_processing(
                api, args, resume, session_file=session_file,
                path=path, log=log)
            script_args = r.set_script_args(args)
            script = r.create_script(source_code, script_args, args, api,
                                     path, session_file, log)
            args.script = script['resource']
        scripts = [script]

    # If a script is provided either through the command line or in resume
    # steps, we use it.
    elif args.script:
        script = bigml.api.get_script_id(args.script)
        scripts = [script]
    elif args.scripts:
        scripts = [script for script in args.script_ids]
        script = scripts[0]
    return script, scripts


def execution_processing(api, args,
                         session_file=None, path=None, log=None):
    """Creating or retrieving an execution

    """
    execution = None
    resume = args.resume
    if args.script or args.scripts:
        # If resuming, try to extract args.execution form log files

        if resume:
            message = u.dated("Execution not found. Resuming.\n")
            resume, args.execution = c.checkpoint(
                c.is_execution_created, path, debug=args.debug,
                message=message,
                log_file=session_file, console=args.verbosity)

        if not resume:
            args.resume = resume
            # Check if there's a created project for it
            args.project_id = pp.project_processing(
                api, args, resume, session_file=session_file, path=path,
                log=log)
            execution_args = r.set_execution_args(args)
            execution = r.create_execution(execution_args, args, api,
                                           path, session_file, log)

    # If a source is provided either through the command line or in resume
    # steps, we use it.
    elif args.execution:
        execution = bigml.api.get_execution_id(args.execution)

    return execution

def library_processing(api, args,
                       session_file=None, path=None, log=None):
    """Creating or retrieving a library

    """
    library = None
    resume = args.resume
    if args.code_file or args.code:
        # If resuming, try to extract args.library form log files

        if resume:
            message = u.dated("Library not found. Resuming.\n")
            resume, library = c.checkpoint(
                c.is_library_created, path, debug=args.debug, message=message,
                log_file=session_file, console=args.verbosity)

        if not resume:
            args.resume = resume
            if args.code_file:
                try:
                    with open(args.code_file) as code_file:
                        source_code = code_file.read()
                except IOError:
                    sys.exit("Failed to find the source code file: %s" %
                             args.code_file)
            else:
                source_code = args.code
            # Check if there's a created project for it
            args.project_id = pp.project_processing(
                api, args, resume, session_file=session_file,
                path=path, log=log)
            library_args = r.set_library_args(args)
            library = r.create_library(source_code, library_args, args, api,
                                       path, session_file, log)
    return library
