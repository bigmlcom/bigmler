# -*- coding: utf-8 -*-
#!/usr/bin/env python
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#pylint: disable=locally-disabled,too-many-public-methods
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


""" Testing reify subcommand

"""
from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)

import bigmler.tests.reify_steps as test_reify

def setup_module():
    """Setup for the module

    """
    common_setup_module()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestReify:
    """Testing reify command"""

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
        Scenario: Successfully building a source reify output in python
            Given I create a BigML source with data "<data>" and params "<params>"
            And I check that the source has been created
            Then I create a reify output in "<output>" for "<language>"
            And the "<output>" file is like "<check_file>"
        """
        print(self.test_scenario1.__doc__)
        headers = ["data", "output", "params", "check_file", "language"]
        examples = [
            ['data/iris.csv', 'scenario_re1/reify.py',
             {"name": "my_source_name"},
             'check_files/reify_source.py', 'python'],
            ['data/iris.csv', 'scenario_re1b/reify.ipynb',
             {"name": "my_source_name"},
             'check_files/reify_source.ipynb', 'nb'],
            ['data/iris.csv', 'scenario_re1c/reify.whizzml',
             {"name": "my_source_name"},
             'check_files/reify_source.whizzml', 'whizzml']]

        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_reify.create_source(
                example["data"], output=example["output"],
                args=example["params"])
            test_reify.i_create_output(
                self, example["output"], example["language"])
            test_reify.i_check_output_file(
                self, output=example["output"],
                check_file=example["check_file"])

    def test_scenario2(self):
        """
        Scenario: Successfully building a dataset reify output in python
            Given I create a BigML dataset from a source with data "<data>" and params "<params>"
            And I check that the source has been created
            And I check that the dataset has been created
            Then I create a reify output in "<output>" for "<language>"
            And the "<output>" file is like "<check_file>"
        """
        print(self.test_scenario2.__doc__)
        headers = ["data", "output", "params", "check_file", "language"]
        examples = [
            ['data/iris.csv', 'scenario_re2/reify.py',
             {"name": "my_dataset_name"}, 'check_files/reify_dataset.py',
             'python']]

        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_reify.create_dataset(
                example["data"],
                output=example["output"],
                args=example["params"])
            test_reify.i_create_output(
                self, example["output"], example["language"],
                resource_type='dataset')
            test_reify.i_check_output_file(self, output=example["output"],
                                           check_file=example["check_file"])

    def test_scenario3(self):
        """
        Scenario: Successfully building a model reify output in python
            Given I create a BigML model from a dataset with data "<data>" and params "<params>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the model has been created
            Then I create a reify output in "<output>" for "<language>"
            And the "<output>" file is like "<check_file>"
        """
        print(self.test_scenario3.__doc__)
        headers = ["data", "output", "params", "check_file", "language"]
        examples = [
            ['data/iris.csv', 'scenario_re3/reify.py',
             {"name": "my_model_name"},
             'check_files/reify_model.py', 'python']]

        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_reify.create_model(example["data"], output=example["output"],
                                    args=example["params"])
            test_reify.i_create_output(self, example["output"],
                                       example["language"],
                                       resource_type='model')
            test_reify.i_check_output_file(
                self, output=example["output"],
                check_file=example["check_file"])

    def test_scenario4(self):
        """
        Scenario: Successfully building a prediction reify output in python
            Given I create a BigML prediction for "<input_data>" from a model with data "<data>" and params "<params>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the model has been created
            And I check that the prediction has been created
            Then I create a reify output in "<output>" for "<language>"
            And the "<output>" file is like "<check_file>"
        """
        print(self.test_scenario4.__doc__)
        headers = ["data", "output", "params", "check_file", "language",
                   "input_data"]
        examples = [
            ['data/iris.csv', 'scenario_re4/reify.py', {"name": "my_prediction_name"}, 'check_files/reify_prediction.py', 'python', {'petal length': 0.5}]]

        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_reify.create_prediction(
                example["data"], input_data=example["input_data"],
                output=example["output"], args=example["params"])
            test_reify.i_create_output(
                self, example["output"], example["language"],
                resource_type='prediction')
            test_reify.i_check_output_file(
                self, output=example["output"],
                check_file=example["check_file"])

    def test_scenario5(self):
        """
        Scenario: Successfully building a cluster reify output in python
            Given I create a BigML cluster from a dataset with data "<data>" and params "<params>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the cluster has been created
            Then I create a reify output in "<output>" for "<language>"
            And the "<output>" file is like "<check_file>"
        """
        print(self.test_scenario5.__doc__)
        headers = ["data", "output", "params", "check_file", "language"]
        examples = [
            ['data/iris.csv', 'scenario_re5/reify.py',
             {"name": "my_cluster_name"},
             'check_files/reify_cluster.py', 'python']]

        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_reify.create_cluster(
                example["data"], output=example["output"],
                args=example["params"])
            test_reify.i_create_output(
                self, example["output"], example["language"],
                resource_type='cluster')
            test_reify.i_check_output_file(
                self, output=example["output"],
                check_file=example["check_file"])

    def test_scenario6(self):
        """
            Scenario: Successfully building an anomaly detector reify output in python
                Given I create a BigML anomaly from a dataset with data "<data>" and params "<params>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the anomaly detector has been created
                Then I create a reify output in "<output>" for "<language>"
                And the "<output>" file is like "<check_file>"
        """
        print(self.test_scenario6.__doc__)
        headers = ["data", "output", "params", "check_file", "language"]
        examples = [
            ['data/iris.csv', 'scenario_re6/reify.py',
             {"name": "my_anomaly_name"},
             'check_files/reify_anomaly.py', 'python']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_reify.create_anomaly(
                example["data"], output=example["output"],
                args=example["params"])
            test_reify.i_create_output(
                self, example["output"], example["language"],
                resource_type='anomaly')
            test_reify.i_check_output_file(
                self, output=example["output"],
                check_file=example["check_file"])

    def test_scenario7(self):
        """
        Scenario: Successfully building a centroid reify output in python
            Given I create a BigML centroid for "<input_data>" from a cluster with data "<data>" and params "<params>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the cluster has been created
            And I check that the centroid has been created
            Then I create a reify output in "<output>" for "<language>"
            And the "<output>" file is like "<check_file>"
        """
        print(self.test_scenario7.__doc__)
        headers = ["data", "output", "params", "check_file", "language",
                   "input_data"]
        examples = [
            ['data/iris.csv', 'scenario_re7/reify.py',
             {"name": "my_centroid_name"}, 'check_files/reify_centroid.py',
             'python', {"petal length": 0.5, "sepal length": 1,
             "petal width": 0.5, "sepal width": 1, "species": "Iris-setosa"}]]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_reify.create_centroid(
                example["data"], input_data=example["input_data"],
                output=example["output"], args=example["params"])
            test_reify.i_create_output(
                self, example["output"], example["language"],
                resource_type='centroid')
            test_reify.i_check_output_file(
                self, output=example["output"],
                check_file=example["check_file"])

    def test_scenario8(self):
        """
        Scenario: Successfully building an anomaly score reify output in python
            Given I create a BigML anomaly score for "<input_data>" from an anomaly detector with data "<data>" and params "<params>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the anomaly detector has been created
            And I check that the anomaly score has been created
            Then I create a reify output in "<output>" for "<language>"
            And the "<output>" file is like "<check_file>"
        """
        print(self.test_scenario8.__doc__)
        headers = ["data", "output", "params", "check_file", "language",
                   "input_data"]
        examples = [
            ['data/iris.csv', 'scenario_re8/reify.py',
             {"name": "my_anomaly_score_name"},
             'check_files/reify_anomaly_score.py', 'python',
             {"petal length": 0.5, "sepal length": 1, "petal width": 0.5,
              "sepal width": 1, "species": "Iris-setosa"}]]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_reify.create_anomaly_score(
                example["data"], input_data=example["input_data"],
                output=example["output"], args=example["params"])
            test_reify.i_create_output(
                self, example["output"], example["language"],
                resource_type='anomaly_score')
            test_reify.i_check_output_file(
                self, output=example["output"],
                check_file=example["check_file"])

    def test_scenario9(self):
        """
        Scenario: Successfully building a batch prediction reify output in python
            Given I create a BigML batch prediction from a model with data "<data>" and params "<params>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the model has been created
            And I check that the batch prediction has been created
            Then I create a reify output in "<output>" for "<language>"
            And the "<output>" file is like "<check_file>"
        """
        print(self.test_scenario9.__doc__)
        headers = ["data", "output", "params", "check_file", "language"]
        examples = [
            ['data/iris.csv', 'scenario_re9/reify.py',
             {"name": "my_batch_prediction_name"},
             'check_files/reify_batch_prediction.py', 'python']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_reify.create_batch_prediction(
                example["data"], output=example["output"],
                args=example["params"])
            test_reify.i_create_output(
                self, example["output"], example["language"],
                resource_type='batch_prediction')
            test_reify.i_check_output_file(
                self, output=example["output"],
                check_file=example["check_file"])

    def test_scenario10(self):
        """
        Scenario: Successfully building a batch centroid reify output in python
            Given I create a BigML batch centroid from a cluster with data "<data>" and params "<params>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the cluster has been created
            And I check that the batch centroid has been created
            Then I create a reify output in "<output>" for "<language>"
            And the "<output>" file is like "<check_file>"
        """
        print(self.test_scenario10.__doc__)
        headers = ["data", "output", "params", "check_file", "language"]
        examples = [
            ['data/iris.csv', 'scenario_re10/reify.py',
             {"name": "my_batch_centroid_name"},
             'check_files/reify_batch_centroid.py', 'python']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_reify.create_batch_centroid(
                example["data"], output=example["output"],
                args=example["params"])
            test_reify.i_create_output(
                self, example["output"], example["language"],
                resource_type='batch_centroid')
            test_reify.i_check_output_file(
                self, output=example["output"],
                check_file=example["check_file"])

    def test_scenario11(self):
        """
        Scenario: Successfully building a batch anomaly score reify output in python
            Given I create a BigML batch anomaly score from an anomaly detector with data "<data>" and params "<params>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the anomaly detector has been created
            And I check that the batch anomaly score has been created
            Then I create a reify output in "<output>" for "<language>"
            And the "<output>" file is like "<check_file>"
        """
        print(self.test_scenario11.__doc__)
        headers = ["data", "output", "params", "check_file", "language"]
        examples = [
            ['data/iris.csv', 'scenario_re11/reify.py',
             {"name": "my_batch_anomaly_score_name"},
             'check_files/reify_batch_anomaly_score.py', 'python']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_reify.create_batch_anomaly_score(
                example["data"], output=example["output"],
                args=example["params"])
            test_reify.i_create_output(
                self, example["output"], example["language"],
                resource_type='batch_anomaly_score')
            test_reify.i_check_output_file(
                self, output=example["output"],
                check_file=example["check_file"])

    def test_scenario12(self):
        """
        Scenario: Successfully building an evaluation reify output in python
            Given I create a BigML evaluation with data "<data>" and params "<params>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the model has been created
            And I check that the evaluation has been created
            Then I create a reify output in "<output>" for "<language>"
            And the "<output>" file is like "<check_file>"
        """
        print(self.test_scenario12.__doc__)
        headers = ["data", "output", "params", "check_file", "language"]
        examples = [
            ['data/iris.csv', 'scenario_re12/reify.py',
             {"name": "my_evaluation_name"},
             'check_files/reify_evaluation.py', 'python']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_reify.create_evaluation(
                example["data"], output=example["output"],
                args=example["params"])
            test_reify.i_create_output(
                self, example["output"], example["language"],
                resource_type='evaluation')
            test_reify.i_check_output_file(
                self, output=example["output"],
                check_file=example["check_file"])

    def test_scenario13(self):
        """
        Scenario: Successfully building an ensemble reify output in python
            Given I create a BigML ensemble from a dataset with data "<data>" and params "<params>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the ensemble has been created
            Then I create a reify output in "<output>" for "<language>"
            And the "<output>" file is like "<check_file>"
        """
        print(self.test_scenario13.__doc__)
        headers = ["data", "output", "params", "check_file", "language"]
        examples = [
            ['data/iris.csv', 'scenario_re13/reify.py', {"name": "my_ensemble_name"}, 'check_files/reify_ensemble.py', 'python']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_reify.create_ensemble(
                example["data"], output=example["output"],
                args=example["params"])
            test_reify.i_create_output(
                self, example["output"], example["language"],
                resource_type='ensemble')
            test_reify.i_check_output_file(
                self, output=example["output"],
                check_file=example["check_file"])

    def test_scenario14(self):
        """
        Scenario: Successfully building a source reify output with fields in python
            Given I create a BigML source with data "<data>" and params "<params>"
            And I check that the source has been created
            Then I create a reify output in "<output>" for "<language>"
            And the "<output>" file is like "<check_file>"

            Examples:
            | data | output | params |check_file | language
            | data/iris_sp_chars.csv | scenario_re14/reify.py | {"name": "my_sóurcè_sp_name"}|../check_files/reify_source_sp.py | python
        """
        print(self.test_scenario14.__doc__)
        headers = ["data", "output", "params", "check_file", "language"]
        examples = [
            ['data/iris_sp_chars.csv', 'scenario_re14/reify.py',
             {"name": "my_sóurcè_sp_name"}, 'check_files/reify_source_sp.py',
             'python']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_reify.create_source(
                example["data"], output=example["output"],
                args=example["params"])
            test_reify.i_create_output(
                self, example["output"], example["language"], add_fields=True)
            test_reify.i_check_output_file(
                self, output=example["output"],
                check_file=example["check_file"])

    def test_scenario15(self):
        """
        Scenario: Successfully building an evaluation with train/tests split reify output in python
            Given I create a BigML evaluation with data "<data>" and train/test split and params "<params>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the model has been created
            And I check that the evaluation has been created
            Then I create a reify output in "<output>" for "<language>"
            And the "<output>" file is like "<check_file>"

            Examples:
            | data | output | params |check_file | language
            | data/iris.csv | scenario_re15/reify.py | {"name": "my_evaluation_name"}|../check_files/reify_evaluation_split.py | python
        """
        print(self.test_scenario15.__doc__)
        headers = ["data", "output", "params", "check_file", "language"]
        examples = [
            ['data/iris.csv', 'scenario_re15/reify.py',
             {"name": "my_evaluation_name"},
             'check_files/reify_evaluation_split.py', 'python']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_reify.create_evaluation_split(
                example["data"], output=example["output"],
                args=example["params"])
            test_reify.i_create_output(
                self, example["output"], example["language"],
                resource_type='evaluation')
            test_reify.i_check_output_file(
                self, output=example["output"],
                check_file=example["check_file"])

    def test_scenario16(self):
        """
        Scenario: Successfully building a dataset reify output in python when built from a batch prediction
            Given I create a BigML dataset from a batch prediction from a model with data "<data>" and params "<params>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the model has been created
            And I check that the batch prediction has been created
            And I check that the batch prediction dataset has been created
            Then I create a reify output in "<output>" for "<language>"
            And the "<output>" file is like "<check_file>"
        """
        print(self.test_scenario16.__doc__)
        headers = ["data", "output", "params", "check_file", "language"]
        examples = [
            ['data/iris.csv', 'scenario_re16/reify.py',
             {"name": "my_dataset_from_batch_prediction_name"},
             'check_files/reify_batch_prediction_dataset.py', 'python']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_reify.create_dataset_from_batch_prediction(
                example["data"], output=example["output"],
                args=example["params"])
            test_reify.i_create_output(
                self, example["output"], example["language"],
                resource_type='batch_prediction_dataset')
            test_reify.i_check_output_file(
                self, output=example["output"],
                check_file=example["check_file"])

    def test_scenario17(self):
        """
        Scenario: Successfully building a dataset reify output in python when built from a batch centroid
            Given I create a BigML dataset from a batch centroid from a cluster with data "<data>" and params "<params>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the cluster has been created
            And I check that the batch centroid has been created
            And I check that the batch centroid dataset has been created
            Then I create a reify output in "<output>" for "<language>"
            And the "<output>" file is like "<check_file>"
        """
        print(self.test_scenario17.__doc__)
        headers = ["data", "output", "params", "check_file", "language"]
        examples = [
            ['data/iris.csv', 'scenario_re17/reify.py',
             {"name": "my_dataset_from_batch_centroid_name"},
             'check_files/reify_batch_centroid_dataset.py', 'python']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_reify.create_dataset_from_batch_centroid(
                example["data"], output=example["output"],
                args=example["params"])
            test_reify.i_create_output(
                self, example["output"], example["language"],
                resource_type='batch_centroid_dataset')
            test_reify.i_check_output_file(
                self, output=example["output"],
                check_file=example["check_file"])

    def test_scenario18(self):
        """
        Scenario: Successfully building a dataset reify output in python when built from a batch anomaly score
            Given I create a BigML dataset from a batch anomaly score from an anomaly detector with data "<data>" and params "<params>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the anomaly detector has been created
            And I check that the batch anomaly score has been created
            And I check that the batch anomaly score dataset has been created
            Then I create a reify output in "<output>" for "<language>"
            And the "<output>" file is like "<check_file>"

            Examples:
            | data | output | params |check_file | language
            | data/iris.csv | scenario_re18/reify.py | {"name": "my_dataset_from_batch_anomaly_score_name"}|../check_files/reify_batch_anomaly_score_dataset.py | python
        """
        print(self.test_scenario18.__doc__)
        headers = ["data", "output", "params", "check_file", "language"]
        examples = [
            ['data/iris.csv', 'scenario_re18/reify.py',
             {"name": "my_dataset_from_batch_anomaly_score_name"},
             'check_files/reify_batch_anomaly_score_dataset.py', 'python']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_reify.create_dataset_from_batch_anomaly(
                example["data"], output=example["output"],
                args=example["params"])
            test_reify.i_create_output(
                self, example["output"], example["language"],
                resource_type='batch_anomaly_score_dataset')
            test_reify.i_check_output_file(
                self, output=example["output"],
                check_file=example["check_file"])

    def test_scenario19(self):
        """
        Scenario: Successfully building a dataset reify output in python when built from another dataset
            Given I create a BigML dataset from a dataset with data "<data>" and params "<params>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the new dataset has been created
            Then I create a reify output in "<output>" for "<language>"
            And the "<output>" file is like "<check_file>"
       """
        print(self.test_scenario19.__doc__)
        headers = ["data", "output", "params", "check_file", "language"]
        examples = [
            ['data/iris.csv', 'scenario_re19/reify.py',
             {"name": "my_dataset_from_dataset_name",
              'all_but': ['000001'], 'all_fields': False,
              'input_fields': ['000000', '000001', '000002', '000003',
                               '000004'],
              'new_fields': [{'description': '', 'field': '2',
                              'label': '', 'name': 'new'}],
              'objective_field': {'id': '100004'}},
              'check_files/reify_dataset_dataset.py', 'python']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_reify.create_dataset_from_dataset(
                example["data"], output=example["output"],
                args=example["params"])
            test_reify.i_create_output(
                self, example["output"], example["language"],
                resource_type='dataset')
            test_reify.i_check_output_file(
                self, output=example["output"],
                check_file=example["check_file"])

    def test_scenario20(self):
        """
        Scenario: Successfully building a dataset reify output in python when built from a dataset from a batch centroid
            Given I create a BigML dataset from a dataset from a batch centroid from a cluster with data "<data>" and params "<params>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the cluster has been created
            And I check that the batch centroid has been created
            And I check that the batch centroid dataset has been created
            And I check that the batch centroid dataset dataset has been created
            Then I create a reify output in "<output>" for "<language>"
            And the "<output>" file is like "<check_file>"
        """
        print(self.test_scenario20.__doc__)
        headers = ["data", "output", "params", "check_file", "language"]
        examples = [
            ['data/iris.csv', 'scenario_re20/reify.py',
             {"name": "my_dataset_from_dataset_from_batch_centroid_name",
              "new_fields": [{"field": "( integer ( replace (" +
              " field \"cluster\" ) \"Cluster \" \"\" ) )",
              "name": "Cluster"}]},
             'check_files/reify_batch_centroid_dataset_dataset.py', 'python']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_reify.create_dataset_from_dataset_from_batch_centroid(
                example["data"], output=example["output"],
                args=example["params"])
            test_reify.i_create_output(
                self, example["output"], example["language"],
                resource_type='dataset')
            test_reify.i_check_output_file(
                self, output=example["output"],
                check_file=example["check_file"])

    def test_scenario21(self):
        """
        Scenario: Successfully building a dataset from a list of datasets
        reify output in python
            Given I create a BigML dataset from a list of datasets with data "<data>" and params "<params>"
            And I check that the source has been created
            And I check that the dataset has been created
            Then I create a BigML dataset from a source with data "<data>" and params "<params>"
            And I check that the source has been created
            And I check that the dataset has been created
            Then I create a reify output in "<output>" for "<language>"
            And the "<output>" file is like "<check_file>"
        """
        print(self.test_scenario21.__doc__)
        headers = ["data", "output", "params", "check_file", "language"]
        examples = [
            ['data/iris.csv', 'scenario_re21/reify.py',
             {"name": "my_dataset_name"},
             'check_files/reify_dataset_datasets.py', 'python',
             'scenario_re21']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_reify.create_dataset_from_datasets(
                example["data"], output=example["output"],
                args=example["params"])
            test_reify.i_create_output(
                self, example["output"], example["language"],
                resource_type='dataset')
            test_reify.i_check_output_file(
                self, output=example["output"],
                check_file=example["check_file"])
