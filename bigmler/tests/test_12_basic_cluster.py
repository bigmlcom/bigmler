# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015 BigML
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


""" Testing clusters

"""
from world import world, setup_module, teardown_module, teardown_class


import basic_tst_prediction_steps as test_pred
import basic_cluster_prediction_steps as test_cluster


class TestCluster(object):

    def teardown(self):
        """Calling generic teardown for every method

        """
        teardown_class()

    def setup(self):
        """No setup operations for every method at present

        """
        pass

    def test_scenario1(self):
        """
            Scenario: Successfully building test centroids from scratch:
                Given I create BigML resources uploading train "<data>" file to create centroids for "<test>" and log predictions in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the cluster has been created
                And I check that the centroids are ready
                Then the local centroids file is like "<predictions_file>"

                Examples:
                | data               | test               | output                           |predictions_file           |
                | ../data/grades.csv | ../data/grades.csv | ./scenario_c_1_r/centroids.csv | ./check_files/centroids_grades.csv |
                | ../data/diabetes.csv   | ../data/diabetes.csv   | ./scenario_c_1/centroids.csv   | ./check_files/centroids_diabetes.csv   |
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/grades.csv', 'data/grades.csv', 'scenario_c_1_r/centroids.csv', 'check_files/centroids_grades.csv'],
            ['data/diabetes.csv', 'data/diabetes.csv', 'scenario_c_1/centroids.csv', 'check_files/centroids_diabetes.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            test_cluster.i_create_all_cluster_resources(self, data=example[0], test=example[1], output=example[2])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_cluster(self)
            test_cluster.i_check_create_centroids(self)
            test_pred.i_check_predictions(self, example[3])

    def test_scenario2(self):
        """
            Scenario: Successfully building test predictions from source
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using source to find centroids for "<test>" and log predictions in "<output>"
                And I check that the dataset has been created
                And I check that the cluster has been created
                And I check that the centroids are ready
                Then the local centroids file is like "<predictions_file>"

                Examples:
                |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
                | scenario_c_1| {"data": "../data/diabetes.csv", "output": "./scenario_c_1/centroids.csv", "test": "../data/diabetes.csv"}   | ../data/diabetes.csv   | ./scenario_c_2/centroids.csv   | ./check_files/centroids_diabetes.csv   |
        """
        print self.test_scenario2.__doc__
        examples = [
            ['scenario_c_1', '{"data": "data/diabetes.csv", "output": "scenario_c_1/centroids.csv", "test": "data/diabetes.csv"}', 'data/diabetes.csv', 'scenario_c_2/centroids.csv', 'check_files/centroids_diabetes.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            test_cluster.i_create_cluster_resources_from_source(self, test=example[2], output=example[3])
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_cluster(self)
            test_cluster.i_check_create_centroids(self)
            test_pred.i_check_predictions(self, example[4])

    def test_scenario3(self):
        """
            Scenario: Successfully building test predictions from dataset
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using dataset to find centroids for "<test>" and log predictions in "<output>"
                And I check that the cluster has been created
                And I check that the centroids are ready
                Then the local centroids file is like "<predictions_file>"

                Examples:
                |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
                | scenario_c_1| {"data": "../data/diabetes.csv", "output": "./scenario_c_1/centroids.csv", "test": "../data/diabetes.csv"}   | ../data/diabetes.csv   | ./scenario_c_3/centroids.csv   | ./check_files/centroids_diabetes.csv   |

        """
        print self.test_scenario3.__doc__
        examples = [
            ['scenario_c_1', '{"data": "data/diabetes.csv", "output": "scenario_c_1/centroids.csv", "test": "data/diabetes.csv"}', 'data/diabetes.csv', 'scenario_c_3/centroids.csv', 'check_files/centroids_diabetes.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            test_cluster.i_create_cluster_resources_from_dataset(self, test=example[2], output=example[3])
            test_pred.i_check_create_cluster(self)
            test_cluster.i_check_create_centroids(self)
            test_pred.i_check_predictions(self, example[4])

    def test_scenario4(self):
        """
            Scenario: Successfully building test predictions from cluster
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using cluster to find centroids for "<test>" and log predictions in "<output>"
                And I check that the centroids are ready
                Then the local centroids file is like "<predictions_file>"

                Examples:
                |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
                | scenario_c_1| {"data": "../data/diabetes.csv", "output": "./scenario_c_1/centroids.csv", "test": "../data/diabetes.csv"}   | ../data/diabetes.csv   | ./scenario_c_4/centroids.csv   | ./check_files/centroids_diabetes.csv   |

        """
        print self.test_scenario4.__doc__
        examples = [
            ['scenario_c_1', '{"data": "data/diabetes.csv", "output": "scenario_c_1/centroids.csv", "test": "data/diabetes.csv"}', 'data/diabetes.csv', 'scenario_c_4/centroids.csv', 'check_files/centroids_diabetes.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            test_cluster.i_create_cluster_resources_from_cluster(self, test=example[2], output=example[3])
            test_cluster.i_check_create_centroids(self)
            test_pred.i_check_predictions(self, example[4])

    def test_scenario5(self):
        """
            Scenario: Successfully building test predictions from clusters file
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using clusters in file "<clusters_file>" to find centroids for "<test>" and log predictions in "<output>"
                And I check that the centroids are ready
                Then the local centroids file is like "<predictions_file>"

                Examples:
                |scenario    | kwargs                                                  | clusters_file        | test                  | output                      |predictions_file                    |
                | scenario_c_1| {"data": "../data/diabetes.csv", "output": "./scenario_c_1/centroids.csv", "test": "../data/diabetes.csv"}   | ./scenario_c_1/clusters | ../data/diabetes.csv | ./scenario_c_5/centroids.csv | ./check_files/centroids_diabetes.csv |

        """
        print self.test_scenario5.__doc__
        examples = [
            ['scenario_c_1', '{"data": "data/diabetes.csv", "output": "scenario_c_1/centroids.csv", "test": "data/diabetes.csv"}', 'data/diabetes.csv', 'scenario_c_5/centroids.csv', 'check_files/centroids_diabetes.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            test_cluster.i_create_cluster_resources_from_clusters_file(self, test=example[2], output=example[3])
            test_cluster.i_check_create_centroids(self)
            test_pred.i_check_predictions(self, example[4])


    def test_scenario6(self):
        """
            Scenario: Successfully generating datasets from cluster centroids
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I generate datasets for "<centroid_names>" centroids and log predictions in "<output>"
                Then I check that the <datasets_number> cluster datasets are ready

                Examples:
                |scenario    | kwargs                                                  | centroid_names        | output                      | datasets_number |
                | scenario_c_1| {"data": "../data/diabetes.csv", "output": "./scenario_c_1/centroids.csv", "test": "../data/diabetes.csv"}   | Cluster 1,Cluster 2 | ./scenario_c_6/centroids.csv | 2 |

        """
        print self.test_scenario6.__doc__
        examples = [
            ['scenario_c_1', '{"data": "data/diabetes.csv", "output": "scenario_c_1/centroids.csv", "test": "data/diabetes.csv"}', 'Cluster 1,Cluster 2', 'scenario_c_6/centroids.csv', '2']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            test_cluster.i_create_datasets_form_cluster(self, centroids=example[2], output=example[3])
            test_cluster.i_check_cluster_datasets(self, datasets_number=example[4])

    def test_scenario7(self):
        """
            Scenario: Successfully building test predictions from cluster
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using local cluster in "<scenario>" to find centroids for "<test>" and log predictions in "<output>"
                And I check that the centroids are ready
                Then the local centroids file is like "<predictions_file>"

                Examples:
                |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
                | scenario_c_1| {"data": "../data/diabetes.csv", "output": "./scenario_c_1/centroids.csv", "test": "../data/diabetes.csv"}   | ../data/diabetes.csv   | ./scenario_c_7/centroids.csv   | ./check_files/centroids_diabetes.csv   |
        """
        print self.test_scenario7.__doc__
        examples = [
            ['scenario_c_1', '{"data": "data/diabetes.csv", "output": "scenario_c_1/centroids.csv", "test": "data/diabetes.csv"}', 'data/diabetes.csv', 'scenario_c_7/centroids.csv', 'check_files/centroids_diabetes.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            test_cluster.i_create_cluster_resources_from_local_cluster(self, directory=example[0], test=example[2], output=example[3])
            test_cluster.i_check_create_centroids(self)
            test_pred.i_check_predictions(self, example[4])
