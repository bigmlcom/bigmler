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


""" Testing Anomaly Detector batch scores

"""
from __future__ import absolute_import


from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, teardown_class)

import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.basic_batch_tst_prediction_steps as test_batch
import bigmler.tests.basic_anomaly_prediction_steps as test_anomaly


def setup_module():
    """Setup for the module

    """
    common_setup_module()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestBatchAnomalyScores(object):

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

    def test_scenario1(self):
        """
            Scenario: Successfully building test anomaly score predictions from scratch:
                Given I create BigML resources uploading train "<data>" file to find anomaly scores for "<test>" remotely with mapping file "<fields_map>" and log predictions in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the anomaly detector has been created
                And I check that the source has been created from the test file
                And I check that the dataset has been created from the test file
                And I check that the batch anomaly scores prediction has been created
                And I check that the anomaly scores are ready
                Then the local anomaly scores file is like "<predictions_file>"

                Examples:
                | data               | test                    | fields_map | output                        |predictions_file           |
                | ../data/grades.csv | ../data/grades_perm.csv | ../data/grades_fields_map_perm.csv | ./scenario_ab_1_r/anomalies.csv | ./check_files/anomaly_scores_grades.csv |
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/grades.csv', 'data/grades_perm.csv', 'data/grades_fields_map_perm.csv', 'scenario_ab_1_r/anomalies.csv', 'check_files/anomaly_scores_grades.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            test_anomaly.i_create_all_anomaly_resources_with_mapping(self, data=example[0], test=example[1], fields_map=example[2], output=example[3])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_anomaly.i_check_create_anomaly(self)
            test_pred.i_check_create_test_source(self)
            test_pred.i_check_create_test_dataset(self)
            test_batch.i_check_create_batch_anomaly_scores(self)
            test_anomaly.i_check_create_anomaly_scores(self)
            test_anomaly.i_check_anomaly_scores(self, example[4])

    def test_scenario2(self):
        """
            Scenario: Successfully building test anomaly score predictions from test split:
                Given I create BigML resources uploading train "<data>" file to find anomaly scores with test split "<test_split>" remotely and log predictions in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the anomaly detector has been created
                And I check that the train dataset has been created
                And I check that the dataset has been created from the test file
                And I check that the batch anomaly scores prediction has been created
                And I check that the anomaly scores are ready
                Then the local anomaly scores file is like "<predictions_file>"

                Examples:
                | data             | test_split | output                 |predictions_file           |
                | ../data/iris.csv | 0.2 | ./scenario_ab_2/anomalies.csv | ./check_files/anomaly_scores_iris.csv |

        """
        print self.test_scenario2.__doc__
        examples = [
            ['data/iris.csv', '0.2', 'scenario_ab_2/anomalies.csv', 'check_files/anomaly_scores_iris.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            test_anomaly.i_create_all_anomaly_resources_with_test_split(self, data=example[0], test_split=example[1], output=example[2])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_anomaly.i_check_create_anomaly(self)
            test_pred.i_check_create_dataset(self, suffix='train ')
            test_pred.i_check_create_dataset(self, suffix='test ')
            test_batch.i_check_create_batch_anomaly_scores(self)
            test_anomaly.i_check_create_anomaly_scores(self)
            test_anomaly.i_check_anomaly_scores(self, example[3])

    def test_scenario3(self):
        """
            Scenario: Successfully building test anomaly score predictions from test split in a dataset:
                Given I create BigML resources uploading train "<data>" file to find anomaly scores with test split "<test_split>" remotely saved to dataset with no CSV output and log resources in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the anomaly detector has been created
                And I check that the train dataset has been created
                And I check that the dataset has been created from the test file
                And I check that the batch anomaly scores prediction has been created
                Then I check that the batch anomaly scores dataset exists
                And no local CSV file is created

                Examples:
                | data             | test_split | output_dir      |
                | ../data/iris.csv | 0.2        | ./scenario_ab_3 |
        """
        print self.test_scenario3.__doc__
        examples = [
            ['data/iris.csv', '0.2', 'scenario_ab_3']]
        for example in examples:
            print "\nTesting with:\n", example
            test_anomaly.i_create_all_anomaly_resources_with_test_split_no_CSV(self, data=example[0], test_split=example[1], output_dir=example[2])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_anomaly.i_check_create_anomaly(self)
            test_pred.i_check_create_dataset(self, suffix='train ')
            test_pred.i_check_create_dataset(self, suffix='test ')
            test_batch.i_check_create_batch_anomaly_scores(self)
            test_anomaly.i_check_create_batch_anomaly_score_dataset(self)
            test_anomaly.i_check_no_local_CSV(self)

    def test_scenario4(self):
        """
            Scenario: Successfully building test anomaly score predictions from training set as a dataset:
                Given I create BigML resources uploading train "<data>" file to find anomaly scores for the training set remotely saved to dataset with no CSV output and log resources in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the anomaly detector has been created
                And I check that the batch anomaly scores prediction has been created
                Then I check that the batch anomaly scores dataset exists
                And no local CSV file is created

                Examples:
                | data             | output_dir      |
                | ../data/iris.csv | ./scenario_ab_4 |
        """
        print self.test_scenario3.__doc__
        examples = [
            ['data/iris.csv', 'scenario_ab_4']]
        for example in examples:
            print "\nTesting with:\n", example
            test_anomaly.i_create_all_anomaly_resources_without_test_split(self, data=example[0], output_dir=example[1])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_anomaly.i_check_create_anomaly(self)
            test_batch.i_check_create_batch_anomaly_scores(self)
            test_anomaly.i_check_create_batch_anomaly_score_dataset(self)
            test_anomaly.i_check_no_local_CSV(self)
