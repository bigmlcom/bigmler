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


""" Testing Multi-label ensembles

"""
from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)

import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.ml_tst_prediction_steps as ml_pred


def setup_module():
    """Setup for the module

    """
    common_setup_module()
    test = TestMLEnsembles()
    test.bigml = {"method": "setup_scenario1"}
    test.setup_scenario1()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()


class TestMLEnsembles:
    """Testing Multi label Ensembles"""

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
            Given I create BigML multi-label resources tagged as "<tag>" with "<label_separator>" label separator and <number_of_labels> labels uploading train "<data>" file with "<training_separator>" field separator and <number_of_models> models ensembles to test "<test>" and log predictions in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the models in the ensembles have been created
            Then I check that the predictions are ready
        """
        print(self.setup_scenario1.__doc__)
        headers = ["tag", "label_separator", "number_of_labels", "data",
                   "training_separator", "number_of_models", "test", "output"]
        examples = [
            ['my_multilabel_1', ':', '7', 'data/multilabel.csv', ',', '10',
             'data/test_multilabel.csv', 'scenario_mle_1/predictions.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            ml_pred.i_create_all_ml_resources_and_ensembles(
                self, tag=example["tag"],
                label_separator=example["label_separator"],
                number_of_labels=example["number_of_labels"],
                data=example["data"],
                training_separator=example["training_separator"],
                number_of_models=example["number_of_models"],
                test=example["test"], output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_pred.i_check_create_models_in_ensembles(
                self, in_ensemble=True)
            test_pred.i_check_create_predictions(self)

    def test_scenario2(self):
        """
        Scenario: Successfully building test predictions from source
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML multi-label resources using source and <number_of_models> models ensembles to test "<test>" and log predictions in "<output>"
            And I check that the dataset has been created
            And I check that the models in the ensembles have been created
            Then I check that the predictions are ready
        """
        print(self.test_scenario2.__doc__)
        headers = ["scenario", "kwargs", "number_of_models", "test", "output"]
        examples = [
            ['scenario_mle_1', '{"tag": "my_multilabel_1",' +
             ' "data": "data/multilabel.csv", "label_separator": ":",' +
             ' "number_of_labels": 7, "training_separator": ",",' +
             ' "output": "scenario_mle_1/predictions.csv",' +
             ' "test": "data/test_multilabel.csv", "number_of_models": 10}',
             '10', 'data/test_multilabel.csv',
             'scenario_mle_2/predictions.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            ml_pred.i_create_resources_and_ensembles_from_source(
                self, multi_label='multi-label ',
                number_of_models=example["number_of_models"],
                test=example["test"], output=example["output"])
            test_pred.i_check_create_dataset(self)
            test_pred.i_check_create_models_in_ensembles(
                self, in_ensemble=True)
            test_pred.i_check_create_predictions(self)

    def test_scenario3(self):
        """
        Scenario: Successfully building test predictions from dataset
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML multi-label resources using dataset and <number_of_models> models ensembles to test "<test>" and log predictions in "<output>"
            And I check that the models in the ensembles have been created
            Then I check that the predictions are ready
        """
        print(self.test_scenario3.__doc__)
        headers = ["scenario", "kwargs", "number_of_models", "test", "output"]
        examples = [
            ['scenario_mle_1', '{"tag": "my_multilabel_1",' +
             ' "data": "data/multilabel.csv", "label_separator": ":",' +
             ' "number_of_labels": 7, "training_separator": ",",' +
             ' "output": "scenario_mle_1/predictions.csv",' +
             ' "test": "data/test_multilabel.csv", "number_of_models": 10}',
             '10', 'data/test_multilabel.csv',
             'scenario_mle_3/predictions.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            ml_pred.i_create_resources_and_ensembles_from_source(
                self, multi_label='multi-label',
                number_of_models=example["number_of_models"],
                test=example["test"], output=example["output"])
            test_pred.i_check_create_dataset(self)
            test_pred.i_check_create_models_in_ensembles(
                self, in_ensemble=True)
            test_pred.i_check_create_predictions(self)
