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


""" Testing clusters

"""
from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)


import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.basic_cluster_prediction_steps as test_cluster


def setup_module():
    """Setup for the module

    """
    common_setup_module()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestCluster:
    """Testing cluster command """

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

    def test_scenario1(self):
        """
        Scenario: Successfully building test centroids from scratch:
            Given I create BigML resources uploading train "<data>" file to create centroids for "<test>" and log predictions in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the cluster has been created
            And I check that the centroids are ready
            Then the local centroids file is like "<predictions_file>"
        """
        print(self.test_scenario1.__doc__)
        headers = ["data", "test", "output", "predictions_file"]
        examples = [
            ['data/grades.csv', 'data/grades.csv',
             'scenario_c_1_r/centroids.csv',
             'check_files/centroids_grades.csv'],
            ['data/diabetes.csv', 'data/diabetes.csv',
             'scenario_c_1/centroids.csv',
             'check_files/centroids_diabetes.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_cluster.i_create_all_cluster_resources(
                self, data=example["data"], test=example["test"],
                output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_cluster(self)
            test_cluster.i_check_create_centroids(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario2(self):
        """
        Scenario: Successfully building test predictions from source
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML resources using source to find centroids for "<test>" and log predictions in "<output>"
            And I check that the dataset has been created
            And I check that the cluster has been created
            And I check that the centroids are ready
            Then the local centroids file is like "<predictions_file>"
        """
        print(self.test_scenario2.__doc__)
        headers = ["scenario", "kwargs", "test", "output", "predictions_file"]
        examples = [
            ['scenario_c_1', '{"data": "data/diabetes.csv",' +
             ' "output": "scenario_c_1/centroids.csv",' +
             ' "test": "data/diabetes.csv"}', 'data/diabetes.csv',
             'scenario_c_2/centroids.csv',
             'check_files/centroids_diabetes.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_cluster.i_create_cluster_resources_from_source(
                self, test=example["test"], output=example["output"])
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_cluster(self)
            test_cluster.i_check_create_centroids(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario3(self):
        """
        Scenario: Successfully building test predictions from dataset
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML resources using dataset to find centroids for "<test>" and log predictions in "<output>"
            And I check that the cluster has been created
            And I check that the centroids are ready
            Then the local centroids file is like "<predictions_file>"
        """
        print(self.test_scenario3.__doc__)
        headers = ["scenario", "kwargs", "test", "output", "predictions_file"]
        examples = [
            ['scenario_c_1', '{"data": "data/diabetes.csv",' +
             ' "output": "scenario_c_1/centroids.csv",' +
             ' "test": "data/diabetes.csv"}', 'data/diabetes.csv',
             'scenario_c_3/centroids.csv',
             'check_files/centroids_diabetes.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_cluster.i_create_cluster_resources_from_dataset(
                self, test=example["test"], output=example["output"])
            test_pred.i_check_create_cluster(self)
            test_cluster.i_check_create_centroids(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario4(self):
        """
        Scenario: Successfully building test predictions from cluster
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML resources using cluster to find centroids for "<test>" and log predictions in "<output>"
            And I check that the centroids are ready
            Then the local centroids file is like "<predictions_file>"
        """
        print(self.test_scenario4.__doc__)
        headers = ["scenario", "kwargs", "test", "output", "predictions_file"]
        examples = [
            ['scenario_c_1', '{"data": "data/diabetes.csv",' +
             ' "output": "scenario_c_1/centroids.csv",' +
             ' "test": "data/diabetes.csv"}', 'data/diabetes.csv',
             'scenario_c_4/centroids.csv',
             'check_files/centroids_diabetes.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_cluster.i_create_cluster_resources_from_cluster(
                self, test=example["test"], output=example["output"])
            test_cluster.i_check_create_centroids(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario5(self):
        """
        Scenario: Successfully building test predictions from clusters file
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML resources using clusters in file "<clusters_file>" to find centroids for "<test>" and log predictions in "<output>"
            And I check that the centroids are ready
            Then the local centroids file is like "<predictions_file>"
        """
        print(self.test_scenario5.__doc__)
        headers = ["scenario", "kwargs", "clusters_file", "test", "output",
                   "predictions_file"]
        examples = [
            ['scenario_c_1', '{"data": "data/diabetes.csv", "output": "scenario_c_1/centroids.csv", "test": "data/diabetes.csv"}', 'scenario_c_1/clusters', 'data/diabetes.csv', 'scenario_c_5/centroids.csv', 'check_files/centroids_diabetes.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_cluster.i_create_cluster_resources_from_clusters_file(
                self, clusters_file=example["clusters_file"],
                test=example["test"], output=example["output"])
            test_cluster.i_check_create_centroids(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario6(self):
        """
        Scenario: Successfully generating datasets from cluster centroids
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I generate datasets for "<centroid_names>" centroids and log predictions in "<output>"
            Then I check that the <datasets_number> cluster datasets are ready
        """
        print(self.test_scenario6.__doc__)
        headers = ["scenario", "kwargs", "centroid_names", "output",
                   "datasets_number"]
        examples = [
            ['scenario_c_1', '{"data": "data/diabetes.csv",' +
             ' "output": "scenario_c_1/centroids.csv",' +
             ' "test": "data/diabetes.csv"}', 'Cluster 1,Cluster 2',
             'scenario_c_6/centroids.csv', '2']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_cluster.i_create_datasets_from_cluster(
                self, centroids=example["centroid_names"],
                output=example["output"])
            test_cluster.i_check_cluster_datasets(
                self, datasets_number=example["datasets_number"])

    def test_scenario7(self):
        """
        Scenario: Successfully building test predictions from cluster
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML resources using local cluster in "<scenario>" to find centroids for "<test>" and log predictions in "<output>"
            And I check that the centroids are ready
            Then the local centroids file is like "<predictions_file>"
        """
        print(self.test_scenario7.__doc__)
        headers = ["scenario", "kwargs", "test", "output", "predictions_file"]
        examples = [
            ['scenario_c_1', '{"data": "data/diabetes.csv", "output": "scenario_c_1/centroids.csv", "test": "data/diabetes.csv"}', 'data/diabetes.csv', 'scenario_c_7/centroids.csv', 'check_files/centroids_diabetes.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_cluster.i_create_cluster_resources_from_local_cluster(
                self, directory=example["scenario"], test=example["test"],
                output=example["output"])
            test_cluster.i_check_create_centroids(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario8(self):
        """
        Scenario: Successfully generating models from cluster centroids
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I generate models for "<centroid_names>" centroids and log results in "<output>"
            Then I check that the <model_number> cluster models are ready
        """
        print(self.test_scenario8.__doc__)
        headers = ["scenario", "kwargs", "centroid_names", "output",
                   "models_number"]
        examples = [
            ['scenario_c_1', '{"data": "data/diabetes.csv",' +
             ' "output": "scenario_c_1/centroids.csv",' +
             ' "test": "data/diabetes.csv"}', 'Cluster 1,Cluster 2',
             'scenario_c_8/centroids.csv', '2']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_cluster.i_create_models_from_cluster(
                self, centroids=example["centroid_names"],
                output=example["output"])
            test_cluster.i_check_create_cluster(self)
            test_cluster.i_check_cluster_models(
                self, models_number=example["models_number"])

    def test_scenario9(self):
        """
        Scenario: Successfully building test predictions from dataset with summary fields
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML cluster using dataset and summary fields "<summary_fields>" and log resources in "<output_dir>"
            And I check that the cluster has been created
            Then the cluster has summary fields "<summary_fields>"
        """
        print(self.test_scenario9.__doc__)
        headers = ["scenario", "kwargs", "output_dir", "summary_fields"]
        examples = [
            ['scenario_c_1', '{"data": "data/diabetes.csv",' +
             ' "output": "scenario_c_1/centroids.csv",' +
             ' "test": "data/diabetes.csv"}', 'scenario_c_9', '000008,000007']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_cluster.i_create_cluster_from_dataset_with_summary_fields(
                self, summary_fields=example["summary_fields"],
                output_dir=example["output_dir"])
            test_pred.i_check_create_cluster(self)
            test_cluster.i_check_cluster_has_summary_fields(
                self, example["summary_fields"])
