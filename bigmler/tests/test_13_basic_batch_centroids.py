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


""" Testing batch centroids

"""
from __future__ import absolute_import


from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, teardown_class)


import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.basic_batch_tst_prediction_steps as batch_pred
import bigmler.tests.basic_cluster_prediction_steps as test_cluster
import bigmler.tests.basic_anomaly_prediction_steps as test_anomaly


def setup_module():
    """Setup for the module

    """
    common_setup_module()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestBatchCentroids(object):

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
            Scenario: Successfully building test centroid predictions from scratch:
                Given I create BigML resources uploading train "<data>" file to find centroids for "<test>" remotely with mapping file "<fields_map>" and log predictions in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the cluster has been created
                And I check that the source has been created from the test file
                And I check that the dataset has been created from the test file
                And I check that the batch centroid prediction has been created
                And I check that the centroids are ready
                Then the local centroids file is like "<predictions_file>"

                Examples:
                | data               | test                    | fields_map | output                        |predictions_file           |
                | ../data/grades.csv | ../data/grades_perm.csv | ../data/grades_fields_map_perm.csv | ./scenario_cb_1_r/centroids.csv | ./check_files/centroids_grades.csv |
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/grades.csv', 'data/grades_perm.csv', 'data/grades_fields_map_perm.csv', 'scenario_cb_1_r/centroids.csv', 'check_files/centroids_grades.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            test_cluster.i_create_all_cluster_resources_with_mapping(self, data=example[0], test=example[1], fields_map=example[2], output=example[3])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_cluster(self)
            test_pred.i_check_create_test_source(self)
            test_pred.i_check_create_test_dataset(self)
            batch_pred.i_check_create_batch_centroid(self)
            test_cluster.i_check_create_centroids(self)
            test_pred.i_check_predictions(self, example[4])

    def test_scenario2(self):
        """
            Scenario: Successfully building remote test centroid predictions from scratch to dataset:
                Given I create BigML resources uploading train "<data>" file to find centroids for "<test>" remotely to dataset with no CSV and log resources in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the cluster has been created
                And I check that the source has been created from the test file
                And I check that the dataset has been created from the test file
                And I check that the batch centroid prediction has been created
                Then I check that the batch centroids dataset exists
                And no local CSV file is created

                Examples:
                | data               | test                    |  output_dir     |
                | ../data/grades.csv | ../data/test_grades.csv | ./scenario_cb_2 |

        """
        print self.test_scenario2.__doc__
        examples = [
            ['data/grades.csv', 'data/test_grades.csv', 'scenario_cb_2']]
        for example in examples:
            print "\nTesting with:\n", example
            test_cluster.i_create_all_cluster_resources_to_dataset(self, data=example[0], test=example[1], output_dir=example[2])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_cluster(self)
            test_pred.i_check_create_test_source(self)
            test_pred.i_check_create_test_dataset(self)
            batch_pred.i_check_create_batch_centroid(self)
            batch_pred.i_check_create_batch_centroids_dataset(self)
            test_anomaly.i_check_no_local_CSV(self)


    def test_scenario3(self):
        """
            Scenario: Successfully building remote test centroid predictions from scratch with prediction fields:
                Given I create BigML resources uploading train "<data>" file to find centroids for "<test>" remotely with prediction fields "<prediction_fields>" and log resources in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the cluster has been created
                And I check that the source has been created from the test file
                And I check that the dataset has been created from the test file
                And I check that the batch centroid prediction has been created
                And I check that the centroids are ready
                Then the local centroids file is like "<predictions_file>"

                Examples:
                | data               | test                    |  prediction_fields | output     | predictions_file
                | ../data/grades.csv | ../data/test_grades.csv |  Assignment       |./scenario_cb_3_r/centroids.csv | ./check_files/centroids_grades_field.csv |

        """
        print self.test_scenario3.__doc__
        examples = [
            ['data/grades.csv', 'data/grades.csv', 'Assignment',
             './scenario_cb_3_r/centroids.csv', "./check_files/centroids_grades_field.csv"]]
        for example in examples:
            print "\nTesting with:\n", example
            test_cluster.i_create_all_cluster_resources_with_prediction_fields(
                self, data=example[0], test=example[1],
                prediction_fields=example[2], output=example[3])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_cluster(self)
            test_pred.i_check_create_test_source(self)
            test_pred.i_check_create_test_dataset(self)
            batch_pred.i_check_create_batch_centroid(self)
            test_cluster.i_check_create_centroids(self)
            test_pred.i_check_predictions(self, example[4])
