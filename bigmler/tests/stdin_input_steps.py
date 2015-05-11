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
from bigml.api import check_resource
from bigmler.checkpoint import file_number_of_lines
from bigmler.tests.common_steps import check_debug
from bigmler.tests.basic_tst_prediction_steps import shell_execute


#@step(r'I create BigML resources uploading train "(.*)" file to test "(.*)" read from stdin and log predictions in "(.*)"$')
def i_create_all_resources_to_test_from_stdin(step, data=None, test=None, output=None):
    if data is None or test is None or output is None:
        assert False
    test = res_filename(test)
    command = ("cat " + test + "|bigmler --train " + res_filename(data) +
               " --test --store --output " + output + " --max-batch-models 1")
    shell_execute(command, output, test=test)


#@step(r'I create a BigML source from stdin using train "(.*)" file and logging in "(.*)"$')
def i_create_source_from_stdin(step, data=None, output_dir=None):
    if data is None or output_dir is None:
        assert False
    command = ("cat " + res_filename(data) + "|bigmler --train " +
               "--store --no-dataset --no-model --output-dir " +
               output_dir + " --max-batch-models 1")
    shell_execute(command, output_dir + "/test", test=None)
