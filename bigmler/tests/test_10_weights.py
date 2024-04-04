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


""" Testing weight options

"""
from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)


import bigmler.tests.basic_tst_prediction_steps as test_pred


def setup_module():
    """Setup for the module

    """
    common_setup_module()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestWeights:
    """Testing weights options in command"""

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
            Scenario: Successfully building a balanced model
                Given I create a BigML balanced model from "<data>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the model has been created
                Then I check that the model is balanced
        """
        print(self.test_scenario1.__doc__)
        headers = ["data", "output_dir"]
        examples = [
            ['data/iris.csv', 'scenario_w_1']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_balanced_model(
                self, data=example["data"], output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_pred.i_check_model_is_balanced(self)

    def test_scenario2(self):
        """
            Scenario: Successfully building a field weighted model
                Given I create a BigML field weighted model from "<data>" using field "<field>" as weight and "<objective>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the model has been created
                Then I check that the model uses as weight "<field_id>"
        """
        print(self.test_scenario2.__doc__)
        headers = ["data", "field", "output_dir", "field_id", "objective"]
        examples = [
            ['data/iris_w.csv', 'weight', 'scenario_w_2', '000005', 'species']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_weighted_field_model(
                self, data=example["data"], field=example["field"],
                output_dir=example["output_dir"],
                objective=example["objective"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_pred.i_check_weighted_model(
                self, field=example["field_id"])

    def test_scenario3(self):
        """
            Scenario: Successfully building a objective weighted model
                Given I create a BigML objective weighted model from "<data>" using the objective weights in file "<path>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the model has been created
                Then I check that the model uses as objective weights "<weights>"

                Examples:
                |data |path | output_dir  | weights
                |../data/iris.csv | ../data/weights.csv |./scenario_w_3 | [["Iris-setosa",5], ["Iris-versicolor",3]]
        """
        print(self.test_scenario3.__doc__)
        headers = ["data", "path", "output_dir", "weights"]
        examples = [
            ['data/iris.csv', 'data/weights.csv', 'scenario_w_3',
             '[["Iris-setosa",5], ["Iris-versicolor",3]]']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_objective_weighted_model(
                self, data=example["data"], path=example["path"],
                output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_pred.i_check_objective_weighted_model(
                self, weights=example["weights"])
