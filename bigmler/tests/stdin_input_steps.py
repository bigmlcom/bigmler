# -*- coding: utf-8 -*-
#
# Copyright 2014-2016 BigML
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
import sys


from bigmler.tests.world import world, res_filename
from subprocess import check_call, CalledProcessError
from bigml.api import check_resource
from bigmler.checkpoint import file_number_of_lines
from bigmler.tests.common_steps import check_debug
from bigmler.tests.basic_tst_prediction_steps import shell_execute
from bigmler.utils import PYTHON3

CAT = u"type " if sys.platform == "win32" else u"cat "

#@step(r'I create BigML resources uploading train "(.*)" file to test "(.*)" read from stdin with name "(.*)" and log predictions in "(.*)"$')
def i_create_all_resources_to_test_from_stdin(step, data=None, test=None, name=None, output=None):
    if data is None or test is None or output is None or name is None:
        assert False

    test = res_filename(test)
    if not PYTHON3:
        name = name.decode("utf-8")

    command = (CAT + test + u"|bigmler --train " + res_filename(data) +
               u" --test --store --output " + output + u" --name \"" +
               name + u"\" --max-batch-models 1")
    shell_execute(command, output, test=test)


#@step(r'I create a BigML source from stdin using train "(.*)" file and logging in "(.*)"$')
def i_create_source_from_stdin(step, data=None, output_dir=None):
    if data is None or output_dir is None:
        assert False
    command = (CAT + res_filename(data) + u"|bigmler --train " +
               u"--store --no-dataset --no-model --output-dir " +
               output_dir + u" --max-batch-models 1")
    shell_execute(command, output_dir + "/test", test=None)
