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

import sys

from bigmler.tests.common_steps import shell_execute, base_shell_execute
from bigmler.tests.world import res_filename, ok_

CAT = "type " if sys.platform == "win32" else "cat "


def i_create_all_resources_to_test_from_stdin(
    step, data=None, test=None, name=None, output=None):
    """Step: I create BigML resources uploading train <data> file to test
    <test> read from stdin with name <name> and log predictions in <output>
    """
    ok_(data is not None and test is not None and output is not None and
        name is not None)
    test = res_filename(test)

    command = (CAT + test + "|bigmler --train " + res_filename(data) +
               " --test --store --output " + output + " --name \"" +
               name + "\" --max-batch-models 1")
    shell_execute(command, output, test=test)


def i_create_source_from_stdin(step, data=None, output_dir=None):
    """Step: I create a BigML source from stdin using train <data>
    file and logging in <output_dir>
    """
    ok_(data is not None and output_dir is not None)
    command = (CAT + res_filename(data) + "|bigmler --train " +
               "--store --no-dataset --no-model --output-dir " +
               output_dir + " --max-batch-models 1")
    base_shell_execute(command, output_dir)
