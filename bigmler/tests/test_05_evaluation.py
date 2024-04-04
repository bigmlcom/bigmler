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


""" Testing evaluations' creation

"""
from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)


import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.basic_logistic_r_steps as lr_pred
import bigmler.tests.evaluation_steps as evaluation
import bigmler.tests.basic_time_series_steps as ts_pred
import bigmler.tests.basic_deepnet_steps as dn_pred


def setup_module():
    """Setup for the module

    """
    common_setup_module()
    test = TestEvaluation()
    test.bigml = {"method": "setup_scenario1"}
    test.setup_scenario1()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()


class TestEvaluation:
    """Testing evaluation commands"""

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

    def setup_scenario1(self):
        """
            Scenario: Successfully building evaluations from start:
                Given I create BigML resources uploading train "<data>" file to evaluate and log evaluation in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the model has been created
                And I check that the evaluation has been created
                Then the evaluation file is like "<json_evaluation_file>"|
        """
        print(self.setup_scenario1.__doc__)
        headers = ["data", "output", "json_evaluation_file"]
        examples = [
            ['data/iris.csv', 'scenario_e1/evaluation',
             'check_files/evaluation_iris.json']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_all_resources_to_evaluate(
                self, data=example["data"], output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_pred.i_check_create_evaluation(self)
            evaluation.then_the_evaluation_file_is_like(
                self, example["json_evaluation_file"])

    def test_scenario2(self):
        """
            Scenario: Successfully building evaluations from source
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using source to evaluate and log evaluation in "<output>"
                And I check that the dataset has been created
                And I check that the model has been created
                And I check that the evaluation has been created
                Then the evaluation file is like "<json_evaluation_file>"
        """
        print(self.test_scenario2.__doc__)
        headers = ["scenario", "kwargs", "output", "json_evaluation_file"]
        examples = [
            ['scenario_e1', '{"data": "data/iris.csv",' +
             ' "output": "scenario_e1/predictions.csv"}',
             'scenario_e2/evaluation', 'check_files/evaluation_iris.json']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            evaluation.given_i_create_bigml_resources_using_source_to_evaluate(
                self, output=example["output"])
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_pred.i_check_create_evaluation(self)
            evaluation.then_the_evaluation_file_is_like(
                self, example["json_evaluation_file"])

    def test_scenario3(self):
        """
            Scenario: Successfully building evaluations from dataset
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using dataset to evaluate and log evaluation in "<output>"
                And I check that the model has been created
                And I check that the evaluation has been created
                Then the evaluation file is like "<json_evaluation_file>"
        """
        print(self.test_scenario3.__doc__)
        headers = ["scenario", "kwargs", "output", "json_evaluation_file"]
        examples = [
            ['scenario_e1', '{"data": "data/iris.csv",' +
             ' "output": "scenario_e1/predictions.csv"}',
             'scenario_e3/evaluation', 'check_files/evaluation_iris.json']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            evaluation.given_i_create_bigml_resources_using_dataset_to_evaluate(
                self, output=example["output"])
            test_pred.i_check_create_model(self)
            test_pred.i_check_create_evaluation(self)
            evaluation.then_the_evaluation_file_is_like(
                self, example["json_evaluation_file"])

    def test_scenario4(self):
        """
            Scenario: Successfully building evaluation from model and test file
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using test file "<test>" to evaluate a model and log evaluation in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the evaluation has been created
                Then the evaluation file is like "<json_evaluation_file>"
        """
        print(self.test_scenario4.__doc__)
        headers = ["scenario", "kwargs", "data", "output", "json_evaluation_file"]
        examples = [
            ['scenario_e1', '{"data": "data/iris.csv",' +
             ' "output": "scenario_e1/predictions.csv"}',
             'data/iris.csv', 'scenario_e4/evaluation',
             'check_files/evaluation_iris2.json']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            evaluation.i_create_all_resources_to_evaluate_with_model(
                self, data=example["data"], output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_evaluation(self)
            evaluation.then_the_evaluation_file_is_like(
                self, example["json_evaluation_file"])

    def test_scenario5(self):
        """
            Scenario: Successfully building evaluation from model and test file with data map
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using test file "<test>" and a fields map "<fields_map>" to evaluate a model and log evaluation in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the evaluation has been created
                Then the evaluation file is like "<json_evaluation_file>"
        """
        print(self.test_scenario5.__doc__)
        headers = ["scenario", "kwargs", "test", "fields_map", "output",
                   "json_evaluation_file"]
        examples = [
            ['scenario_e1', '{"data": "data/iris.csv",' +
             ' "output": "scenario_e1/predictions.csv"}',
             'data/iris_permuted.csv', 'data/fields_map.csv',
             'scenario_e7/evaluation', 'check_files/evaluation_iris2.json']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            evaluation.i_create_all_resources_to_evaluate_with_model_and_map(
                self, data=example["test"], fields_map=example["fields_map"],
                output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_evaluation(self)
            evaluation.then_the_evaluation_file_is_like(
                self, example["json_evaluation_file"])

    def test_scenario6(self):
        """
            Scenario: Successfully building evaluations from start and test-split:
                Given I create BigML resources uploading train "<data>" file to evaluate with test-split <split> and log evaluation in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the train dataset has been created
                And I check that the test dataset has been created
                And I check that the model has been created
                And I check that the evaluation has been created
                Then the evaluation key "<key>" value for the model is greater than <value>
        """
        print(self.test_scenario6.__doc__)
        headers = ["data", "output", "split", "key", "value"]
        examples = [
            ['data/iris.csv', 'scenario_e6/evaluation', '0.2', 'average_phi', '0.85']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            evaluation.i_create_with_split_to_evaluate(
                self, data=example["data"], split=example["split"],
                output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_dataset(self, suffix='train ')
            test_pred.i_check_create_dataset(self, suffix='test ')
            test_pred.i_check_create_model(self)
            test_pred.i_check_create_evaluation(self)
            evaluation.i_check_evaluation_key(
                self, key=example["key"], value=example["value"])

    def test_scenario7(self):
        """
            Scenario: Successfully building ensemble evaluations from start and test-split:
                Given I create BigML resources uploading train "<data>" file to evaluate an ensemble of <number_of_models> models with test-split <split> and log evaluation in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the train dataset has been created
                And I check that the test dataset has been created
                And I check that the ensemble has been created
                And I check that the evaluation has been created
                Then the evaluation key "<key>" value for the model is greater than <value>
                And I evaluate the ensemble in directory "<directory>" with the dataset in directory "<directory>" and log evaluation in "<output2>"
                And I check that the evaluation has been created
                Then the evaluation key "<key>" value for the model is greater than <value>
        """
        print(self.test_scenario7.__doc__)
        headers = ["data", "output", "split", "number_of_models", "key",
                   "value", "directory", "output2"]
        examples = [
            ['data/iris.csv', 'scenario_e8/evaluation', '0.2', '5',
             'average_phi', '0.94', 'scenario_e8', 'scenario_e9/evaluation']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            evaluation.i_create_with_split_to_evaluate_ensemble(
                self, data=example["data"],
                number_of_models=example["number_of_models"],
                split=example["split"], output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_dataset(self, suffix='train ')
            test_pred.i_check_create_dataset(self, suffix='test ')
            test_pred.i_check_create_ensemble(self)
            test_pred.i_check_create_evaluation(self)
            evaluation.i_check_evaluation_key(
                self, key=example["key"], value=example["value"])
            evaluation.i_evaluate_ensemble_with_dataset(
                self, ensemble_dir=example["directory"],
                dataset_dir=example["directory"],
                output=example["output"])
            test_pred.i_check_create_evaluation(self)
            evaluation.i_check_evaluation_key(
                self, key=example["key"], value=example["value"])

    def test_scenario8(self):
        """
            Scenario: Successfully building evaluations for logistic regression from start:
                Given I create BigML logistic regression resources uploading train "<data>" file to evaluate and log evaluation in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the logistic regression has been created
                And I check that the evaluation has been created
                Then the evaluation file is like "<json_evaluation_file>"
        """
        print(self.test_scenario8.__doc__)
        headers = ["data", "output", "json_evaluation_file"]
        examples = [
            ['data/iris.csv', 'scenario_e8/evaluation',
             'check_files/evaluation_iris_lr.json']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            lr_pred.i_create_all_lr_resources_to_evaluate(
                self, data=example["data"], output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            lr_pred.i_check_create_lr_model(self)
            test_pred.i_check_create_evaluation(self)
            evaluation.then_the_evaluation_file_is_like(
                self, example["json_evaluation_file"])

    def test_scenario9(self):
        """
            Scenario: Successfully building ensemble evaluations from start and test-split:
                Given I create BigML resources uploading train "<data>" file to evaluate an ensemble of <number_of_models> models with test-split <split> threshold "<threshold>" and log evaluation in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the train dataset has been created
                And I check that the test dataset has been created
                And I check that the ensemble has been created
                And I check that the evaluation has been created
                Then the evaluation key "<key>" value for the model is greater than <value>
                And I evaluate the ensemble in directory "<directory>" with the dataset in directory "<directory>" and options "<options>" and log evaluation in "<output2>"
                And I check that the evaluation has been created
                Then the evaluation key "<key>" value for the model is greater than <value>
        """
        print(self.test_scenario9.__doc__)
        headers = ["data", "output", "split", "number_of_models", "key",
                   "value", "directory", "output2", "options"]
        examples = [
            ['data/iris.csv', 'scenario_e9/evaluation', '0.2', '5',
             'average_phi', '0.89', 'scenario_e9', 'scenario_e9/evaluation',
             "--method threshold --threshold 5 --class Iris-virginica"]]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            evaluation.i_create_with_split_to_evaluate_ensemble(
                self, data=example["data"],
                number_of_models=example["number_of_models"],
                split=example["split"], output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_dataset(self, suffix='train ')
            test_pred.i_check_create_dataset(self, suffix='test ')
            test_pred.i_check_create_ensemble(self)
            test_pred.i_check_create_evaluation(self)
            evaluation.i_check_evaluation_key(
                self, key=example["key"], value=example["value"])
            evaluation.i_evaluate_ensemble_with_dataset_and_options(
                self, ensemble_dir=example["directory"],
                dataset_dir=example["directory"],
                output=example["output2"], options=example["options"])
            test_pred.i_check_create_evaluation(self)
            evaluation.i_check_evaluation_key(
                self, key=example["key"], value=example["value"])

    def test_scenario10(self):
        """
            Scenario: Successfully building evaluations for time series from start:
                Given I create BigML time series resources uploading train "<data>" file to evaluate and log evaluation in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the time series has been created
                And I check that the evaluation has been created
                Then the evaluation file is like "<json_evaluation_file>"
        """
        print(self.test_scenario10.__doc__)
        headers = ["data", "output", "json_evaluation_file"]
        examples = [
            ['data/grades.csv', 'scenario_e10/evaluation',
             'check_files/evaluation_grades_ts.json']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            ts_pred.i_create_all_ts_resources_to_evaluate(
                self, data=example["data"], output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            ts_pred.i_check_create_time_series(self)
            test_pred.i_check_create_evaluation(self)
            evaluation.then_the_evaluation_file_is_like(
                self, example["json_evaluation_file"])

    def test_scenario11(self):
        """
            Scenario: Successfully building evaluations for deepnets from start:
                Given I create BigML deepnet resources uploading train "<data>" file to evaluate and log evaluation in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the deepnet has been created
                And I check that the evaluation has been created
                Then the evaluation file is like "<json_evaluation_file>"
        """
        print(self.test_scenario11.__doc__)
        headers = ["data", "output", "json_evaluation_file"]
        examples = [
            ['data/iris.csv', 'scenario_e11/evaluation',
             'check_files/evaluation_iris_dn.json']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            dn_pred.i_create_all_dn_resources_to_evaluate(
                self, data=example["data"], output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            dn_pred.i_check_create_dn_model(self)
            test_pred.i_check_create_evaluation(self)
            evaluation.then_the_evaluation_file_is_like(
                self, example["json_evaluation_file"])
