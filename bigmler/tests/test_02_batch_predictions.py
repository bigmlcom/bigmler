# -*- coding: utf-8 -*-
#
# Copyright 2014-2017 BigML
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
from __future__ import absolute_import


from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, teardown_class)

import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.basic_batch_tst_prediction_steps as test_batch_pred
import bigmler.tests.basic_anomaly_prediction_steps as anomaly_pred



def setup_module():
    """Setup for the module

    """
    common_setup_module()
    test = TestBatchPrediction()
    test.setup_scenario2()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()


class TestBatchPrediction(object):

    def teardown(self):
        """Calling generic teardown for every method

        """
        teardown_class()
        print "\nEnd of tests in: %s\n-------------------\n" % __name__

    def setup(self):
        """Debug information

        """
        print "\n-------------------\nTests in: %s\n" % __name__

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

                Examples:
                | data               | test                    | fields_map | output                        |predictions_file           |
                | ../data/grades.csv | ../data/test_grades.csv | ../data/grades_fields_map.csv | ./scenario_r1_r/predictions.csv | ./check_files/predictions_grades.csv |
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/grades.csv', 'data/test_grades.csv', 'data/grades_fields_map.csv', 'scenario_r1_r/predictions.csv', 'check_files/predictions_grades.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_create_all_resources_batch_map(self, data=example[0], test=example[1], fields_map=example[2], output=example[3])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_batch_pred.i_check_create_test_source(self)
            test_batch_pred.i_check_create_test_dataset(self)
            test_batch_pred.i_check_create_batch_prediction(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[4])

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

                Examples:
                | data               | test                    | output                        |predictions_file           |
                | ../data/iris.csv   | ../data/test_iris.csv   | ./scenario_r1/predictions.csv   | ./check_files/predictions_iris.csv   |
        """
        print self.setup_scenario2.__doc__
        examples = [
            ['data/iris.csv', 'data/test_iris.csv', 'scenario_r1/predictions.csv', 'check_files/predictions_iris.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_create_all_resources_batch(self, data=example[0], test=example[1], output=example[2])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_batch_pred.i_check_create_test_source(self)
            test_batch_pred.i_check_create_test_dataset(self)
            test_batch_pred.i_check_create_batch_prediction(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[3])

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

                Examples:
                |scenario    | kwargs                                                    | output                        |predictions_file           |
                | scenario_r1| {"data": "../data/iris.csv", "output": "./scenario_r1/predictions.csv", "test": "../data/test_iris.csv"}   |./scenario_r2/predictions.csv   | ./check_files/predictions_iris.csv   |
        """

        print self.test_scenario3.__doc__
        examples = [
            ['scenario_r1', '{"data": "data/iris.csv", "output": "scenario_r1/predictions.csv", "test": "data/test_iris.csv"}', 'scenario_r2/predictions.csv', 'check_files/predictions_iris.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            test_pred.i_create_resources_from_source_batch(self, output=example[2])
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_batch_pred.i_check_create_test_dataset(self)
            test_batch_pred.i_check_create_batch_prediction(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[3])

    def test_scenario4(self):
        """
            Scenario 4: Successfully building test predictions from dataset
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using dataset to test the previous test dataset remotely and log predictions in "<output>"
                And I check that the model has been created
                And I check that the batch prediction has been created
                And I check that the predictions are ready
                Then the local prediction file is like "<predictions_file>"

                Examples:
                |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
                | scenario_r1| {"data": "../data/iris.csv", "output": "./scenario_r1/predictions.csv", "test": "../data/test_iris.csv"}   | ../data/test_iris.csv   | ./scenario_r3/predictions.csv   | ./check_files/predictions_iris.csv   |

        """

        print self.test_scenario4.__doc__
        examples = [
            ['scenario_r1', '{"data": "data/iris.csv", "output": "scenario_r1/predictions.csv", "test": "data/test_iris.csv"}', 'scenario_r3/predictions.csv', 'check_files/predictions_iris.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            test_pred.i_create_resources_from_dataset_batch(self, output=example[2])
            test_pred.i_check_create_model(self)
            test_batch_pred.i_check_create_batch_prediction(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[3])

    def test_scenario5(self):
        """
            Scenario 5: Successfully building test predictions from dataset and prediction format info
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using a model to test the previous test dataset remotely with prediction headers and fields "<fields>" and log predictions in "<output>"
                And I check that the batch prediction has been created
                And I check that the predictions are ready
                Then the local prediction file is like "<predictions_file>"

                Examples:
                |scenario    | kwargs                                                  | fields | output                        |predictions_file           |
                | scenario_r1| {"data": "../data/iris.csv", "output": "./scenario_r1/predictions.csv", "test": "../data/test_iris.csv"}   | sepal length,sepal width | ./scenario_r4/predictions.csv   | ./check_files/predictions_iris_format.csv   |

        """

        print self.test_scenario5.__doc__
        examples = [
            ['scenario_r1', '{"data": "data/iris.csv", "output": "scenario_r1/predictions.csv", "test": "data/test_iris.csv"}', 'sepal length,sepal width', 'scenario_r4/predictions.csv', 'check_files/predictions_iris_format.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            test_pred.i_create_resources_from_model_batch(self, fields=example[2], output=example[3])
            test_batch_pred.i_check_create_batch_prediction(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[4])

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

                Examples:
                | data               | test                    | output_dir      |
                | ../data/iris.csv   | ../data/test_iris.csv   | ./scenario_r5   |
        """

        print self.test_scenario6.__doc__
        examples = [
            ['data/iris.csv', 'data/test_iris.csv', 'scenario_r5']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_create_all_resources_batch_to_dataset(self, data=example[0], test=example[1], output_dir=example[2])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_batch_pred.i_check_create_test_source(self)
            test_batch_pred.i_check_create_test_dataset(self)
            test_batch_pred.i_check_create_batch_prediction(self)
            test_batch_pred.i_check_create_batch_predictions_dataset(self)
            anomaly_pred.i_check_no_local_CSV(self)
