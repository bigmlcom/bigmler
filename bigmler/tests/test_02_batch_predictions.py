# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#pylint: disable=locally-disabled,invalid-name
#
# Copyright 2014-2024 BigML
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

""" Testing batch prediction creation

"""
from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)

import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.basic_batch_tst_prediction_steps as test_batch_pred
import bigmler.tests.basic_anomaly_prediction_steps as anomaly_pred


def setup_module():
    """Setup for the module

    """
    common_setup_module()
    test = TestBatchPrediction()
    test.bigml = {"method": "setup_scenario2"}
    test.setup_scenario2()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()


class TestBatchPrediction:
    """Testing batch prediction commands"""

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
            Scenario 1: Successfully building test predictions from scratch:
                Given I create BigML resources uploading train "<data>" file to test "<test>" remotely with mapping file "<fields_map>" and log predictions in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the model has been created
                And I check that the source has been created from the test file
                And I check that the dataset has been created from the test file
                And I check that the batch prediction has been created
                And I check that the predictions are ready
                Then the local prediction file is like "<predictions_file>"

        """
        print(self.test_scenario1.__doc__)
        headers = ["data", "test", "fields_map", "output", "predictions_file"]
        examples = [
            ['data/grades.csv', 'data/test_grades.csv',
             'data/grades_fields_map.csv', 'scenario_r1_r/predictions.csv',
             'check_files/predictions_grades.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_all_resources_batch_map(
                self, data=example["data"], test=example["test"],
                fields_map=example["fields_map"], output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_batch_pred.i_check_create_test_source(self)
            test_batch_pred.i_check_create_test_dataset(self)
            test_batch_pred.i_check_create_batch_prediction(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def setup_scenario2(self):
        """
            Scenario 2: Successfully building test predictions from scratch:
                Given I create BigML resources uploading train "<data>" file to test "<test>" remotely and log predictions in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the model has been created
                And I check that the source has been created from the test file
                And I check that the dataset has been created from the test file
                And I check that the batch prediction has been created
                And I check that the predictions are ready
                Then the local prediction file is like "<predictions_file>"
        """
        print(self.setup_scenario2.__doc__)
        headers = ["data", "test", "output", "predictions_file"]
        examples = [
            ['data/iris.csv', 'data/test_iris.csv',
             'scenario_r1/predictions.csv',
             'check_files/predictions_iris.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_all_resources_batch(
                self, data=example["data"], test=example["test"],
                output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_batch_pred.i_check_create_test_source(self)
            test_batch_pred.i_check_create_test_dataset(self)
            test_batch_pred.i_check_create_batch_prediction(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario3(self):
        """
            Scenario 3: Successfully building test predictions from source
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using source to test the previous test source remotely and log predictions in "<output>"
                And I check that the dataset has been created
                And I check that the model has been created
                And I check that the dataset has been created from the test file
                And I check that the batch prediction has been created
                And I check that the predictions are ready
                Then the local prediction file is like "<predictions_file>"
        """

        print(self.test_scenario3.__doc__)
        headers = ["scenario", "kwargs", "output", "predictions_file"]
        examples = [
            ['scenario_r1', '{"data": "data/iris.csv",' +
             ' "output": "scenario_r1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}',
             'scenario_r2/predictions.csv',
             'check_files/predictions_iris.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_create_resources_from_source_batch(
                self, output=example["output"])
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_batch_pred.i_check_create_test_dataset(self)
            test_batch_pred.i_check_create_batch_prediction(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario4(self):
        """
            Scenario 4: Successfully building test predictions from dataset
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using dataset to test the previous test dataset remotely and log predictions in "<output>"
                And I check that the model has been created
                And I check that the batch prediction has been created
                And I check that the predictions are ready
                Then the local prediction file is like "<predictions_file>"
        """

        print(self.test_scenario4.__doc__)
        headers = ["scenario", "kwargs", "output", "predictions_file"]
        examples = [
            ['scenario_r1', '{"data": "data/iris.csv",' +
             ' "output": "scenario_r1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}',
             'scenario_r3/predictions.csv',
             'check_files/predictions_iris.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_create_resources_from_dataset_batch(
                self, output=example["output"])
            test_pred.i_check_create_model(self)
            test_batch_pred.i_check_create_batch_prediction(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario5(self):
        """
            Scenario 5: Successfully building test predictions from dataset and prediction format info
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using a model to test the previous test dataset remotely with prediction headers and fields "<fields>" and log predictions in "<output>"
                And I check that the batch prediction has been created
                And I check that the predictions are ready
                Then the local prediction file is like "<predictions_file>"
        """

        print(self.test_scenario5.__doc__)
        headers = ["scenario", "kwargs", "fields", "output",
            "predictions_file"]
        examples = [
            ['scenario_r1', '{"data": "data/iris.csv",' +
             ' "output": "scenario_r1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}',
             'sepal length,sepal width',
             'scenario_r4/predictions.csv',
             'check_files/predictions_iris_format.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_create_resources_from_model_batch(
                self, fields=example["fields"], output=example["output"])
            test_batch_pred.i_check_create_batch_prediction(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario6(self):
        """
            Scenario 6: Successfully building remote test predictions from scratch to a dataset:
                Given I create BigML resources uploading train "<data>" file to test "<test>" remotely to a dataset with no CSV output and log resources in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the model has been created
                And I check that the source has been created from the test file
                And I check that the dataset has been created from the test file
                And I check that the batch prediction has been created
                Then I check that the batch predictions dataset exists
                And no local CSV file is created
        """

        print(self.test_scenario6.__doc__)
        headers = ["data", "test", "output_dir"]
        examples = [
            ['data/iris.csv', 'data/test_iris.csv', 'scenario_r5']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_all_resources_batch_to_dataset(
                self, data=example["data"], test=example["test"],
                output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_batch_pred.i_check_create_test_source(self)
            test_batch_pred.i_check_create_test_dataset(self)
            test_batch_pred.i_check_create_batch_prediction(self)
            test_batch_pred.i_check_create_batch_predictions_dataset(self)
            anomaly_pred.i_check_no_local_csv(self)

    def test_scenario7(self):
        """
        Scenario: Successfully building test predictions from model with operating point
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML resources using model with operating point "<operating_point>" to test "<test>" and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        headers = ["scenario", "kwargs", "test", "output",
            "predictions_file", "operating_point"]
        examples = [
            ['scenario_r1', '{"data": "data/iris.csv",' +
             ' "output": "scenario_r1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}',
             'data/test_iris.csv', 'scenario_r7/predictions_p.csv', 'check_files/predictions_iris_op_prob.csv', "data/operating_point_prob.json"],
            ['scenario_r1', '{"data": "data/iris.csv",' +
             ' "output": "scenario_r1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}', 'data/test_iris.csv',
             'scenario_r7/predictions_c.csv',
             'check_files/predictions_iris_op_conf.csv',
             "data/operating_point_conf.json"]]

        print(self.test_scenario7.__doc__)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_batch_pred.i_create_resources_from_model_with_op_remote(
                self, operating_point=example["operating_point"],
                test=example["test"], output=example["output"])
            test_batch_pred.i_check_create_batch_prediction(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"],
                                          headers=True)

    def test_scenario8(self):
        """
        Scenario: Successfully building test predictions from model with operating point
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML remote batch predictions one by one using model to test "<test>" and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        headers = ["scenario", "kwargs", "test", "output",
            "predictions_file"]
        examples = [
            ['scenario_r1', '{"data": "data/iris.csv",' +
             ' "output": "scenario_r1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}', 'data/test_iris.csv',
             'scenario_r8/predictions.csv',
             'check_files/predictions_iris.csv']]

        print(self.test_scenario8.__doc__)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it( \
                self, example["scenario"], example["kwargs"])
            test_batch_pred.i_create_resources_from_model_remote_no_batch( \
                self, test=example["test"], output=example["output"])
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"],
                                          headers=True)
