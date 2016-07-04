# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2016 BigML
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


""" Testing logistic regression predictions creation

"""
from __future__ import absolute_import

from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module,
                                 teardown_class)


import bigmler.tests.basic_execute_steps as execute

def setup_module():
    """Setup for the module

    """
    common_setup_module()


def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()


class TestExecute(object):

    def setup(self):
        """
            Debug information
        """
        print "\n-------------------\nTests in: %s\n" % __name__

    def teardown(self):
        """Calling generic teardown for every method

        """
        self.world = teardown_class()
        print "\nEnd of tests in: %s\n-------------------\n" % __name__

    def test_scenario01(self):
        """
        Scenario: Successfully creating an execution from source code:
            Given I create BigML execution resources from source code "<code>" and log results in  "<output_dir>"
            And I check that the script has been created
            And I check that the execution has been created
            And I check that the result is ready
            Then the result file is like "<result_file>"

            Examples:
            | code      | output_dir       | result_file
            | (+ 1 1)   | scenario1_exe    | check_files/results_s1exe.json

        """
        print self.test_scenario01.__doc__
        examples = [
            ['(+ 1 1)', 'scenario1_exe', 'check_files/results_s1exe.json' ]]
        for example in examples:
            print "\nTesting with:\n", example
            execute.i_create_all_execution_resources(self, example[0], example[1])
            execute.i_check_create_script(self)
            execute.i_check_create_execution(self)
            execute.i_check_create_result(self)
            execute.i_check_result_is(self, example[2])


    def test_scenario02(self):
        """
        Scenario: Successfully creating a library from file:
            Given I create BigML library from code in file "<code_file>" and log results in  "<output_dir>"
            Then I check that the library has been created

            Examples:
            | code_file         | output_dir
            | code_lib.whizzml      | scenario2_exe

        """
        print self.test_scenario02.__doc__
        examples = [
            ['data/code_lib.whizzml', 'scenario2_exe']]
        for example in examples:
            print "\nTesting with:\n", example
            execute.i_create_all_library_resources(self, example[0], example[1])
            execute.i_check_create_library(self)


    def test_scenario03(self):
        """
        Scenario: Successfully creating an execution with input/outputs from a code file:
            Given I create BigML execution resources from code in file "<code_file>" with inputs "<inputs_dec>", outputs "<outputs_dec>" and inputs "<inputs>" and log results in  "<output_dir>"
            And I check that the script has been created
            And I check that the execution has been created
            And I check that the result is ready
            Then the result file is like "<result_file>"

            Examples:
            | code_file      | output_dir       | inputs_dec           | outputs_dec           | inputs           | result_file
            | code.whizzml   | scenario3_exe    | data/inputs_dec.json | data/outputs_dec.json | data/inputs.json | check_files/results_s3exe.json

        """
        print self.test_scenario03.__doc__
        examples = [
            ['data/code.whizzml', 'scenario3_exe', 'data/inputs_dec.json', 'data/outputs_dec.json', 'data/inputs.json', 'check_files/results_s3exe.json']]
        for example in examples:
            print "\nTesting with:\n", example
            execute.i_create_all_execution_with_io_resources(self, example[0], example[1], example[2], example[3], example[4])
            execute.i_check_create_script(self)
            execute.i_check_create_execution(self)
            execute.i_check_create_result(self)
            execute.i_check_result_is(self, example[5])


    def test_scenario04(self):
        """
        Scenario: Successfully creating an whizzml package from a metadata file:
            Given I create a BigML whizzml package from "<package_dir>" and log results in  "<output_dir>"
            Then I check that the script in "<package_dir>" has been created

            Examples:
            | package_dir       | output_dir       |
            | data              | scenario4_pck    |

        """
        print self.test_scenario04.__doc__
        examples = [
            ['data', 'scenario4_pck']]
        for example in examples:
            print "\nTesting with:\n", example
            execute.i_create_from_whizzml_package(self, example[0], example[1])
            execute.i_check_create_package_script(self, example[0])
