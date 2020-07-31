# -*- coding: utf-8 -*-
#
# Copyright 2017-2020 BigML
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
from bigmler.tests.world import world, res_filename
from subprocess import check_call, CalledProcessError
from bigml.api import check_resource
from bigml.io import UnicodeReader
from bigmler.checkpoint import file_number_of_lines
from bigmler.utils import storage_file_name, open_mode
from bigmler.tests.common_steps import check_debug
from nose.tools import ok_, assert_equal, assert_not_equal, assert_almost_equal


def shell_execute(command, output, test=None, options=None,
                  test_rows=None, project=True):
    """Excute bigmler command in shell

    """
    command = check_debug(command, project=project)
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    try:
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)
        if test is not None:
            world.test_lines = file_number_of_lines(test)
            if options is None or \
                    options.find('--prediction-header') == -1:
                # test file has headers in it, so first line must be ignored
                world.test_lines -= 1
        elif test_rows is not None:
            world.test_lines = test_rows
            if options is not None and \
                    options.find('--prediction-header') > -1:
                world.test_lines += 1
        elif options is not None and \
                options.find('--prediction-header') > -1:
            world.test_lines += 1
        world.output = output
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create BigML time series resources uploading train "(.*?)"'
#       ' file with no headers and log forecasts in "([^"]*)"$')
def i_create_all_ts_resources_with_no_headers( \
    step, data=None, output=None):
    ok_(data is not None and output is not None)
    command = ("bigmler time-series --train " + res_filename(data) +
               " --store --output " + output +
               " --no-train-header --no-test-header")
    shell_execute(command, output, test=test, options='--prediction-header')


#@step(r'I create BigML time series resources uploading train "(.*?)"'
#       ' file to test "(.*?)" and log forecasts in "([^"]*)"$')
def i_create_all_resources(step, data=None, test=None, output=None):
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)
