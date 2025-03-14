# -*- coding: utf-8 -*-
#!/usr/bin/env python
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#
# Copyright 2017-2025 BigML
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


""" Bigmler retrain

"""

from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)


import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.basic_execute_steps as execute_steps


def setup_module():
    """Setup for the module

    """
    common_setup_module()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestRetrain:
    """Testing retrain command"""

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
            Scenario: Successfully retraining a balanced model
                Given I create a BigML balanced model from "<data>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the model has been created
                And I retrain the model from "<data>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the model has been created
                Then I check that the model has doubled its rows
                And I check that the model is balanced
        """
        print(self.test_scenario1.__doc__)
        headers = ["data", "output_dir", "output_dir_ret"]
        examples = [
            ['data/iris.csv', 'scenario_rt_1', 'scenario_rt_1b'],
            ['https://static.bigml.com/csv/iris.csv', 'scenario_rt_1c',
             'scenario_rt_1d']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_balanced_model(
                self, data=example["data"], output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_pred.i_retrain_model(
                self, data=example["data"],
                output_dir=example["output_dir_ret"])
            if not example["data"].startswith("https"):
                test_pred.i_check_create_source(self)
            execute_steps.i_check_create_execution(
                self, number_of_executions=2)
            test_pred.i_check_create_model_in_execution(self)
            test_pred.i_check_model_double(self)
            test_pred.i_check_model_is_balanced(self)

    def test_scenario2(self):
        """
            Scenario: Successfully retraining from a model using sampled dataset
                Given I create a BigML balanced model from "<data>" sampling 50% of data and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the model has been created
                And I retrain the model from "<data>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the model has been created
                Then I check that the model has doubled its rows
                And I check that the model is balanced

                Examples:
                |data |output_dir  | output_dir_ret
                |../data/iris.csv | ./scenario_rt_2 |./scenario_rt_2b |
        """
        print(self.test_scenario2.__doc__)
        headers = ["data", "output_dir", "output_dir_ret"]
        examples = [
            ['data/iris.csv', 'scenario_rt_2', 'scenario_rt_2b'],
            ['https://static.bigml.com/csv/iris.csv', 'scenario_rt_2c',
             'scenario_rt_2d']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_balanced_model_from_sample(
                self, data=example["data"], output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_dataset(self, suffix='gen ')
            test_pred.i_check_create_model(self)
            test_pred.i_retrain_model(
                self, data=example["data"],
                output_dir=example["output_dir_ret"])
            if not example["data"].startswith("https"):
                test_pred.i_check_create_source(self)
            execute_steps.i_check_create_execution(
                self, number_of_executions=2)
            test_pred.i_check_create_model_in_execution(self)
            test_pred.i_check_model_double(self)
            test_pred.i_check_model_is_balanced(self)
