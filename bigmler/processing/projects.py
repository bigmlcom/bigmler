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

"""BigMLer - Resource processing: creation, update and retrieval of projects

"""
from __future__ import absolute_import

import bigml.api
import bigmler.resources as r
import bigmler.utils as u
import bigmler.checkpoint as c


def project_processing(api, args, resume,
                       session_file=None, path=None, log=None, create=False):
    """Creating or retrieving a project from input arguments

    """
    # if no project info given by the user, we skip project processing and no
    # project will be assigned
    if args.project is None and args.project_id is None:
        return None
    project_id = None
    if args.project:
        # If resuming, try to extract args.project_id form log files

        if resume:
            message = u.dated("Project not found. Resuming.\n")
            resume, project_id = c.checkpoint(
                c.is_project_created, path, debug=args.debug, message=message,
                log_file=session_file, console=args.verbosity)
        elif not create:
            project_id = r.get_project_by_name(
                args.project, api=api, verbosity=args.verbosity,
                session_file=session_file)
    elif args.project_id:
        project_id = bigml.api.get_project_id(args.project_id)

    # If no project is found by that name, we create a new one.
    if project_id is None:
        project_args = r.set_project_args(args, name=args.project)
        project = r.create_project(
            project_args, args, api, session_file, path, log)
        project_id = project['resource']

    return project_id

def update_project(args, api, resume,
                   session_file=None, path=None, log=None):
    """Updating project attributes according to input arguments

    """
    # if no project info given by the user, we skip project processing and no
    # project will be assigned
    if args.project_id is None:
        return None
        # If resuming, try to extract args.project_id form log files

    if resume:
        message = u.dated("Project not found. Resuming.\n")
        resume, project_id = c.checkpoint(
            c.is_project_created, path, debug=args.debug, message=message,
            log_file=session_file, console=args.verbosity)
    elif args.project_id:
        project_id = bigml.api.get_project_id(args.project_id)

    if project_id is not None:
        project_args = r.set_project_args(args, name=args.project)
        project = r.update_project(
            project_args, args, api, session_file, log)
        project_id = project['resource']

    return project_id
