# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2020 BigML
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


""" Testing predictions with missing splits

"""



from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, teardown_class)


import bigmler.tests.basic_tst_prediction_steps as test_pred


def setup_module():
    """Setup for the module

    """
    common_setup_module()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestMissingSplits(object):

    def teardown(self):
        """Calling generic teardown for every method

        """
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)
        teardown_class()

    def setup(self):
        """
            Debug information
        """
        print("\n-------------------\nTests in: %s\n" % __name__)

    def test_scenario1(self):
        """
            Scenario: Successfully building test predictions with missing-splits model:
                Given I create BigML resources uploading train "<data>" file to test "<test>" with a missing-splits model and log predictions in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the model has been created
                And I check that the predictions are ready
                Then the local prediction file is like "<predictions_file>"

                Examples:
                | data               | test                          | output                            |predictions_file           |
                | ../data/iris_missing.csv   | ../data/test_iris_missing.csv   | ./scenario_mspl_1/predictions.csv | ./check_files/predictions_iris_missing.csv   |
        """
        print(self.test_scenario1.__doc__)
        examples = [
            ['data/iris_missing.csv', 'data/test_iris_missing.csv', 'scenario_mspl_1/predictions.csv', 'check_files/predictions_iris_missing.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            test_pred.i_create_all_resources_missing_splits(self, data=example[0], test=example[1], output=example[2])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[3])

    def test_scenario2(self):
        """
            Scenario: Successfully building test predictions from scratch:
                Given I create BigML resources uploading train "<data>" file to test "<test>" remotely with a missing-splits model and log predictions in "<output>"
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
                | ../data/iris_missing.csv   | ../data/test_iris_missing.csv   | ./scenario_mspl_2/predictions.csv   | ./check_files/predictions_iris_missing.csv
        """
        print(self.test_scenario2.__doc__)
        examples = [
            ['data/iris_missing.csv', 'data/test_iris_missing.csv', 'scenario_mspl_2/predictions.csv', 'check_files/predictions_iris_missing.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            test_pred.i_create_all_resources_remote_missing_splits(self, data=example[0], test=example[1], output=example[2])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_pred.i_check_create_test_source(self)
            test_pred.i_check_create_test_dataset(self)
            test_pred.i_check_create_batch_prediction(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[3])
