# -*- coding: utf-8 -*-
#
# Copyright 2016 BigML
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

from nose.tools import assert_equal, assert_not_equal, ok_
from bigmler.tests.world import world, res_filename
from subprocess import check_call, CalledProcessError
from bigml.api import check_resource
from bigmler.checkpoint import file_number_of_lines
from bigmler.tests.common_steps import check_debug


def shell_execute(command, output, test=None, options=None,
                  data=None, test_split=None):
    """Excute bigmler command in shell

    """
    command = check_debug(command)
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    try:
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            if test is not None:
                world.test_lines = file_number_of_lines(test)
                world.test_lines -= 1
                # prediction file has headers in it,
                # so first line must be ignored
                world.prediction_header = options is not None and \
                    options.find('--prediction-header') > -1
            if test_split is not None:
                data_lines = file_number_of_lines(data) - 1
                world.test_lines = int(data_lines * float(test_split))
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create BigML execution resources from source code "(.*)" and log results in  "(.*)"$')
def i_create_all_execution_resources(step, code=None, output_dir=None):
    ok_(code is not None and output_dir is not None)
    command = ("bigmler execute --code \"" + code +
               "\" --store --output-dir " + output_dir)
    shell_execute(command, "%s/xx.txt" % output_dir)


#@step(r'I check that the script has been created')
def i_check_create_script(step):
    script_file = "%s%sscripts" % (world.directory, os.sep)
    try:
        script_file = open(script_file, "r")
        script = check_resource(script_file.readline().strip(),
                                world.api.get_script)
        world.scripts.append(script['resource'])
        world.script = script
        script_file.close()
        assert True
    except Exception, exc:
        assert False, str(exc)


#@step(r'I check that the execution has been created')
def i_check_create_execution(step):
    execution_file = os.path.join(world.directory, "execution")
    try:
        execution_file = open(execution_file, "r")
        execution = check_resource(execution_file.readline().strip(),
                                   world.api.get_execution)
        world.executions.append(execution['resource'])
        world.execution = execution
        execution_file.close()
        assert True
    except Exception, exc:
        assert False, str(exc)


#@step(r'I check that the result is ready')
def i_check_create_result(step):
    result_file = os.path.join(world.directory, "whizzml_results.json")
    try:
        result_file = open(result_file, "r")
        world.results = json.load(result_file)
        del world.results["sources"]
        result_file.close()
        assert True
    except Exception, exc:
        assert False, str(exc)

#@step(r'the result is like "(.*)"')
def i_check_result_is(step, check_file=None):
    try:
        check_file = open(res_filename(check_file), "r")
        results = json.load(check_file)
        del results["sources"]
        assert_equal(results, world.results)
        check_file.close()
        assert True
    except Exception, exc:
        assert False, str(exc)
