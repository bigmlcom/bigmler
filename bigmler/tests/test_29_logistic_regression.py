# -*- coding: utf-8 -*-
#!/usr/bin/env python
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
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


""" Testing logistic regression predictions creation

"""
from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)

import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.basic_batch_tst_prediction_steps as batch_pred
import bigmler.tests.basic_logistic_r_steps as lr_pred

def setup_module():
    """Setup for the module

    """
    common_setup_module()
    test = TestPrediction()
    test.bigml = {"method": "setup_scenario02"}
    test.setup_scenario02()


def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()


class TestPrediction:
    """Testing logistic regression predictions"""

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

    def test_scenario01(self):
        """
        Scenario: Successfully building logistic regression test predictions from start with no headers:
            Given I create BigML logistic regression resources uploading train "<data>" file with no headers to test "<test>" with no headers and log predictions in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the logistic regression model has been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        print(self.test_scenario01.__doc__)
        headers = ["data", "test", "output", "predictions_file"]
        examples = [
            ['data/iris_nh.csv', 'data/test_iris_nh.csv',
             'scenario1_lr_nh/predictions.csv',
             'check_files/predictions_iris_lr.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            lr_pred.i_create_all_lr_resources_with_no_headers(
                self, example["data"], example["test"], example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            lr_pred.i_check_create_lr_model(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def setup_scenario02(self):
        """
        Scenario: Successfully building test predictions from start:
            Given I create BigML logistic regression resources uploading train "<data>" file to test "<test>" and log predictions in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the model has been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        print(self.setup_scenario02.__doc__)
        headers = ["data", "test", "output", "predictions_file"]
        examples = [
            ['data/iris.csv', 'data/test_iris.csv',
             'scenario1_lr/predictions.csv',
             'check_files/predictions_iris_lr.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            lr_pred.i_create_all_lr_resources(
                self, example["data"], example["test"], example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            lr_pred.i_check_create_lr_model(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario03(self):
        """
        Scenario: Successfully building test predictions from source
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML logistic regression resources using source to test "<test>" and log predictions in "<output>"
            And I check that the dataset has been created
            And I check that the model has been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        print(self.test_scenario03.__doc__)
        headers = ["scenario", "kwargs", "test", "output", "predictions_file"]
        examples = [
            ['scenario1_lr', '{"data": "data/iris.csv",' +
             ' "output": "scenario1_lr/predictions.csv",' +
             ' "test": "data/test_iris.csv"}', 'data/test_iris.csv',
             'scenario2_lr/predictions.csv',
             'check_files/predictions_iris_lr.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            lr_pred.i_create_lr_resources_from_source(
                self, None, test=example["test"],
                output=example["output"])
            test_pred.i_check_create_dataset(self, suffix=None)
            lr_pred.i_check_create_lr_model(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario04(self):
        """
        Scenario: Successfully building test predictions from dataset
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML logistic regression resources using dataset to test "<test>" and log predictions in "<output>"
            And I check that the model has been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        print(self.test_scenario04.__doc__)
        headers = ["scenario", "kwargs", "test", "output", "predictions_file"]
        examples = [
            ['scenario1_lr', '{"data": "data/iris.csv",' +
             ' "output": "scenario1_lr/predictions.csv",' +
             ' "test": "data/test_iris.csv"}', 'data/test_iris.csv',
             'scenario3_lr/predictions.csv',
             'check_files/predictions_iris_lr.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            lr_pred.i_create_lr_resources_from_dataset(
                self, None, test=example["test"], output=example["output"])
            lr_pred.i_check_create_lr_model(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario05(self):
        """
        Scenario: Successfully building test predictions from model
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML logistic regression resources using model to test "<test>" and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        print(self.test_scenario05.__doc__)
        headers = ["scenario", "kwargs", "test", "output", "predictions_file"]
        examples = [
            ['scenario1_lr', '{"data": "data/iris.csv",' +
             ' "output": "scenario1_lr/predictions.csv",' +
             ' "test": "data/test_iris.csv"}', 'data/test_iris.csv',
             'scenario4_lr/predictions.csv',
             'check_files/predictions_iris_lr.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            lr_pred.i_create_lr_resources_from_model(
                self, test=example["test"], output=example["output"])
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario06(self):
        """
        Scenario: Successfully building batch test predictions from model
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML logistic regression resources using model to test "<test>" as a batch prediction and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        print(self.test_scenario06.__doc__)
        headers = ["scenario", "kwargs", "test", "output", "predictions_file"]
        examples = [
            ['scenario1_lr', '{"data": "data/iris.csv",' +
             ' "output": "scenario1_lr/predictions.csv",' +
             ' "test": "data/test_iris.csv"}', 'data/test_iris.csv',
             'scenario5_lr/predictions.csv',
             'check_files/predictions_iris_lr.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            lr_pred.i_create_lr_resources_from_model_remote(
                self, test=example["test"], output=example["output"])
            batch_pred.i_check_create_batch_prediction(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario07(self):
        """
        Scenario: Successfully building batch test predictions from model
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML logistic regression resources using model to test "<test>" with <operating_point> as a batch prediction and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        print(self.test_scenario07.__doc__)
        headers = ["scenario", "kwargs", "test", "output", "predictions_file",
                   "operating_point"]
        examples = [
            ['scenario1_lr', '{"data": "data/iris.csv",' +
             ' "output": "scenario1_lr/predictions.csv",' +
             ' "test": "data/test_iris.csv"}', 'data/test_iris.csv',
             'scenario6_lr/predictions_p.csv',
             'check_files/predictions_iris_lr_op_prob.csv',
             'data/operating_point_prob.json']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            lr_pred.i_create_lr_resources_from_model_with_op(
                self, test=example["test"], output=example["output"],
                operating_point=example["operating_point"])
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])
