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


from bigmler.tests.common_steps import shell_execute
from bigmler.tests.world import res_filename, ok_


def i_create_all_ts_resources_with_no_headers(
    step, data=None, output=None):
    """Step: I create BigML time series resources uploading train <data>
    file with no headers and log forecasts in <output>
    """
    ok_(data is not None and output is not None)
    command = ("bigmler time-series --train " + res_filename(data) +
               " --store --output " + output +
               " --no-train-header --no-test-header")
    shell_execute(command, output, options='--prediction-header')


def i_create_all_resources(step, data=None, test=None, output=None):
    """Step: I create BigML time series resources uploading train <data>
    file to test <test> and log forecasts in <output>
    """
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)
