# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2014-2024 BigML
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



import os

from bigml.api import check_resource, BigML

from bigmler.tests.common_steps import base_shell_execute
from bigmler.tests.world import world, res_filename, ok_, eq_


def i_create_source_with_project(
    step, data=None, project=None, output_dir=None):
    """Step: I create a BigML source uploading train <data> file and associate
    it to a new project named <project> storing results in <output_dir>
    """
    ok_(data is not None)
    #Check if the project already exists
    previous_projects = world.api.list_projects('name=%s' % project)
    while previous_projects['meta']['total_count'] > 0:
        print("the project %s already exists, trying with:" % project)
        project += " " + project
        print(project)
        previous_projects = world.api.list_projects('name=%s' % project)
    command = ("bigmler --train " + res_filename(data) +
               " --no-model --no-dataset --store --output-dir " +
               output_dir +
               " --project=\"" + project + "\"")
    base_shell_execute(command, output_dir)


def i_create_project_in_org(
    step, name=None, output_dir=None, organization=None):
    """Step: I create a BigML project in an organization named <name> storing
    results in <output>
    """
    ok_(name is not None and organization is not None)
    command = ("bigmler project --name \"" + name +
               "\" --organization " + organization +
               " --output-dir " + output_dir)
    base_shell_execute(command, output_dir)


def i_create_source_with_org_project(step, data=None, output_dir=None):
    """Step: I create a BigML source uploading train <data> file and associate
    it to the last created project id storing results in <output_dir>
    """
    ok_(data is not None)
    command = ("bigmler --train " + res_filename(data) +
               " --no-model --no-dataset --store --output-dir " +
               output_dir +
               " --org-project " + world.project["resource"])
    base_shell_execute(command, output_dir)


def i_create_source_with_project_id(step, data=None, output_dir=None):
    """Step: I create a BigML source uploading train <data> file and associate
    it to the last created project id storing results in <output_dir>
    """
    ok_(data is not None)
    command = ("bigmler --train " + res_filename(data) +
               " --no-model --no-dataset --store --output-dir " +
               output_dir +
               " --project-id " + world.project['resource'])
    base_shell_execute(command, output_dir)


def check_source_in_project(step):
    """Step: the source is associated to the project"""
    eq_(world.project['resource'], world.source['object']['project'])


def i_check_create_project(step, organization=False):
    """Step: I check that the project has been created"""
    project_file = os.path.join(world.directory, "project")
    message = None
    try:
        with open(project_file) as handler:
            project = check_resource(handler.readline().strip(),
                                     world.api.get_project)
            world.projects.append(project['resource'])
            world.project = project
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)
    if organization:
        world.api = BigML(world.username, world.api_key, debug=world.debug,
                          project=world.project["resource"])
        print(world.api.connection_info())


def check_source_in_no_project(step):
    """Step: the source has no project association"""
    ok_(world.source['object']['project'] is None)


def i_create_project(step, project=None, output_dir=None):
    """Step: I create a BigML project <project> and log results
    in <output_dir>
    """
    ok_(project is not None)
    command = ("bigmler project --name \"" + project +
               "\" --store --output-dir " +
               output_dir)
    base_shell_execute(command, output_dir)


def i_update_project(step, params=None, values=None):
    """Step: I update the project params <params> to <values>"""
    ok_(params is not None and values is not None)
    command = ("bigmler project --project-id " +
               world.project['resource'] +
               " --store --output-dir " +
               world.directory)
    for index, param in enumerate(params):
        value = values[index]
        command += " --%s %s" % (param, value)
    base_shell_execute(command, world.directory)


def check_params_values(step, params=None, values=None):
    """Step: the project params <params> are <values>"""
    for index, param in enumerate(params):
        value = values[index]
        eq_(world.project['object'][param], value)


def i_check_update_project(step):
    """Step: I check that the project has been updated"""
    project = check_resource(world.project['resource'],
                             world.api.get_project)
    world.project = project
