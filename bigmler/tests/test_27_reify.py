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


""" Testing reify subcommand

"""



import json
import os


from bigmler.tests.world import (world, common_setup_module, res_filename,
                                 common_teardown_module, teardown_class)

import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.sample_steps as test_sample
import bigmler.tests.reify_steps as test_reify
import bigmler.tests.dataset_advanced_steps as dataset_adv

def setup_module():
    """Setup for the module

    """
    common_setup_module()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestReify(object):

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
            Scenario: Successfully building a source reify output in python
                Given I create a BigML source with data "<data>" and params "<params>"
                And I check that the source has been created
                Then I create a reify output in "<output>" for "<language>"
                And the "<output>" file is like "<check_file>"

                Examples:
                | data | output | params |check_file | language
                | data/iris.csv | scenario_re1/reify.py | {"name": "my_source_name"}|../check_files/reify_source.py | python
        """
        print(self.test_scenario1.__doc__)
        examples = [
            ['data/iris.csv', 'scenario_re1/reify.py', {"name": "my_source_name"}, 'check_files/reify_source.py', 'python'],
            ['data/iris.csv', 'scenario_re1b/reify.ipynb', {"name": "my_source_name"}, 'check_files/reify_source.ipynb', 'nb'],
            ['data/iris.csv', 'scenario_re1c/reify.whizzml', {"name": "my_source_name"}, 'check_files/reify_source.whizzml', 'whizzml']]

        for example in examples:
            print("\nTesting with:\n", example)
            test_reify.create_source(example[0], output=example[1],
                                     args=example[2])
            test_reify.i_create_output(self, example[1], example[4])
            test_reify.i_check_output_file(self, output=example[1],
                                           check_file=example[3])

    def test_scenario2(self):
        """
            Scenario: Successfully building a dataset reify output in python
                Given I create a BigML dataset from a source with data "<data>" and params "<params>"
                And I check that the source has been created
                And I check that the dataset has been created
                Then I create a reify output in "<output>" for "<language>"
                And the "<output>" file is like "<check_file>"

                Examples:
                | data | output | params |check_file | language
                | data/iris.csv | scenario_re2/reify.py | {"name": "my_dataset_name"}|../check_files/reify_dataset.py | python
        """
        print(self.test_scenario2.__doc__)
        examples = [
            ['data/iris.csv', 'scenario_re2/reify.py', {"name": "my_dataset_name"}, 'check_files/reify_dataset.py', 'python']]

        for example in examples:
            print("\nTesting with:\n", example)
            test_reify.create_dataset(example[0], output=example[1],
                                      args=example[2])
            test_reify.i_create_output(self, example[1], example[4], resource_type='dataset')
            test_reify.i_check_output_file(self, output=example[1],
                                           check_file=example[3])

    def test_scenario3(self):
        """
            Scenario: Successfully building a model reify output in python
                Given I create a BigML model from a dataset with data "<data>" and params "<params>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the model has been created
                Then I create a reify output in "<output>" for "<language>"
                And the "<output>" file is like "<check_file>"

                Examples:
                | data | output | params |check_file | language
                | data/iris.csv | scenario_re3/reify.py | {"name": "my_model_name"}|../check_files/reify_model.py | python
        """
        print(self.test_scenario3.__doc__)
        examples = [
            ['data/iris.csv', 'scenario_re3/reify.py', {"name": "my_model_name"}, 'check_files/reify_model.py', 'python']]

        for example in examples:
            print("\nTesting with:\n", example)
            test_reify.create_model(example[0], output=example[1],
                                    args=example[2])
            test_reify.i_create_output(self, example[1], example[4], resource_type='model')
            test_reify.i_check_output_file(self, output=example[1],
                                           check_file=example[3])

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

                Examples:
                | data | output | params |check_file | language | input_data
                | data/iris.csv | scenario_re4/reify.py | {"name": "my_prediction_name"}|../check_files/reify_prediction.py | python | {'petal length': 0.5}
        """
        print(self.test_scenario4.__doc__)
        examples = [
            ['data/iris.csv', 'scenario_re4/reify.py', {"name": "my_prediction_name"}, 'check_files/reify_prediction.py', 'python', {'petal length': 0.5}]]

        for example in examples:
            print("\nTesting with:\n", example)
            test_reify.create_prediction(example[0], input_data=example[5],
                                         output=example[1],
                                         args=example[2])
            test_reify.i_create_output(self, example[1], example[4],
                                       resource_type='prediction')
            test_reify.i_check_output_file(self, output=example[1],
                                           check_file=example[3])

    def test_scenario5(self):
        """
            Scenario: Successfully building a cluster reify output in python
                Given I create a BigML cluster from a dataset with data "<data>" and params "<params>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the cluster has been created
                Then I create a reify output in "<output>" for "<language>"
                And the "<output>" file is like "<check_file>"

                Examples:
                | data | output | params |check_file | language
                | data/iris.csv | scenario_re5/reify.py | {"name": "my_cluster_name"}|../check_files/reify_cluster.py | python
        """
        print(self.test_scenario5.__doc__)
        examples = [
            ['data/iris.csv', 'scenario_re5/reify.py', {"name": "my_cluster_name"}, 'check_files/reify_cluster.py', 'python']]

        for example in examples:
            print("\nTesting with:\n", example)
            test_reify.create_cluster(example[0],
                                      output=example[1],
                                      args=example[2])
            test_reify.i_create_output(self, example[1], example[4],
                                       resource_type='cluster')
            test_reify.i_check_output_file(self, output=example[1],
                                           check_file=example[3])

    def test_scenario6(self):
        """
            Scenario: Successfully building an anomaly detector reify output in python
                Given I create a BigML anomaly from a dataset with data "<data>" and params "<params>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the anomaly detector has been created
                Then I create a reify output in "<output>" for "<language>"
                And the "<output>" file is like "<check_file>"

                Examples:
                | data | output | params |check_file | language
                | data/iris.csv | scenario_re6/reify.py | {"name": "my_anomaly_name"}|../check_files/reify_anomaly.py | python
        """
        print(self.test_scenario6.__doc__)
        examples = [
            ['data/iris.csv', 'scenario_re6/reify.py', {"name": "my_anomaly_name"}, 'check_files/reify_anomaly.py', 'python']]

        for example in examples:
            print("\nTesting with:\n", example)
            test_reify.create_anomaly(example[0],
                                      output=example[1],
                                      args=example[2])
            test_reify.i_create_output(self, example[1], example[4],
                                       resource_type='anomaly')
            test_reify.i_check_output_file(self, output=example[1],
                                           check_file=example[3])

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

                Examples:
                | data | output | params |check_file | language | input_data
                | data/iris.csv | scenario_re7/reify.py | {"name": "my_centroid_name"}|../check_files/reify_anomaly.py | python | {"petal length": 0.5, "sepal length": 1, "petal width": 0.5, "sepal width": 1, "species": "Iris-setosa"}
        """
        print(self.test_scenario7.__doc__)
        examples = [
            ['data/iris.csv', 'scenario_re7/reify.py', {"name": "my_centroid_name"}, 'check_files/reify_centroid.py', 'python', {"petal length": 0.5, "sepal length": 1, "petal width": 0.5, "sepal width": 1, "species": "Iris-setosa"}]]

        for example in examples:
            print("\nTesting with:\n", example)
            test_reify.create_centroid(example[0],
                                       input_data=example[5],
                                       output=example[1],
                                       args=example[2])
            test_reify.i_create_output(self, example[1], example[4],
                                       resource_type='centroid')
            test_reify.i_check_output_file(self, output=example[1],
                                           check_file=example[3])

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

                Examples:
                | data | output | params |check_file | language | input_data
                | data/iris.csv | scenario_re8/reify.py | {"name": "my_anomaly_score_name"}|../check_files/reify_anomaly_score.py | python | {"petal length": 0.5, "sepal length": 1, "petal width": 0.5, "sepal width": 1, "species": "Iris-setosa"}
        """
        print(self.test_scenario8.__doc__)
        examples = [
            ['data/iris.csv', 'scenario_re8/reify.py', {"name": "my_anomaly_score_name"}, 'check_files/reify_anomaly_score.py', 'python', {"petal length": 0.5, "sepal length": 1, "petal width": 0.5, "sepal width": 1, "species": "Iris-setosa"}]]

        for example in examples:
            print("\nTesting with:\n", example)
            test_reify.create_anomaly_score(example[0],
                                            input_data=example[5],
                                            output=example[1],
                                            args=example[2])
            test_reify.i_create_output(self, example[1], example[4],
                                       resource_type='anomaly_score')
            test_reify.i_check_output_file(self, output=example[1],
                                           check_file=example[3])

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

                Examples:
                | data | output | params |check_file | language
                | data/iris.csv | scenario_re9/reify.py | {"name": "my_batch_prediction_name"}|../check_files/reify_batch_prediction.py | python
        """
        print(self.test_scenario9.__doc__)
        examples = [
            ['data/iris.csv', 'scenario_re9/reify.py', {"name": "my_batch_prediction_name"}, 'check_files/reify_batch_prediction.py', 'python']]

        for example in examples:
            print("\nTesting with:\n", example)
            test_reify.create_batch_prediction(example[0],
                                               output=example[1],
                                               args=example[2])
            test_reify.i_create_output(self, example[1], example[4],
                                       resource_type='batch_prediction')
            test_reify.i_check_output_file(self, output=example[1],
                                           check_file=example[3])

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

                Examples:
                | data | output | params |check_file | language
                | data/iris.csv | scenario_re10/reify.py | {"name": "my_batch_centroid_name"}|../check_files/reify_batch_centroid.py | python
        """
        print(self.test_scenario10.__doc__)
        examples = [
            ['data/iris.csv', 'scenario_re10/reify.py', {"name": "my_batch_centroid_name"}, 'check_files/reify_batch_centroid.py', 'python']]

        for example in examples:
            print("\nTesting with:\n", example)
            test_reify.create_batch_centroid(example[0],
                                             output=example[1],
                                             args=example[2])
            test_reify.i_create_output(self, example[1], example[4],
                                       resource_type='batch_centroid')
            test_reify.i_check_output_file(self, output=example[1],
                                           check_file=example[3])

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

                Examples:
                | data | output | params |check_file | language
                | data/iris.csv | scenario_re11/reify.py | {"name": "my_batch_anomaly_score_name"}|../check_files/reify_batch_anomaly_score.py | python
        """
        print(self.test_scenario11.__doc__)
        examples = [
            ['data/iris.csv', 'scenario_re11/reify.py', {"name": "my_batch_anomaly_score_name"}, 'check_files/reify_batch_anomaly_score.py', 'python']]

        for example in examples:
            print("\nTesting with:\n", example)
            test_reify.create_batch_anomaly_score(example[0],
                                                  output=example[1],
                                                  args=example[2])
            test_reify.i_create_output(self, example[1], example[4],
                                       resource_type='batch_anomaly_score')
            test_reify.i_check_output_file(self, output=example[1],
                                           check_file=example[3])

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

                Examples:
                | data | output | params |check_file | language
                | data/iris.csv | scenario_re12/reify.py | {"name": "my_evaluation_name"}|../check_files/reify_evaluation.py | python
        """
        print(self.test_scenario12.__doc__)
        examples = [
            ['data/iris.csv', 'scenario_re12/reify.py', {"name": "my_evaluation_name"}, 'check_files/reify_evaluation.py', 'python']]

        for example in examples:
            print("\nTesting with:\n", example)
            test_reify.create_evaluation(example[0],
                                         output=example[1],
                                         args=example[2])
            test_reify.i_create_output(self, example[1], example[4],
                                       resource_type='evaluation')
            test_reify.i_check_output_file(self, output=example[1],
                                           check_file=example[3])

    def test_scenario13(self):
        """
            Scenario: Successfully building an ensemble reify output in python
                Given I create a BigML ensemble from a dataset with data "<data>" and params "<params>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the ensemble has been created
                Then I create a reify output in "<output>" for "<language>"
                And the "<output>" file is like "<check_file>"

                Examples:
                | data | output | params |check_file | language
                | data/iris.csv | scenario_re13/reify.py | {"name": "my_ensemble_name"}|../check_files/reify_ensemble.py | python
        """
        print(self.test_scenario13.__doc__)
        examples = [
            ['data/iris.csv', 'scenario_re13/reify.py', {"name": "my_ensemble_name"}, 'check_files/reify_ensemble.py', 'python']]

        for example in examples:
            print("\nTesting with:\n", example)
            test_reify.create_ensemble(example[0], output=example[1],
                                       args=example[2])
            test_reify.i_create_output(self, example[1], example[4],
                                       resource_type='ensemble')
            test_reify.i_check_output_file(self, output=example[1],
                                           check_file=example[3])

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
        examples = [
            ['data/iris_sp_chars.csv', 'scenario_re14/reify.py', {"name": "my_sóurcè_sp_name"}, 'check_files/reify_source_sp.py', 'python']]

        for example in examples:
            print("\nTesting with:\n", example)
            test_reify.create_source(example[0], output=example[1],
                                     args=example[2])
            test_reify.i_create_output(self, example[1], example[4],
                                       add_fields=True)
            test_reify.i_check_output_file(self, output=example[1],
                                           check_file=example[3])

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
        examples = [
            ['data/iris.csv', 'scenario_re15/reify.py', {"name": "my_evaluation_name"}, 'check_files/reify_evaluation_split.py', 'python']]

        for example in examples:
            print("\nTesting with:\n", example)
            test_reify.create_evaluation_split(example[0],
                                               output=example[1],
                                               args=example[2])
            test_reify.i_create_output(self, example[1], example[4],
                                       resource_type='evaluation')
            test_reify.i_check_output_file(self, output=example[1],
                                           check_file=example[3])


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

                Examples:
                | data | output | params |check_file | language
                | data/iris.csv | scenario_re16/reify.py | {"name": "my_dataset_from_batch_prediction_name"}|../check_files/reify_batch_prediction_dataset.py | python
        """
        print(self.test_scenario16.__doc__)
        examples = [
            ['data/iris.csv', 'scenario_re16/reify.py', {"name": "my_dataset_from_batch_prediction_name"}, 'check_files/reify_batch_prediction_dataset.py', 'python']]

        for example in examples:
            print("\nTesting with:\n", example)
            test_reify.create_dataset_from_batch_prediction(example[0],
                                                            output=example[1],
                                                            args=example[2])
            test_reify.i_create_output(
                self, example[1], example[4],
                resource_type='batch_prediction_dataset')
            test_reify.i_check_output_file(self, output=example[1],
                                           check_file=example[3])


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

                Examples:
                | data | output | params |check_file | language
                | data/iris.csv | scenario_re17/reify.py | {"name": "my_dataset_from_batch_centroid_name"}|../check_files/reify_batch_centroid_dataset.py | python
        """
        print(self.test_scenario17.__doc__)
        examples = [
            ['data/iris.csv', 'scenario_re17/reify.py', {"name": "my_dataset_from_batch_centroid_name"}, 'check_files/reify_batch_centroid_dataset.py', 'python']]

        for example in examples:
            print("\nTesting with:\n", example)
            test_reify.create_dataset_from_batch_centroid(example[0],
                                                          output=example[1],
                                                          args=example[2])
            test_reify.i_create_output(
                self, example[1], example[4],
                resource_type='batch_centroid_dataset')
            test_reify.i_check_output_file(self, output=example[1],
                                           check_file=example[3])

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
        examples = [
            ['data/iris.csv', 'scenario_re18/reify.py', {"name": "my_dataset_from_batch_anomaly_score_name"}, 'check_files/reify_batch_anomaly_score_dataset.py', 'python']]

        for example in examples:
            print("\nTesting with:\n", example)
            test_reify.create_dataset_from_batch_anomaly(example[0],
                                                         output=example[1],
                                                         args=example[2])
            test_reify.i_create_output(
                self, example[1], example[4],
                resource_type='batch_anomaly_score_dataset')
            test_reify.i_check_output_file(self, output=example[1],
                                           check_file=example[3])


    def test_scenario19(self):
        """
            Scenario: Successfully building a dataset reify output in python when built from another dataset
                Given I create a BigML dataset from a dataset with data "<data>" and params "<params>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the new dataset has been created
                Then I create a reify output in "<output>" for "<language>"
                And the "<output>" file is like "<check_file>"

                Examples:
                | data | output | params |check_file | language
                | data/iris.csv | scenario_re19/reify.py | {"name": "my_dataset_from_dataset_name", 'all_but': [u'000001'], 'all_fields': False, 'input_fields': [u'000004', u'000002', u'000003', u'000000', u'000001'], 'new_fields': [{u'description': u'', 'field': u'2', u'label': u'', u'name': u'new'}], 'objective_field': {'id': u'100004'}}|../check_files/reify_dataset_dataset.py | python
        """
        print(self.test_scenario19.__doc__)
        examples = [
            ['data/iris.csv', 'scenario_re19/reify.py', {"name": "my_dataset_from_dataset_name", 'all_but': ['000001'], 'all_fields': False, 'input_fields': ['000000', '000001', '000002', '000003', '000004'], 'new_fields': [{'description': '', 'field': '2', 'label': '', 'name': 'new'}], 'objective_field': {'id': '100004'}}, 'check_files/reify_dataset_dataset.py', 'python']]

        for example in examples:
            print("\nTesting with:\n", example)
            test_reify.create_dataset_from_dataset(example[0],
                                                   output=example[1],
                                                   args=example[2])
            test_reify.i_create_output(
                self, example[1], example[4], resource_type='dataset')
            test_reify.i_check_output_file(self, output=example[1],
                                           check_file=example[3])


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

                Examples:
                | data | output | params |check_file | language
                | data/iris.csv | scenario_re20/reify.py | {"name": "my_dataset_from_dataset_from_batch_centroid_name"}|../check_files/reify_batch_centroid_dataset_dataset.py | python
        """
        print(self.test_scenario20.__doc__)
        examples = [
            ['data/iris.csv', 'scenario_re20/reify.py', {"name": "my_dataset_from_dataset_from_batch_centroid_name", "new_fields": [{"field": "( integer ( replace ( field \"cluster\" ) \"Cluster \" \"\" ) )", "name": "Cluster"}]}, 'check_files/reify_batch_centroid_dataset_dataset.py', 'python']]

        for example in examples:
            print("\nTesting with:\n", example)
            test_reify.create_dataset_from_dataset_from_batch_centroid(
                example[0], output=example[1], args=example[2])
            test_reify.i_create_output(
                self, example[1], example[4], resource_type='dataset')
            test_reify.i_check_output_file(self, output=example[1],
                                           check_file=example[3])

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

                Examples:
                | data | output | params |check_file | language
                | data/iris.csv | scenario_re2/reify.py | {"name": "my_dataset_name"}|../check_files/reify_dataset.py | python
        """
        print(self.test_scenario21.__doc__)
        examples = [
            ['data/iris.csv', 'scenario_re21/reify.py', {"name": "my_dataset_name"}, 'check_files/reify_dataset_datasets.py', 'python', 'scenario_re21']]

        for example in examples:
            print("\nTesting with:\n", example)
            test_reify.create_dataset_from_datasets( \
                example[0], output=example[1], args=example[2])
            test_reify.i_create_output(self, example[1], example[4],
                                       resource_type='dataset')
            test_reify.i_check_output_file(self, output=example[1],
                                           check_file=example[3])
