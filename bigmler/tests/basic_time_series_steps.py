# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2017-2024 BigML
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
import shutil

from bigml.api import check_resource

from bigmler.tests.common_steps import shell_execute, check_rows_equal
from bigmler.tests.world import world, res_filename, ok_


def i_create_all_ts_resources_with_no_headers(
    step, data=None, output=None):
    """Step: I create BigML time series resources uploading train <data>
    file with no headers and log forecasts in <output>
    """
    ok_(data is not None and output is not None)
    command = ("bigmler time-series --train " + res_filename(data) +
               " --store --output " + output +
               " --horizon 10 --no-train-header --no-test-header")
    shell_execute(command, output, options='--prediction-header')


def i_create_all_ts_resources(step, data=None, test=None, output=None):
    """Step: I create BigML time series resources uploading train <data>
    file to test <test> and log forecasts in <output>
    """
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler time-series --train " + res_filename(data) +
               " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


def i_create_all_ts_resources_to_evaluate(step, data=None, output=None):
    """Step: I create BigML time series resources uploading train <data> file
    to evaluate and log evaluation in <output>
    """
    ok_(data is not None and output is not None)
    command = ("bigmler time-series --train " + res_filename(data) +
               " --evaluate" +
               " --store --output " + output)
    shell_execute(command, output)


def i_check_create_time_series(step):
    """Step: I check that the time series has been created"""
    ts_file = os.path.join(world.directory, "time_series")
    message = None
    #pylint: disable=locally-disabled,import-outside-toplevel
    try:
        with open(ts_file) as handler:
            ts_ = check_resource(handler.readline().strip(),
                                 world.api.get_time_series)
            world.time_series_set.append(ts_['resource'])
            world.time_series = ts_
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_forecasts(step, check_file):
    """Step: the local forecasts file is like <check_file>"""
    check_file_path = res_filename(check_file)
    forecasts_file_path = "%s_%s.csv" % \
        (world.output, world.time_series["object"]["objective_field"])
    message = None
    #pylint: disable=locally-disabled,import-outside-toplevel
    try:
        message = check_rows_equal(forecasts_file_path,
            check_file_path)
    except Exception:
        import traceback
        shutil.copyfile(forecasts_file_path, "%s.new" % check_file_path)
        message = traceback.format_exc()
    ok_(message is None, msg=message)
