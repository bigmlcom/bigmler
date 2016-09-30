# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2016 BigML
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
from __future__ import absolute_import


from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, teardown_class)


import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.basic_logistic_r_steps as lr_pred
import bigmler.tests.evaluation_steps as evaluation



def setup_module():
    """Setup for the module

    """
    common_setup_module()
    test = TestEvaluation()
    test.setup_scenario1()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()


class TestEvaluation(object):

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
            Scenario: Successfully building evaluations from start:
                Given I create BigML resources uploading train "<data>" file to evaluate and log evaluation in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the model has been created
                And I check that the evaluation has been created
                Then the evaluation file is like "<json_evaluation_file>"

                Examples:
                | data             | output                   | json_evaluation_file    |
                | ../data/iris.csv | ./scenario_e1/evaluation | ./check_files/evaluation_iris.json |
        """
        print self.setup_scenario1.__doc__
        examples = [
            ['data/iris.csv', 'scenario_e1/evaluation', 'check_files/evaluation_iris.json']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_create_all_resources_to_evaluate(self, data=example[0], output=example[1])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_pred.i_check_create_evaluation(self)
            evaluation.then_the_evaluation_file_is_like(self, example[2])

    def test_scenario2(self):
        """
            Scenario: Successfully building evaluations from source
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using source to evaluate and log evaluation in "<output>"
                And I check that the dataset has been created
                And I check that the model has been created
                And I check that the evaluation has been created
                Then the evaluation file is like "<json_evaluation_file>"

                Examples:
                |scenario    | kwargs                                                  | output                   | json_evaluation_file    |
                | scenario_e1| {"data": "../data/iris.csv", "output": "./scenario_e1/predictions.csv"}   |./scenario_e2/evaluation | ./check_files/evaluation_iris.json |
        """
        print self.test_scenario2.__doc__
        examples = [
            ['scenario_e1', '{"data": "data/iris.csv", "output": "scenario_e1/predictions.csv"}', 'scenario_e2/evaluation', 'check_files/evaluation_iris.json']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            evaluation.given_i_create_bigml_resources_using_source_to_evaluate(self, output=example[2])
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_pred.i_check_create_evaluation(self)
            evaluation.then_the_evaluation_file_is_like(self, example[3])

    def test_scenario3(self):
        """
            Scenario: Successfully building evaluations from dataset
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using dataset to evaluate and log evaluation in "<output>"
                And I check that the model has been created
                And I check that the evaluation has been created
                Then the evaluation file is like "<json_evaluation_file>"

                Examples:
                |scenario    | kwargs                                                                    |output                   | json_evaluation_file    |
                | scenario_e1| {"data": "../data/iris.csv", "output": "./scenario_e1/predictions.csv"}   |./scenario_e3/evaluation | ./check_files/evaluation_iris.json |

        """
        print self.test_scenario3.__doc__
        examples = [
            ['scenario_e1', '{"data": "data/iris.csv", "output": "scenario_e1/predictions.csv"}', 'scenario_e3/evaluation', 'check_files/evaluation_iris.json']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            evaluation.given_i_create_bigml_resources_using_dataset_to_evaluate(self, output=example[2])
            test_pred.i_check_create_model(self)
            test_pred.i_check_create_evaluation(self)
            evaluation.then_the_evaluation_file_is_like(self, example[3])

    def test_scenario4(self):
        """
            Scenario: Successfully building evaluation from model and test file
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using test file "<test>" to evaluate a model and log evaluation in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the evaluation has been created
                Then the evaluation file is like "<json_evaluation_file>"

                Examples:
                |scenario    | kwargs                                                   | test             | output                   | json_evaluation_file     |
                | scenario_e1| {"data": "../data/iris.csv", "output": "./scenario_e1/predictions.csv"}   | ../data/iris.csv | ./scenario_e4/evaluation | ./check_files/evaluation_iris2.json |
        """
        print self.test_scenario4.__doc__
        examples = [
            ['scenario_e1', '{"data": "data/iris.csv", "output": "scenario_e1/predictions.csv"}', 'data/iris.csv', 'scenario_e4/evaluation', 'check_files/evaluation_iris2.json']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            evaluation.i_create_all_resources_to_evaluate_with_model(self, data=example[2], output=example[3])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_evaluation(self)
            evaluation.then_the_evaluation_file_is_like(self, example[4])

    def test_scenario5(self):
        """
            Scenario: Successfully building evaluation from model and test file with data map
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using test file "<test>" and a fields map "<fields_map>" to evaluate a model and log evaluation in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the evaluation has been created
                Then the evaluation file is like "<json_evaluation_file>"

                Examples:
                |scenario    | kwargs                                                                   | test             | fields_map | output                   | json_evaluation_file     |
                | scenario_e1| {"data": "../data/iris.csv", "output": "./scenario_e1/predictions.csv"}  | ../data/iris_permuted.csv | ../data/fields_map.csv | ./scenario_e7/evaluation | ./check_files/evaluation_iris2.json |
        """
        print self.test_scenario5.__doc__
        examples = [
            ['scenario_e1', '{"data": "data/iris.csv", "output": "scenario_e1/predictions.csv"}', 'data/iris_permuted.csv', 'data/fields_map.csv', 'scenario_e7/evaluation', 'check_files/evaluation_iris2.json']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            evaluation.i_create_all_resources_to_evaluate_with_model_and_map(self, data=example[2], fields_map=example[3], output=example[4])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_evaluation(self)
            evaluation.then_the_evaluation_file_is_like(self, example[5])

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

                Examples:
                | data             | output                   | split    | key         | value |
                | ../data/iris.csv | ./scenario_e6/evaluation | 0.2      | average_phi | 0.85  |
        """
        print self.test_scenario6.__doc__
        examples = [
            ['data/iris.csv', 'scenario_e6/evaluation', '0.2', 'average_phi', '0.85']]
        for example in examples:
            print "\nTesting with:\n", example
            evaluation.i_create_with_split_to_evaluate(self, data=example[0], split=example[2], output=example[1])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_dataset(self, suffix='train ')
            test_pred.i_check_create_dataset(self, suffix='test ')
            test_pred.i_check_create_model(self)
            test_pred.i_check_create_evaluation(self)
            evaluation.i_check_evaluation_key(self, key=example[3], value=example[4])


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

                Examples:
                | data             | output                   | split    | number_of_models | key         | value | directory      | output2
                | ../data/iris.csv | ./scenario_e8/evaluation | 0.2      | 5                | average_phi | 0.94  | ./scenario_e8/ | ./scenario_e9/evaluation
        """
        print self.test_scenario7.__doc__
        examples = [
            ['data/iris.csv', 'scenario_e8/evaluation', '0.2', '5', 'average_phi', '0.94', 'scenario_e8', 'scenario_e9/evaluation']]
        for example in examples:
            print "\nTesting with:\n", example
            evaluation.i_create_with_split_to_evaluate_ensemble(self, data=example[0], number_of_models=example[3], split=example[2], output=example[1])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_dataset(self, suffix='train ')
            test_pred.i_check_create_dataset(self, suffix='test ')
            test_pred.i_check_create_ensemble(self)
            test_pred.i_check_create_evaluation(self)
            evaluation.i_check_evaluation_key(self, key=example[4], value=example[5])
            evaluation.i_evaluate_ensemble_with_dataset(self, ensemble_dir=example[6], dataset_dir=example[6], output=example[7])
            test_pred.i_check_create_evaluation(self)
            evaluation.i_check_evaluation_key(self, key=example[4], value=example[5])


    def test_scenario8(self):
        """
            Scenario: Successfully building evaluations for logistic regression from start:
                Given I create BigML logistic regression resources uploading train "<data>" file to evaluate and log evaluation in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the logistic regression has been created
                And I check that the evaluation has been created
                Then the evaluation file is like "<json_evaluation_file>"

                Examples:
                | data             | output                   | json_evaluation_file    |
                | ../data/iris.csv | ./scenario_e8/evaluation | ./check_files/evaluation_iris_lr.json |
        """
        print self.test_scenario8.__doc__
        examples = [
            ['data/iris.csv', 'scenario_e8/evaluation', 'check_files/evaluation_iris_lr.json']]
        for example in examples:
            print "\nTesting with:\n", example
            lr_pred.i_create_all_lr_resources_to_evaluate(self, data=example[0], output=example[1])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            lr_pred.i_check_create_lr_model(self)
            test_pred.i_check_create_evaluation(self)
            evaluation.then_the_evaluation_file_is_like(self, example[2])
