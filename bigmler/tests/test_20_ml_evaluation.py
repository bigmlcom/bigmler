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


""" Testing Multi-label evaluations

"""
from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)

import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.ml_tst_evaluation_steps as ml_eval
import bigmler.tests.evaluation_steps as evaluation


def setup_module():
    """Setup for the module

    """
    common_setup_module()
    test = TestMLEvaluation()
    test.bigml = {"method": "setup_scenario1"}
    test.setup_scenario1()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestMLEvaluation:
    """Test multi-label evaluation """

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
        Scenario: Successfully building multi-label evaluations from scratch
            Given I create BigML multi-label resources tagged as "<tag>" with "<label_separator>" label separator and "<number_of_labels>" labels uploading train "<data>" file with "<training_separator>" field separator to evaluate and log evaluation in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the models have been created
            And I check that the <number_of_labels> evaluations have been created
            And I check that the evaluation is ready
            Then the evaluation file is like "<json_evaluation_file>"
        """
        print(self.setup_scenario1.__doc__)
        headers = ["tag", "label_separator", "number_of_labels", "data",
                   "training_separator", "output", "json_evaluation_file"]
        examples = [
            ['my_multilabel_e_1', ':', '7', 'data/multilabel.csv', ',',
             'scenario_ml_e1/evaluation', 'check_files/evaluation_ml.json']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            ml_eval.i_create_all_ml_evaluations(
                self, tag=example["tag"],
                label_separator=example["label_separator"],
                number_of_labels=example["number_of_labels"],
                data=example["data"],
                training_separator=example["training_separator"],
                output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_pred.i_check_create_models(self)
            test_pred.i_check_create_evaluations(
                self, number_of_evaluations=example["number_of_labels"])
            ml_eval.i_check_evaluation_ready(self)
            evaluation.then_the_evaluation_file_is_like(
                self, example["json_evaluation_file"])

    def test_scenario2(self):
        """
        Scenario: Successfully building multi-label evaluations from source
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML multi-label resources using source to evaluate and log evaluation in "<output>"
            And I check that the dataset has been created
            And I check that the models have been created
            And I check that the <number_of_labels> evaluations have been created
            And I check that the evaluation is ready
            Then the evaluation file is like "<json_evaluation_file>"
        """
        print(self.test_scenario2.__doc__)
        headers = ["scenario", "kwargs", "number_of_labels", "output",
                   "json_evaluation_file"]
        examples = [
            ['scenario_ml_e1', '{"tag": "my_multilabel_e_1",' +
             ' "data": "data/multilabel.csv", "label_separator": ":",' +
             ' "number_of_labels": 7, "training_separator": ",",' +
             ' "output": "scenario_ml_e1/evaluation"}', '7',
             'scenario_ml_e2/evaluation', 'check_files/evaluation_ml.json']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            ml_eval.i_create_ml_evaluations_from_source(
                self, output=example["output"])
            test_pred.i_check_create_dataset(self)
            test_pred.i_check_create_models(self)
            test_pred.i_check_create_evaluations(
                self, number_of_evaluations=example["number_of_labels"])
            ml_eval.i_check_evaluation_ready(self)
            evaluation.then_the_evaluation_file_is_like(
                self, example["json_evaluation_file"])

    def test_scenario3(self):
        """
        Scenario: Successfully building multi-label evaluations from dataset
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML multi-label resources using dataset to evaluate and log evaluation in "<output>"
            And I check that the models have been created
            And I check that the <number_of_labels> evaluations have been created
            And I check that the evaluation is ready
            Then the evaluation file is like "<json_evaluation_file>"
        """
        print(self.test_scenario3.__doc__)
        headers = ["scenario", "kwargs", "number_of_labels", "output",
                   "json_evaluation_file"]
        examples = [
            ['scenario_ml_e1', '{"tag": "my_multilabel_e_1",' +
             ' "data": "data/multilabel.csv", "label_separator": ":",' +
             ' "number_of_labels": 7, "training_separator": ",",' +
             ' "output": "scenario_ml_e1/evaluation"}', '7',
             'scenario_ml_e3/evaluation', 'check_files/evaluation_ml.json']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            ml_eval.i_create_ml_evaluations_from_dataset(
                self, output=example["output"])
            test_pred.i_check_create_models(self)
            test_pred.i_check_create_evaluations(
                self, number_of_evaluations=example["number_of_labels"])
            ml_eval.i_check_evaluation_ready(self)
            evaluation.then_the_evaluation_file_is_like(
                self, example["json_evaluation_file"])

    def test_scenario4(self):
        """
        Scenario: Successfully building multi-label evaluations from models file
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML multi-label resources using models in file "<models_file>" to evaluate and log evaluation in "<output>"
            And I check that the <number_of_labels> evaluations have been created
            And I check that the evaluation is ready
            Then the evaluation key "<key>" value for the model is greater than <value>
        """
        print(self.test_scenario4.__doc__)
        headers = ["scenario", "kwargs", "models_file", "number_of_labels",
                   "output", "key", "value"]
        examples = [
            ['scenario_ml_e1', '{"tag": "my_multilabel_e_1",' +
             ' "data": "data/multilabel.csv", "label_separator": ":",' +
             ' "number_of_labels": 7, "training_separator": ",",' +
             ' "output": "scenario_ml_e1/evaluation"}',
             'scenario_ml_e1/models', '7', 'scenario_ml_e4/evaluation',
             'average_phi', '0.8180']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            ml_eval.i_create_ml_evaluations_from_models(
                self, models_file=example["models_file"],
                output=example["output"])
            test_pred.i_check_create_evaluations(
                self, number_of_evaluations=example["number_of_labels"])
            ml_eval.i_check_evaluation_ready(self)
            evaluation.i_check_evaluation_key(
                self, key=example["key"], value=example["value"])

    def test_scenario5(self):
        """
        Scenario: Successfully building multi-label evaluations from models retrieved by tag
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML multi-label resources using models tagged as "<tag>" to evaluate and log evaluation in "<output>"
            And I check that the <number_of_labels> evaluations have been created
            And I check that the evaluation is ready
            Then the evaluation key "<key>" value for the model is greater than <value>
        """
        print(self.test_scenario5.__doc__)
        headers = ["scenario", "kwargs", "tag", "number_of_labels", "output",
                   "key", "value"]
        examples = [
            ['scenario_ml_e1', '{"tag": "my_multilabel_e_1",' +
             ' "data": "data/multilabel.csv", "label_separator": ":",' +
             ' "number_of_labels": 7, "training_separator": ",",' +
             ' "output": "scenario_ml_e1/evaluation"}', 'my_multilabel_e_1' ,
             '7', 'scenario_ml_e5/evaluation', 'average_phi', '0.8180']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            ml_eval.i_create_ml_evaluations_from_tagged_models(
                self, tag=example["tag"], output=example["output"])
            test_pred.i_check_create_evaluations(
                self, number_of_evaluations=example["number_of_labels"])
            ml_eval.i_check_evaluation_ready(self)
            evaluation.i_check_evaluation_key(
                self, key=example["key"], value=example["value"])
