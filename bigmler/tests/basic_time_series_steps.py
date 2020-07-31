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
        if retcode < 0:
            assert False
        else:
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
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create BigML time series resources uploading train "(.*?)"'
#       ' file with no headers and log forecasts in "([^"]*)"$')
def i_create_all_ts_resources_with_no_headers( \
    step, data=None, output=None):
    ok_(data is not None and output is not None)
    command = ("bigmler time-series --train " + res_filename(data) +
               " --store --output " + output +
               " --horizon 10 --no-train-header --no-test-header")
    shell_execute(command, output, options='--prediction-header')


#@step(r'I create BigML time series resources uploading train "(.*?)"'
#       ' file to test "(.*?)" and log forecasts in "([^"]*)"$')
def i_create_all_ts_resources(step, data=None, test=None, output=None):
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler time-series --train " + res_filename(data) +
               " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML time series resources uploading train "(.*)" file to evaluate and log evaluation in "([^"]*)"$')
def i_create_all_ts_resources_to_evaluate(step, data=None, output=None):
    ok_(data is not None and output is not None)
    command = ("bigmler time-series --train " + res_filename(data) +
               " --evaluate" +
               " --store --output " + output)
    shell_execute(command, output)


#@step(r'I check that the time series has been created')
def i_check_create_time_series(step):
    ts_file = "%s%stime_series" % (world.directory, os.sep)
    try:
        ts_file = open(ts_file, "r")
        ts = check_resource(ts_file.readline().strip(),
                            world.api.get_time_series)
        world.time_series_set.append(ts['resource'])
        world.time_series = ts
        ts_file.close()
    except Exception as exc:
        assert False, str(exc)

#@step(r'the local forecasts file is like "(.*)"')
def i_check_forecasts(step, check_file):
    check_file = res_filename(check_file)
    forecasts_file = "%s_%s.csv" % \
        (world.output, world.time_series["object"]["objective_field"])
    import traceback
    try:
        with UnicodeReader(forecasts_file) as forecasts_file:
            with UnicodeReader(check_file) as check_file:
                for row in forecasts_file:
                    check_row = next(check_file)
                    assert_equal(len(check_row), len(row))
                    for index in range(len(row)):
                        dot = row[index].find(".")
                        decimal_places = 1
                        if dot > 0 or (check_row[index].find(".") > 0
                                       and check_row[index].endswith(".0")):
                            try:
                                decimal_places = min(len(row[index]),
                                                     len(check_row[index])) \
                                    - dot - 1
                                row[index] = round(float(row[index]),
                                                   decimal_places)
                                check_row[index] = round(float(check_row[ \
                                    index]), decimal_places)
                            except ValueError:
                                decimal_places = 1
                            assert_almost_equal(check_row[index], row[index],
                                                places=(decimal_places - 1))
                        else:
                            assert_equal(check_row[index], row[index])
    except Exception as exc:
        assert False, traceback.format_exc()
