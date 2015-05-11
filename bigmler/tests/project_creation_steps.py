# -*- coding: utf-8 -*-
#
# Copyright 2014-2015 BigML
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
from __future__ import absolute_import


import os
import time
import csv
import json
from bigmler.tests.world import world, res_filename
from subprocess import check_call, CalledProcessError
from bigmler.checkpoint import file_number_of_lines
from bigmler.utils import SYSTEM_ENCODING
from bigml.api import check_resource
from bigmler.tests.common_steps import check_debug


#@step(r'I create a BigML source uploading train "(.*)" file and associate it to a new project named "(.*)" storing results in "(.*)"')
def i_create_source_with_project(step, data=None, project=None, output_dir=None):
    if data is None:
        assert False
    world.directory = output_dir
    world.folders.append(world.directory)
    #Check if the project already exists
    previous_projects = world.api.list_projects('name=%s' % project)
    while previous_projects['meta']['total_count'] > 0:
        print "the project %s already exists, trying with:" % project
        project += " " + project
        print project
        previous_projects = world.api.list_projects('name=%s' % project)
    try:
        command = (u"bigmler --train " + res_filename(data) +
                   u" --no-model --no-dataset --store --output-dir " +
                   output_dir +
                   u" --project=\"" + project + "\"")
        command = check_debug(command)
        retcode = check_call(command.encode(SYSTEM_ENCODING), shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = output_dir
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create a BigML source uploading train "(.*)" file and associate it to the last created project id storing results in "(.*)"')
def i_create_source_with_project_id(step, data=None, output_dir=None):
    if data is None:
        assert False
    world.directory = output_dir
    world.folders.append(world.directory)
    try:
        command = (u"bigmler --train " + res_filename(data) +
                   u" --no-model --no-dataset --store --output-dir " +
                   output_dir +
                   u" --project-id " + world.project['resource'])
        command = check_debug(command)
        retcode = check_call(command.encode(SYSTEM_ENCODING), shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = output_dir
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'the source is associated to the project')
def check_source_in_project(step):
    if world.project['resource'] == world.source['object']['project']:
        assert True
    else:
        assert False, ("Project id is %s and source is associated to %s" % (
                       world.project['resource'],
                       world.source['object']['project']))


#@step(r'I check that the project has been created$')
def i_check_create_project(step):
    project_file = "%s%sproject" % (world.directory, os.sep)
    try:
        project_file = open(project_file, "r")
        project = check_resource(project_file.readline().strip(),
                                 world.api.get_project)
        world.projects.append(project['resource'])
        world.project = project
        project_file.close()
        assert True
    except Exception, exc:
        assert False, str(exc)


#@step(r'the source has no project association')
def check_source_in_no_project(step):
    if world.source['object']['project'] is None:
        assert True
    else:
        assert False, ("Source is associated to %s" %
                       world.source['object']['project'])
