# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2017 BigML
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
from __future__ import absolute_import


from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, teardown_class)

import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.ml_tst_prediction_steps as ml_pred
import bigmler.tests.ml_tst_evaluation_steps as ml_eval
import bigmler.tests.evaluation_steps as evaluation


def setup_module():
    """Setup for the module

    """
    common_setup_module()
    test = TestMLEvaluation()
    test.setup_scenario1()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestMLEvaluation(object):

    def teardown(self):
        """Calling generic teardown for every method

        """
        print "\nEnd of tests in: %s\n-------------------\n" % __name__
        teardown_class()

    def setup(self):
        """
            Debug information
        """
        print "\n-------------------\nTests in: %s\n" % __name__

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

                Examples:
                |tag |label_separator |number_of_labels| data                   |training_separator |  output                          |json_evaluation_file
                |my_multilabel_e_1|:|7| ../data/multilabel.csv |,| ./scenario_ml_e1/evaluation | ./check_files/evaluation_ml.json
        """
        print self.setup_scenario1.__doc__
        examples = [
            ['my_multilabel_e_1', ':', '7', 'data/multilabel.csv', ',', 'scenario_ml_e1/evaluation', 'check_files/evaluation_ml.json']]
        for example in examples:
            print "\nTesting with:\n", example
            ml_eval.i_create_all_ml_evaluations(self, tag=example[0], label_separator=example[1], number_of_labels=example[2], data=example[3], training_separator=example[4], output=example[5])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_pred.i_check_create_models(self)
            test_pred.i_check_create_evaluations(self, number_of_evaluations=example[2])
            ml_eval.i_check_evaluation_ready(self)
            evaluation.then_the_evaluation_file_is_like(self, example[6])

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

                Examples:
                |scenario    | kwargs                                                  | number_of_labels                    | output                        |json_evaluation_file          |
                | scenario_ml_e1| {"tag": "my_multilabel_e_1", "data": "../data/multilabel.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "./scenario_ml_e1/evaluation"}   | 7 | ./scenario_ml_e2/evaluation   | ./check_files/evaluation_ml.json   |
        """
        print self.test_scenario2.__doc__
        examples = [
            ['scenario_ml_e1', '{"tag": "my_multilabel_e_1", "data": "data/multilabel.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "scenario_ml_e1/evaluation"}', '7', 'scenario_ml_e2/evaluation', 'check_files/evaluation_ml.json']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            ml_eval.i_create_ml_evaluations_from_source(self, output=example[3])
            test_pred.i_check_create_dataset(self)
            test_pred.i_check_create_models(self)
            test_pred.i_check_create_evaluations(self, number_of_evaluations=example[2])
            ml_eval.i_check_evaluation_ready(self)
            evaluation.then_the_evaluation_file_is_like(self, example[4])

    def test_scenario3(self):
        """
            Scenario: Successfully building multi-label evaluations from dataset
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML multi-label resources using dataset to evaluate and log evaluation in "<output>"
                And I check that the models have been created
                And I check that the <number_of_labels> evaluations have been created
                And I check that the evaluation is ready
                Then the evaluation file is like "<json_evaluation_file>"

                Examples:
                |scenario    | kwargs                                                  | number_of_labels                    | output                        |json_evaluation_file          |
                | scenario_ml_e1| {"tag": "my_multilabel_e_1", "data": "../data/multilabel.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "./scenario_ml_e1/evaluation"}   | 7 | ./scenario_ml_e3/evaluation   | ./check_files/evaluation_ml.json   |
        """
        print self.test_scenario3.__doc__
        examples = [
            ['scenario_ml_e1', '{"tag": "my_multilabel_e_1", "data": "data/multilabel.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "scenario_ml_e1/evaluation"}', '7', 'scenario_ml_e3/evaluation', 'check_files/evaluation_ml.json']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            ml_eval.i_create_ml_evaluations_from_dataset(self, output=example[3])
            test_pred.i_check_create_models(self)
            test_pred.i_check_create_evaluations(self, number_of_evaluations=example[2])
            ml_eval.i_check_evaluation_ready(self)
            evaluation.then_the_evaluation_file_is_like(self, example[4])

    def test_scenario4(self):
        """
        Scenario: Successfully building multi-label evaluations from models file
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML multi-label resources using models in file "<models_file>" to evaluate and log evaluation in "<output>"
            And I check that the <number_of_labels> evaluations have been created
            And I check that the evaluation is ready
            Then the evaluation key "<key>" value for the model is greater than <value>

            Examples:
            |scenario    | kwargs                                                  | models_file | number_of_labels                    | output                        |key          | value
            | scenario_ml_e1| {"tag": "my_multilabel_e_1", "data": "../data/multilabel.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "./scenario_ml_e1/evaluation"}   | ./scenario_ml_e1/models | 7 | ./scenario_ml_e4/evaluation   | average_phi   | 0.8180
        """
        print self.test_scenario4.__doc__
        examples = [
            ['scenario_ml_e1', '{"tag": "my_multilabel_e_1", "data": "data/multilabel.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "scenario_ml_e1/evaluation"}', 'scenario_ml_e1/models', '7', 'scenario_ml_e4/evaluation', 'average_phi', '0.8180']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            ml_eval.i_create_ml_evaluations_from_models(self, models_file=example[2], output=example[4])
            test_pred.i_check_create_evaluations(self, number_of_evaluations=example[3])
            ml_eval.i_check_evaluation_ready(self)
            evaluation.i_check_evaluation_key(self, key=example[5], value=example[6])

    def test_scenario5(self):
        """
            Scenario: Successfully building multi-label evaluations from models retrieved by tag
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML multi-label resources using models tagged as "<tag>" to evaluate and log evaluation in "<output>"
                And I check that the <number_of_labels> evaluations have been created
                And I check that the evaluation is ready
                Then the evaluation key "<key>" value for the model is greater than <value>

                Examples:
                |scenario    | kwargs                                                  | tag | number_of_labels                    | output                        |key          | value
                | scenario_ml_e1| {"tag": "my_multilabel_e_1", "data": "../data/multilabel.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "./scenario_ml_e1/evaluation"}   | my_multilabel_e_1 | 7 | ./scenario_ml_e5/evaluation   | average_phi   | 0.8180

        """
        print self.test_scenario5.__doc__
        examples = [
            ['scenario_ml_e1', '{"tag": "my_multilabel_e_1", "data": "data/multilabel.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "scenario_ml_e1/evaluation"}', 'my_multilabel_e_1', '7', 'scenario_ml_e5/evaluation', 'average_phi', '0.8180']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            ml_eval.i_create_ml_evaluations_from_tagged_models(self, tag=example[2], output=example[4])
            test_pred.i_check_create_evaluations(self, number_of_evaluations=example[3])
            ml_eval.i_check_evaluation_ready(self)
            evaluation.i_check_evaluation_key(self, key=example[5], value=example[6])
