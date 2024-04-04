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


""" Testing predictions with proportional missing strategy

"""
from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)


import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.evaluation_steps as evaluation


def setup_module():
    """Setup for the module

    """
    common_setup_module()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestProportionalMissing:
    """Testing missings proportional strategy"""

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
            Scenario: Successfully building test predictions with proportional missing strategy:
                Given I create BigML resources uploading train "<data>" file to test "<test>" with proportional missing strategy and log predictions in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the model has been created
                And I check that the predictions are ready
                Then the local prediction file is like "<predictions_file>"
        """
        print(self.test_scenario1.__doc__)
        headers = ["data", "test", "output", "predictions_file"]
        examples = [
            ['data/iris.csv', 'data/test_iris_nulls.csv',
             'scenario_mis_1/predictions.csv',
             'check_files/predictions_iris_nulls.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_all_resources_proportional(
                self, data=example["data"], test=example["test"],
                output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario2(self):
        """
            Given I create BigML resources uploading train "<data>" file to test "<test>" remotely with proportional missing strategy and log predictions in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the model has been created
            And I check that the source has been created from the test file
            And I check that the dataset has been created from the test file
            And I check that the batch prediction has been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        print(self.test_scenario2.__doc__)
        headers = ["data", "test", "output", "predictions_file"]
        examples = [
            ['data/iris.csv', 'data/test_iris_nulls.csv', 'scenario_mis_2/predictions.csv', 'check_files/predictions_iris_nulls.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_all_resources_remote_proportional(
                self, data=example["data"], test=example["test"],
                output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_pred.i_check_create_test_source(self)
            test_pred.i_check_create_test_dataset(self)
            test_pred.i_check_create_batch_prediction(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(
                self, example["predictions_file"])

    def test_scenario3(self):
        """
            Scenario: Successfully building evaluations from start:
                Given I create BigML resources uploading train "<data>" file to create model and log in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the model has been created
                And I evaluate "<test>" with proportional missing strategy
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the evaluation has been created
                Then the evaluation file is like "<json_evaluation_file>"
        """
        print(self.test_scenario3.__doc__)
        headers = ["data", "test", "output", "json_evaluation_file"]
        examples = [
            ['data/iris.csv', 'data/iris_nulls.csv',
             'scenario_mis_3/evaluation',
             'check_files/evaluation_iris_nulls.json']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_all_resources_to_model(
                self, data=example["data"], output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            evaluation.i_create_proportional_to_evaluate(
                self, test=example["test"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_pred.i_check_create_evaluation(self)
            evaluation.then_the_evaluation_file_is_like(
                self, example["json_evaluation_file"])
