# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2016-2024 BigML
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
import json

from bigml.api import check_resource

from bigmler.tests.common_steps import shell_execute
from bigmler.tests.world import world, res_filename, ok_, eq_


def i_create_all_execution_resources(step, code=None, output_dir=None):
    """Step: I create BigML execution resources from source code <code> and log
    results in <output_dir>
    """
    ok_(code is not None and output_dir is not None)
    command = ("bigmler execute --code \"" + code +
               "\" --store --output-dir " + output_dir)
    shell_execute(command, "%s/xx.txt" % output_dir)


def i_create_all_library_resources(step, code_file=None, output_dir=None):
    """Step: I create BigML library from code in file <code_file> and log
    results in <output_dir>
    """
    ok_(code_file is not None and output_dir is not None)
    command = ("bigmler execute --code-file " + res_filename(code_file) +
               " --store --to-library --output-dir " + output_dir)
    shell_execute(command, "%s/xx.txt" % output_dir)


def i_create_all_execution_with_io_resources(
    step, code_file=None, output_dir=None, inputs_dec=None,
    outputs_dec=None, inputs=None):
    """Step: I create BigML execution resources from code in file <code_file>
    with inputs <inputs_dec>, outputs <outputs_dec> and inputs <inputs> and
    log results in <output_dir>
    """
    ok_(code_file is not None and output_dir is not None and
        inputs_dec is not None and outputs_dec is not None and
        inputs is not None)
    command = ("bigmler execute --code-file " + res_filename(code_file) +
               " --store --declare-inputs " + res_filename(inputs_dec) +
               " --declare-outputs "+ res_filename(outputs_dec) +
               " --inputs " + res_filename(inputs) +
               " --output-dir " + output_dir)
    shell_execute(command, "%s/xx.txt" % output_dir)


def i_create_from_whizzml_package(step, package_dir=None, output_dir=None):
    """Step: 'I create a BigML whizzml package from <package_dir> and log
    results in <output_dir>
    """
    ok_(package_dir is not None and output_dir is not None)
    command = ("bigmler whizzml --package-dir " + res_filename(package_dir) +
               " --store --output-dir " + output_dir)
    shell_execute(command, "%s/xx.txt" % output_dir)


def i_check_create_script(step):
    """Step: I check that the script has been created"""
    script_file = os.path.join(world.directory, "scripts")
    message = None
    try:
        with open(script_file) as handler:
            script = check_resource(handler.readline().strip(),
                                    world.api.get_script)
            world.scripts.append(script['resource'])
            world.script = script
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_create_execution(step, number_of_executions=1):
    """Step: I check that the execution has been created"""
    execution_file = os.path.join(world.directory, "execution")
    message = None
    try:
        with open(execution_file) as handler:
            for _ in range(number_of_executions):
                execution = check_resource(handler.readline().strip(),
                                           world.api.get_execution)
                world.executions.append(execution['resource'])
                world.execution = execution
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_create_result(step):
    """Step: I check that the result is ready"""
    result_file = os.path.join(world.directory, "whizzml_results.json")
    message = None
    try:
        with open(result_file) as handler:
            world.results = json.load(handler)
        del world.results["sources"]
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_result_is(step, check_file=None):
    """Step: the result is like <check_file>"""
    try:
        with open(res_filename(check_file)) as handler:
            results = json.load(handler)
        del results["sources"]
        eq_(results, world.results)
    except Exception as exc:
        message = str(exc)
        ok_(message is None, msg=message)


def i_check_create_library(step):
    """Step: I check that the library has been created"""
    library_file = os.path.join(world.directory, "library")
    message = None
    try:
        with open(library_file) as handler:
            library = check_resource(handler.readline().strip(),
                                     world.api.get_library)
            world.libraries.append(library['resource'])
            world.library = library
    except Exception as exc:
        message = str(exc)
        ok_(message is None, msg=message)


def i_check_create_package_script(step, package_dir=None):
    """Step: I check that the package script in <package_dir> has been
    created
    """
    script_file = os.path.join(world.directory, os.path.basename(package_dir),
                               "scripts")
    message = None
    try:
        with open(script_file) as handler:
            script = check_resource(handler.readline().strip(),
                                    world.api.get_script)
            world.scripts.append(script['resource'])
            world.script = script
    except Exception as exc:
        message = str(exc)
        ok_(message is None, msg=message)



def i_create_from_whizzml_package_embedding(step, package_dir=None,
                                            output_dir=None):
    """Step: I create a BigML whizzml package from <package_dir>, embed any
    library and log results in <output_dir>
    """
    ok_(package_dir is not None and output_dir is not None)
    command = ("bigmler whizzml --package-dir " + res_filename(package_dir) +
               " --embed-libs --store --output-dir " + output_dir)
    shell_execute(command, "%s/xx.txt" % output_dir)
