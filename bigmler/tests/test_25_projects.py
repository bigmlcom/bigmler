# -*- coding: utf-8 -*-
#!/usr/bin/env python
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#
# Copyright 2015-2024 BigML
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
""" Testing projects

"""
from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)

import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.project_creation_steps as test_project
import bigmler.tests.delete_subcommand_steps as delete


def setup_module():
    """Setup for the module

    """
    common_setup_module()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestProjects:
    """Testing projects commands"""

    def setup_method(self, method):
        """
            Debug information
        """
        self.bigml = {}
        self.bigml["method"] = method.__name__
        print("\n-------------------\nTests in: %s\n" % __name__)

    def teardown_method(self):
        """Calling generic teardown for every method

        """
        world.clear_paths()
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)
        self.bigml = {}

    def test_scenario1(self):
        """
        Scenario: Successfully creating a project and associating resources to it:
            Given I create a BigML source uploading train "<data>" file and associate it to a new project named "<project>" storing results in "<output_dir>"
            And I check that the project has been created
            And I check that the source has been created
            Then the source is associated to the project
        """
        print(self.test_scenario1.__doc__)
        headers = ["data", "project", "output_dir"]
        examples = [
            ['data/iris.csv', 'My new project', 'scenario_p_1']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_project.i_create_source_with_project(
                self, data=example["data"],
                project=example["project"], output_dir=example["output_dir"])
            test_project.i_check_create_project(self)
            test_pred.i_check_create_source(self)
            test_project.check_source_in_project(self)

    def test_scenario2(self):
        """
        Scenario: Successfully associating resources to an existing project:
            Given I create a BigML source uploading train "<data>" file and associate it to a new project named "<project>" storing results in "<output_dir>"
            And I check that the project has been created
            And I check that the source has been created
            And I create a BigML source uploading train "<data>" file and associate it to the last created project id storing results in "<output_dir2>"
            Then the source is associated to the project
        """
        print(self.test_scenario2.__doc__)
        headers = ["data", "project", "output_dir", "output_dir2"]
        examples = [
            ['data/iris.csv', 'My new project', 'scenario_p_2', 'scenario_p_2_1']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_project.i_create_source_with_project(
                self, data=example["data"], project=example["project"],
                output_dir=example["output_dir"])
            test_project.i_check_create_project(self)
            test_pred.i_check_create_source(self)
            test_project.i_create_source_with_project_id(
                self, data=example["data"], output_dir=example["output_dir"])
            test_project.check_source_in_project(self)

    def test_scenario3(self):
        """
        Scenario: Successfully creating resources with no project association:
            Given I create a BigML source from file "<data>" storing results in "<output_dir>"
            And I check that the source has been created
            Then the source has no project association
        """
        print(self.test_scenario3.__doc__)
        headers = ["data", "output_dir"]
        examples = [
            ['data/iris.csv', 'scenario_p_3']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            delete.i_create_source_from_file(
                self, data=example["data"],
                output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_project.check_source_in_no_project(self)

    def test_scenario4(self):
        """
        Scenario: Successfully creating and updating project:
            Given I create a BigML project "<project>" and log results in "<output_dir>"
            And I check that the project has been created
            And I update the project params "<params>" to "<values>"
            And I check that the project has been updated
            Then the project params "<params>" are "<values>"
        """
        print(self.test_scenario4.__doc__)
        headers = ["project", "output_dir", "params", "values"]
        examples = [
            ['My new project', 'scenario_p_4',
             ['name', 'category'], ['my_project_name', 1]]]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_project.i_create_project(
                self, project=example["project"],
                output_dir=example["output_dir"])
            test_project.i_check_create_project(self)
            test_project.i_update_project(
                self, params=example["params"],
                values=example["values"])
            test_project.i_check_update_project(self)
            test_project.check_params_values(
                self, params=example["params"],
                values=example["values"])
