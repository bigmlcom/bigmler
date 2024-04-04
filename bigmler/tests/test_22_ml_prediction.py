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


""" Testing Multi-label predictions

"""

from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)

import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.ml_tst_prediction_steps as ml_pred


def setup_module():
    """Setup for the module

    """
    common_setup_module()
    test = TestML()
    test.bigml = {"method": "setup_scenario1"}
    test.setup_scenario1()


def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestML:
    """Test multi labels"""

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
        Scenario: Successfully building multi-label test predictions from start:
            Given I create BigML multi-label resources tagged as "<tag>" with "<label_separator>" label separator and <number_of_labels> labels uploading train "<data>" file with "<training_separator>" field separator to test "<test>" and log predictions in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the models have been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        print(self.setup_scenario1.__doc__)
        headers = ["tag", "label_separator", "number_of_labels", "data",
                   "training_separator", "test", "output", "predictions_file"]
        examples = [
            ['my_multilabel_1', ':', '7', 'data/multilabel.csv', ',',
             'data/test_multilabel.csv', 'scenario_ml_1/predictions.csv',
             'check_files/predictions_ml.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            kwargs = example.copy()
            del kwargs["predictions_file"]
            ml_pred.i_create_all_ml_resources(
                self, **kwargs)
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_pred.i_check_create_models(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario2(self):
        """
        Scenario: Successfully building test predictions from source
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML multi-label resources using source to test "<test>" and log predictions in "<output>"
            And I check that the dataset has been created
            And I check that the models have been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"

            Examples:
            |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
            | scenario_ml_1| {"tag": "my_multilabel_1", "data": "../data/multilabel.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "./scenario_ml_1/predictions.csv", "test": "../data/test_multilabel.csv"}   | ../data/test_multilabel.csv   | ./scenario_ml_2/predictions.csv   | ./check_files/predictions_ml_comma.csv   |
        """
        print(self.test_scenario2.__doc__)
        headers = ["scenario", "kwargs", "test", "output", "predictions_file"]
        examples = [
            ['scenario_ml_1', '{"tag": "my_multilabel_1",' +
             ' "data": "data/multilabel.csv", "label_separator": ":",' +
             ' "number_of_labels": 7, "training_separator": ",",' +
             ' "output": "scenario_ml_1/predictions.csv",' +
             ' "test": "data/test_multilabel.csv"}',
             'data/test_multilabel.csv', 'scenario_ml_2/predictions.csv',
             'check_files/predictions_ml_comma.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_create_resources_from_source(
                self, multi_label='multi-label',
                test=example["test"], output=example["output"])
            test_pred.i_check_create_dataset(self)
            test_pred.i_check_create_models(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario3(self):
        """
        Scenario: Successfully building test predictions from dataset
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML multi-label resources using dataset to test "<test>" and log predictions in "<output>"
            And I check that the models have been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        print(self.test_scenario3.__doc__)
        headers = ["scenario", "kwargs", "test", "output", "predictions_file"]
        examples = [
            ['scenario_ml_1', '{"tag": "my_multilabel_1",' +
             ' "data": "data/multilabel.csv", "label_separator": ":",' +
             ' "number_of_labels": 7, "training_separator": ",",' +
             ' "output": "scenario_ml_1/predictions.csv",' +
             ' "test": "data/test_multilabel.csv"}',
             'data/test_multilabel.csv', 'scenario_ml_3/predictions.csv',
             'check_files/predictions_ml_comma.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_create_resources_from_dataset(
                self, multi_label='multi-label',
                test=example["test"], output=example["output"])
            test_pred.i_check_create_models(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario4(self):
        """
        Scenario: Successfully building test predictions from models file
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML multi-label resources using models in file "<models_file>" to test "<test>" and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        print(self.test_scenario4.__doc__)
        headers = ["scenario", "kwargs", "models_file", "test", "output",
                   "predictions_file"]
        examples = [
            ['scenario_ml_1', '{"tag": "my_multilabel_1",' +
             ' "data": "data/multilabel.csv", "label_separator": ":",' +
             ' "number_of_labels": 7, "training_separator": ",",' +
             ' "output": "scenario_ml_1/predictions.csv",' +
             ' "test": "data/test_multilabel.csv"}', 'scenario_ml_1/models',
             'data/test_multilabel.csv', 'scenario_ml_4/predictions.csv',
             'check_files/predictions_ml_comma.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_create_resources_from_models_file(
                self, multi_label='multi-label',
                models_file=example["models_file"],
                test=example["test"], output=example["output"])
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario5(self):
        """
        Scenario: Successfully building test predictions from models retrieved by tag
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML multi-label resources using models tagged as "<tag>" to test "<test>" and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        print(self.test_scenario5.__doc__)
        headers = ["scenario", "kwargs", "tag", "test", "output",
                   "predictions_file"]
        examples = [
            ['scenario_ml_6', '{"tag": "my_multilabel_5",' +
             ' "data": "data/multilabel.csv", "label_separator": ":",' +
             ' "number_of_labels": 7, "training_separator": ",",' +
             ' "output": "scenario_ml_6/predictions.csv",' +
             ' "test": "data/test_multilabel.csv"}', 'my_multilabel_5',
             'data/test_multilabel.csv', 'scenario_ml_5/predictions.csv',
             'check_files/predictions_ml_comma.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            ml_pred.i_predict_ml_from_model_tag(
                self, tag=example["tag"], test=example["test"],
                output=example["output"])
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario6(self):
        """
        Scenario: Successfully building test predictions from models retrieved by tag
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML multi-label resources with labels "<labels>" using models tagged as "<tag>" to test "<test>" and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        print(self.test_scenario6.__doc__)
        headers = ["scenario", "kwargs", "labels", "tag", "test", "output",
                   "predictions_file"]
        examples = [
            ['scenario_ml_6', '{"tag": "my_multilabel_5",' +
             ' "data": "data/multilabel.csv", "label_separator": ":",' +
             ' "number_of_labels": 7, "training_separator": ",",' +
             ' "output": "scenario_ml_6/predictions.csv",' +
             ' "test": "data/test_multilabel.csv"}', 'Adult,Student',
             'my_multilabel_5', 'data/test_multilabel.csv',
             'scenario_ml_7/predictions.csv',
             'check_files/predictions_ml_labels.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            ml_pred.i_predict_ml_from_model_tag_with_labels(
                self, labels=example["labels"], tag=example["tag"],
                test=example["test"], output=example["output"])
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])
