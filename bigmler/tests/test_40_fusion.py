# -*- coding: utf-8 -*-
#!/usr/bin/env python
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#
# Copyright 2019-2024 BigML
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

""" Testing fusion predictions creation

"""

from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)


import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.basic_batch_tst_prediction_steps as batch_pred
import bigmler.tests.basic_fusion_steps as fs_pred
import bigmler.tests.evaluation_steps as evaluation


def setup_module():
    """Setup for the module

    """
    common_setup_module()
    test = TestPrediction()
    test.bigml = {"method": "setup_scenario01"}
    test.setup_scenario01()


def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()


class TestPrediction:
    """Testing fusion predictions"""

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


    def setup_scenario01(self):
        """
        Scenario: Successfully building a model and deepnet

        """
        print(self.setup_scenario01.__doc__)
        headers = ["data", "output_dir"]
        examples = [
            ['data/iris.csv', 'scenario1_fs']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            fs_pred.setup_for_fusion(
                self, train=example["data"], output_dir=example["output_dir"])

    def test_scenario01(self):
        """
        Scenario: Successfully building test predictions from model
            And I create BigML fusion resources using preset models to test "<test>" and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"

        """
        print(self.test_scenario01.__doc__)
        headers = ["test", "output", "predictions_file"]
        examples = [
            ['data/test_iris.csv', 'scenario1_fs/predictions.csv',
             'check_files/predictions_iris_fs.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            fs_pred.i_create_fs_resources_from_model(
                self, test=example["test"], output=example["output"])
            fs_pred.i_check_create_fusion(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario02(self):
        """
        Scenario: Successfully building batch test predictions from model
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML fusion resources using model built from "<train>" to test "<test>" as a batch prediction and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        print(self.test_scenario02.__doc__)
        headers = ["test", "output", "predictions_file"]
        examples = [
            ['data/test_iris.csv', 'scenario2_fs/predictions.csv',
             'check_files/predictions_iris_fs.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            fs_pred.i_create_fs_resources_from_model_remote(
                self, test=example["test"], output=example["output"])
            fs_pred.i_check_create_fusion(self)
            batch_pred.i_check_create_batch_prediction(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario03(self):
        """
        Scenario: Successfully building batch test predictions from model with customized output
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML fusion resources using model built on "<train>" to test "<test>" as a batch prediction with output format "<batch-output>" and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        print(self.test_scenario03.__doc__)
        headers = ["test", "batch_output", "output", "predictions_file"]
        examples = [
            ['data/test_iris.csv', 'data/batch_output.json',
             'scenario3_fs/predictions.csv',
             'check_files/predictions_iris_fs_prob.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            fs_pred.i_create_fs_resources_from_model_remote_with_options(
                self, test=example["test"], output=example["output"],
                options_file=example["batch_output"])
            fs_pred.i_check_create_fusion(self)
            batch_pred.i_check_create_batch_prediction(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario04(self):
        """
        Scenario: Successfully building evaluation from fusion
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML fusion resources using pretrained model to test "<test>" as an evaluation and log predictions in "<output>"
            Then the evaluation file is like "<json_evaluation_file>"
        """
        print(self.test_scenario04.__doc__)
        headers = ["output", "json_evaluation_file"]
        examples = [
            ['scenario_fs_e1/evaluation',
             'check_files/evaluation_iris_fs.json']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            fs_pred.i_create_fs_resources_from_mode_and_evaluate(
                self, output=example["output"])
            fs_pred.i_check_create_fusion(self)
            test_pred.i_check_create_evaluation(self)
            evaluation.then_the_evaluation_file_is_like(
                self, example["json_evaluation_file"])
