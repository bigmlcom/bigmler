# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2016-2020 BigML
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
                                 common_teardown_module,
                                 teardown_class)


import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.basic_batch_tst_prediction_steps as batch_pred
import bigmler.tests.basic_logistic_r_steps as lr_pred

def setup_module():
    """Setup for the module

    """
    common_setup_module()
    test = TestPrediction()
    test.setup_scenario02()


def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()


class TestPrediction(object):

    def setup(self):
        """
            Debug information
        """
        print("\n-------------------\nTests in: %s\n" % __name__)

    def teardown(self):
        """Calling generic teardown for every method

        """
        self.world = teardown_class()
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)

    def test_scenario01(self):
        """
        Scenario: Successfully building logistic regression test predictions from start with no headers:
            Given I create BigML logistic regression resources uploading train "<data>" file with no headers to test "<test>" with no headers and log predictions in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the logistic regression model has been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"

            Examples:
            | data               | test                    | output                        |predictions_file           |
            | ../data/iris_nh.csv   | ../data/test_iris_nh.csv   | ./scenario1_lr_nh/predictions.csv   | ./check_files/predictions_iris_lr.csv   |


        """
        print(self.test_scenario01.__doc__)
        examples = [
            ['data/iris_nh.csv', 'data/test_iris_nh.csv', 'scenario1_lr_nh/predictions.csv', 'check_files/predictions_iris_lr.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            lr_pred.i_create_all_lr_resources_with_no_headers(self, example[0], example[1], example[2])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            lr_pred.i_check_create_lr_model(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[3])

    def setup_scenario02(self):
        """
        Scenario: Successfully building test predictions from start:
            Given I create BigML logistic regression resources uploading train "<data>" file to test "<test>" and log predictions in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the model has been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"

            Examples:
            | data               | test                    | output                        |predictions_file           |
            | ../data/iris.csv   | ../data/test_iris.csv   | ./scenario1_lr/predictions.csv   | ./check_files/predictions_iris_lr.csv   |
        """
        print(self.setup_scenario02.__doc__)
        examples = [
            ['data/iris.csv', 'data/test_iris.csv', 'scenario1_lr/predictions.csv', 'check_files/predictions_iris_lr.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            lr_pred.i_create_all_lr_resources(self, example[0], example[1], example[2])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            lr_pred.i_check_create_lr_model(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[3])

    def test_scenario03(self):
        """
        Scenario: Successfully building test predictions from source
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML logistic regression resources using source to test "<test>" and log predictions in "<output>"
            And I check that the dataset has been created
            And I check that the model has been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"

            Examples:
            |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
            | scenario1| {"data": "../data/iris.csv", "output": "./scenario1_lr/predictions.csv", "test": "../data/test_iris.csv"}   | ../data/test_iris.csv   | ./scenario2/predictions.csv   | ./check_files/predictions_iris.csv   |
        """
        print(self.test_scenario03.__doc__)
        examples = [
            ['scenario1_lr', '{"data": "data/iris.csv", "output": "scenario1_lr/predictions.csv", "test": "data/test_iris.csv"}', 'data/test_iris.csv', 'scenario2_lr/predictions.csv', 'check_files/predictions_iris_lr.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            lr_pred.i_create_lr_resources_from_source(self, None, test=example[2], output=example[3])
            test_pred.i_check_create_dataset(self, suffix=None)
            lr_pred.i_check_create_lr_model(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[4])


    def test_scenario04(self):
        """
        Scenario: Successfully building test predictions from dataset
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML logistic regression resources using dataset to test "<test>" and log predictions in "<output>"
            And I check that the model has been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"

            Examples:
            |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
            | scenario1| {"data": "../data/iris.csv", "output": "./scenario1/predictions.csv", "test": "../data/test_iris.csv"}   | ../data/test_iris.csv   | ./scenario3/predictions.csv   | ./check_files/predictions_iris.csv   |

        """
        print(self.test_scenario04.__doc__)
        examples = [
            ['scenario1_lr', '{"data": "data/iris.csv", "output": "scenario1_lr/predictions.csv", "test": "data/test_iris.csv"}', 'data/test_iris.csv', 'scenario3_lr/predictions.csv', 'check_files/predictions_iris_lr.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            lr_pred.i_create_lr_resources_from_dataset(self, None, test=example[2], output=example[3])
            lr_pred.i_check_create_lr_model(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[4])

    def test_scenario05(self):
        """
        Scenario: Successfully building test predictions from model
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML logistic regression resources using model to test "<test>" and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"

            Examples:
            |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
            | scenario1| {"data": "../data/iris.csv", "output": "./scenario1/predictions.csv", "test": "../data/test_iris.csv"}   | ../data/test_iris.csv   | ./scenario4/predictions.csv   | ./check_files/predictions_iris.csv   |

        """
        print(self.test_scenario05.__doc__)
        examples = [
            ['scenario1_lr', '{"data": "data/iris.csv", "output": "scenario1_lr/predictions.csv", "test": "data/test_iris.csv"}', 'data/test_iris.csv', 'scenario4_lr/predictions.csv', 'check_files/predictions_iris_lr.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            lr_pred.i_create_lr_resources_from_model(self, test=example[2], output=example[3])
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[4])

    def test_scenario06(self):
        """
        Scenario: Successfully building batch test predictions from model
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML logistic regression resources using model to test "<test>" as a batch prediction and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"

            Examples:
            |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
            | scenario1| {"data": "../data/iris.csv", "output": "./scenario1/predictions.csv", "test": "../data/test_iris.csv"}   | ../data/test_iris.csv   | ./scenario4/predictions.csv   | ./check_files/predictions_iris.csv   |

        """
        print(self.test_scenario06.__doc__)
        examples = [
            ['scenario1_lr', '{"data": "data/iris.csv", "output": "scenario1_lr/predictions.csv", "test": "data/test_iris.csv"}', 'data/test_iris.csv', 'scenario5_lr/predictions.csv', 'check_files/predictions_iris_lr.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            lr_pred.i_create_lr_resources_from_model_remote(self, test=example[2], output=example[3])
            batch_pred.i_check_create_batch_prediction(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[4])

    def test_scenario07(self):
        """
        Scenario: Successfully building batch test predictions from model
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML logistic regression resources using model to test "<test>" as a batch prediction and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"

            Examples:
            |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
            | scenario1| {"data": "../data/iris.csv", "output": "./scenario1/predictions.csv", "test": "../data/test_iris.csv"}   | ../data/test_iris.csv   | ./scenario6_lr/predictions.csv   | ./check_files/predictions_iris.csv   |

        """
        print(self.test_scenario07.__doc__)
        examples = [
            ['scenario1_lr', '{"data": "data/iris.csv", "output": "scenario1_lr/predictions.csv", "test": "data/test_iris.csv"}', 'data/test_iris.csv', 'scenario6_lr/predictions_p.csv', 'check_files/predictions_iris_lr_op_prob.csv', 'data/operating_point_prob.json']]
        for example in examples:
            print("\nTesting with:\n", example)
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            lr_pred.i_create_lr_resources_from_model_with_op(self, test=example[2], output=example[3], operating_point=example[5])
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[4])
