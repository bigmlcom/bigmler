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


import os
import time
import json
from bigmler.tests.world import world
from subprocess import check_call, CalledProcessError
from bigml.api import check_resource
from bigml.io import UnicodeReader
from bigmler.checkpoint import file_number_of_lines
from bigmler.utils import storage_file_name, open_mode
from bigmler.tests.common_steps import check_debug
from nose.tools import ok_, assert_equal, assert_not_equal


def shell_execute(command, output, test=None, options=None,
                  test_rows=None, project=True):
    """Excute bigmler command in shell

    """
    command = check_debug(command, project=project)
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    try:
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            if test is not None:
                world.test_lines = file_number_of_lines(test)
                if options is None or \
                        options.find('--projection-header') == -1:
                    # test file has headers in it, so first line must be ignored
                    world.test_lines -= 1
            elif test_rows is not None:
                world.test_lines = test_rows
                if options is not None and \
                        options.find('--projection-header') > -1:
                    world.test_lines += 1
            elif options is not None and \
                    options.find('--projection-header') > -1:
                world.test_lines += 1
            world.output = output
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)

#@step(r'I create BigML external connection using  "(.*)", "(.*)", "(.*)", "(.*)", "(.*)", "(.*)" and "(.*)" and log files in  "(.*)"$')
def i_create_external_connector(step, name=None, source=None, host=None,
                                port=None, database=None, user=None,
                                password=None ,output_dir=None):
    ok_(name is not None and source is not None and host is not None and
        port is not None and database is not None and user is not None and
        password is not None and output_dir is not None)
    command = ("bigmler connector --name \"" + name +
               "\" --host " + host +
               " --port " + port +
               " --database " +  database +
               " --user " + user +
               " --password " + password +
               " --engine " + source +
               " --store --output-dir " + output_dir)
    shell_execute(command, "%s/x" % output_dir)


#@step(r'I check that the external connection is ready')
def i_check_external_connector(step):
    connector_file = "%s%sexternal_connector" % (world.directory, os.sep)
    try:
        connector_file = open(connector_file, "r")
        connector = check_resource(connector_file.readline().strip(),
                                   world.api.get_external_connector)
        world.external_connectors.append(connector['resource'])
        world.external_connector = connector
        connector_file.close()
    except Exception as exc:
        assert False, str(exc)



#@step(r'I update the external connection to "(.*)" and logs to "(.*)"$')
def i_update_external_connector(step, name=None, output_dir=None):
    ok_(name is not None and output_dir is not None)
    command = ("bigmler connector --external-connector " +
               world.external_connector["resource"] +
               " --name \"" + name + "\"" + " --output-dir " + output_dir)
    shell_execute(command, "%s/x" % output_dir)


#@step(r'I check that the external connection is ready')
def i_check_external_connector_name(step, name=None):
    ec_name = world.external_connector.get( \
        "object", world.external_connector).get("name")
    assert_equal(ec_name, name)
