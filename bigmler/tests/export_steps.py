# -*- coding: utf-8 -*-
#
# Copyright 2017 BigML
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

from nose.tools import assert_equal, assert_not_equal, ok_, eq_
from bigmler.tests.world import world, res_filename
from subprocess import check_call, CalledProcessError
from bigml.api import check_resource
from bigmler.checkpoint import file_number_of_lines
from bigmler.tests.common_steps import check_debug
from bigmler.export.dispatcher import EXTENSIONS
from bigml.util import PY3


def extract_content(file_handler):
    """reads the file and removes the model ID in the comments

    """
    content = file_handler.read()
    variable_comment = " from" \
        " model/"
    try:
        position = content.index(variable_comment)
        content = content[:position] + \
            content[position + len(variable_comment) + 24:]
    except ValueError:
        pass
    return content


def shell_execute(command, output, test=None, options=None,
                  data=None, test_split=None):
    """Execute bigmler command in shell

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
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I I export the model as a function in "(.*)"$')
def i_export_model(step, language=None, output=None):
    ok_(language is not None and output is not None)
    output_dir = world.directory
    command = ("bigmler export --language " + language +
               " --output-dir " + output_dir + " --model " +
               world.model['resource'])
    shell_execute(command, output)

#@step(r'I create BigML resources uploading train "(.*)" file using "(.*)" and log in "(.*)"$')
def i_create_all_resources_to_model_with_source_attrs( \
    self, data=None, source_attributes=None, output=None):
    ok_(data is not None and source_attributes is not None
        and output is not None)
    if source_attributes != "":
        source_attributes = " --source-attributes " + \
            res_filename(source_attributes)
    command = ("bigmler --train " + res_filename(data) +
               " --output " + output + source_attributes +
               " --store --max-batch-models 1 --no-fast")
    shell_execute(command, output)

#@step(r'I check the output for "(.*)" is like "(.*)" expected file')
def i_check_if_the_output_is_like_expected_file(step, language, expected_file):
    ok_(language is not None and expected_file is not None)
    with open(res_filename(expected_file)) as file_handler:
        expected_content = extract_content(file_handler)
    with open(os.path.join(world.directory, "%s.%s" % \
            (world.model['resource'].replace("/", "_"),
             EXTENSIONS[language]))) \
            as file_handler:
        output = extract_content(file_handler)
    if PY3 and output.strip() != expected_content.strip():
        try:
            name, extension = expected_file.split(".")
            expected_file = "%s_p3.%s" % (name, extension)
            with open(res_filename(expected_file)) as file_handler:
                expected_content = extract_content(file_handler)
        except IOError:
            pass
    eq_(output.strip(), expected_content.strip(), "Found: %s\nExpected:%s" % \
        (world.directory + "/" + world.model["resource"],
         expected_file))
