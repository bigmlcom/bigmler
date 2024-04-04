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

from bigmler.tests.common_steps import shell_execute
from bigmler.export.dispatcher import EXTENSIONS
from bigmler.tests.world import world, res_filename, ok_, eq_


def extract_content(file_handler):
    """Reads the file and removes the model ID in the comments"""
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


def i_export_model(step, language=None, output=None):
    """Step: I export the model as a function in <output>"""
    ok_(language is not None and output is not None)
    output_dir = world.directory
    command = ("bigmler export --language " + language +
               " --output-dir " + output_dir + " --model " +
               world.model['resource'])
    shell_execute(command, output)

def i_create_all_resources_to_model_with_source_attrs(
    self, data=None, source_attributes=None, output=None):
    """Step: I create BigML resources uploading train <data> file using
    <source_attributes> and log in <output>
    """
    ok_(data is not None and source_attributes is not None
        and output is not None)
    if source_attributes != "":
        source_attributes = " --source-attributes " + \
            res_filename(source_attributes)
    command = ("bigmler --train " + res_filename(data) +
               " --output " + output + source_attributes +
               " --store --max-batch-models 1 --no-fast")
    shell_execute(command, output)


def i_check_if_the_output_is_like_expected_file(step, language, expected_file):
    """Step: I check the output for <language> is like <expected_file>
    expected file
    """
    ok_(language is not None and expected_file is not None)
    with open(res_filename(expected_file)) as file_handler:
        expected_content = extract_content(file_handler)
    with open(os.path.join(world.directory, "%s.%s" % \
            (world.model['resource'].replace("/", "_"),
             EXTENSIONS[language]))) \
            as file_handler:
        output = extract_content(file_handler)
    if output.strip() != expected_content.strip():
        try:
            name, extension = expected_file.split(".")
            expected_file = "%s_p3.%s" % (name, extension)
            out_file = "%s.%s.out" % (name, extension)
            with open(res_filename(out_file), "w") as writer:
                writer.write(output)
            with open(res_filename(expected_file)) as file_handler:
                expected_content = extract_content(file_handler)
        except IOError:
            pass
    eq_(output.strip(), expected_content.strip(),
        msg="Found: %s\nExpected:%s" % \
        (world.directory + "/" + world.model["resource"],
         expected_file))
