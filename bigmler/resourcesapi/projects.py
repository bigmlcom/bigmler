# -*- coding: utf-8 -*-
#
# Copyright 2020 BigML
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
"""Resources management functions

"""


import sys

import bigml.api

from bigmler.utils import (dated, log_message, check_resource,
                           check_resource_error, log_created_resources)
from bigmler.reports import report

from bigmler.resourcesapi.common import set_basic_args, \
    update_json_args


def set_project_args(args, name=None):
    """Return project arguments dict

    """
    if name is None:
        name = args.name
    project_args = set_basic_args(args, name)
    if 'project' in args.json_args:
        update_json_args(project_args, args.json_args.get('project'), None)
    return project_args


def create_project(project_args, args, api=None,
                   session_file=None, path=None, log=None):
    """Creates remote project

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Creating project.\n")
    log_message(message, log_file=session_file, console=args.verbosity)
    project = api.create_project(project_args)
    log_created_resources("project", path,
                          bigml.api.get_project_id(project), mode='a')
    project_id = check_resource_error(project, "Failed to create project: ")
    try:
        project = check_resource(project, api=api, raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a finished project: %s" % str(exception))
    message = dated("Project \"%s\" has been created.\n" %
                    project['object']['name'])
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % project_id, log_file=log)
    try:
        if args.reports:
            report(args.reports, path, project)
    except AttributeError:
        pass
    return project


def update_project(project_args, args,
                   api=None, session_file=None, log=None):
    """Updates project properties

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Updating project attributes.\n")
    log_message(message, log_file=session_file,
                console=args.verbosity)
    project = api.update_project(args.project_id, project_args)
    check_resource_error(project, "Failed to update project: %s"
                         % project['resource'])
    message = dated("Project \"%s\" has been updated.\n" %
                    project['resource'])
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % args.project_id, log_file=log)
    return project


def get_project_by_name(project, api=None, verbosity=True, session_file=None):
    """Retrieves the project info by project name

    """
    if api is None:
        api = bigml.api.BigML()
    project_id = None

    if (isinstance(project, str) or
            bigml.api.get_status(project)['code'] != bigml.api.FINISHED):
        message = dated("Retrieving project info.\n")
        log_message(message, log_file=session_file,
                    console=verbosity)
        projects = api.list_projects(query_string="name=%s" % project)
        projects = projects.get('objects', [])
        if projects:
            project_id = projects[0]['resource']

    return project_id
