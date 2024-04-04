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


""" Testing analyze subcommand

"""
from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)

import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.evaluation_steps as evaluation
import bigmler.tests.dataset_advanced_steps as dataset_adv


def setup_module():
    """Setup for the module

    """
    common_setup_module()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestAnalyze:
    """Testing bigmler analyze"""

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
        Scenario: Successfully building k-fold cross-validation from dataset:
            Given I create BigML dataset uploading train "<data>" file in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I create BigML <kfold>-fold cross-validation
            And I check that the <kfold>-datasets have been created
            And I check that the <kfold>-models have been created
            And I check that the <kfold>-fold cross-validation has been created
            Then the evaluation file is like "<json_evaluation_file>"
        """
        print(self.test_scenario1.__doc__)
        headers = ["data", "output", "kfold", "json_evaluation_file"]
        examples = [
            ['data/iris.csv', 'scenario_a_1/evaluation', '2',
             'check_files/evaluation_kfold.json']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_dataset(
                self, data=example["data"], output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_pred.i_create_kfold_cross_validation(
                self, k_folds=example["kfold"])
            test_pred.i_check_create_kfold_datasets(self, example["kfold"])
            test_pred.i_check_create_kfold_models(self, example["kfold"])
            test_pred.i_check_create_kfold_cross_validation(
                self, example["kfold"])
            evaluation.then_the_evaluation_file_is_like(
                self, example["json_evaluation_file"])

    def test_scenario2(self):
        """
        Scenario: Successfully building feature selection from dataset:
            Given I create BigML dataset uploading train "<data>" file in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I create BigML feature selection <kfold>-fold cross-validations improving "<metric>"
            And I check that the <kfold>-datasets have been created
            And I check that the <kfold>-models have been created
            And I check that all the <kfold>-fold cross-validations have been created
            Then the best feature selection is "<selection>", with "<metric>" of <metric_value>
            And I generate a report from the output directory
            And a symlink file is generated in the reports directory
        """
        print(self.test_scenario2.__doc__)
        headers = ["data", "output", "kfold", "metric", "selection",
                   "metric_value"]
        examples = [
            ['data/iris_2f.csv', 'scenario_a_2/evaluation', '2', 'accuracy',
             'petal width', '100.00%'],
            ['data/iris_2f.csv', 'scenario_a_3/evaluation', '2', 'phi',
             'petal width', '1']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_dataset(
                self, data=example["data"], output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_pred.i_create_kfold_cross_validation_metric(
                self, k_folds=example["kfold"], metric=example["metric"])
            test_pred.i_check_create_kfold_datasets(self, example["kfold"])
            test_pred.i_check_create_kfold_models(self, example["kfold"])
            test_pred.i_check_create_all_kfold_cross_validations(
                self, example["kfold"])
            test_pred.i_check_feature_selection(
                self, example["selection"], example["metric"],
                example["metric_value"])
            test_pred.i_generate_report(self)
            test_pred.is_symlink(self)

    def test_scenario3(self):
        """
        Scenario: Successfully building feature selection from dataset setting objective:
            Given I create BigML dataset uploading train "<data>" file in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I create BigML feature selection <kfold>-fold cross-validations for "<objective>" improving "<metric>"
            And I check that the <kfold>-datasets have been created
            And I check that the <kfold>-models have been created
            And I check that all the <kfold>-fold cross-validations have been created
            Then the best feature selection is "<selection>", with "<metric>" of <metric_value>
        """
        print(self.test_scenario3.__doc__)
        headers = ["data", "objective", "output", "kfold", "metric",
                   "selection", "metric_value"]
        examples = [
            ['data/iris_2f.csv', '0', 'scenario_a_5/evaluation', '2',
             'r_squared', 'species', '0.352845'],
            ['data/iris_2f.csv', '0', 'scenario_a_8/evaluation', '2',
             'mean_squared_error', 'species', '0.475200']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_dataset(
                self, data=example["data"], output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_pred.i_create_kfold_cross_validation_objective(
                self, k_folds=example["kfold"], objective=example["objective"],
                metric=example["metric"])
            test_pred.i_check_create_kfold_datasets(self, example["kfold"])
            test_pred.i_check_create_kfold_models(self, example["kfold"])
            test_pred.i_check_create_all_kfold_cross_validations(
                self, example["kfold"])
            test_pred.i_check_feature_selection(
                self, example["selection"], example["metric"],
                example["metric_value"])

    def test_scenario4(self):
        """
        Scenario: Successfully building feature selection from filtered dataset setting objective:
            Given I create BigML dataset uploading train "<data>" file in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I filter out field "<field>" from dataset and log to "<output_dir>"
            And I check that the new dataset has been created
            And I create BigML feature selection <kfold>-fold cross-validations for "<objective>" improving "<metric>"
            And I check that the <kfold>-datasets have been created
            And I check that the <kfold>-models have been created
            And I check that all the <kfold>-fold cross-validations have been created
            Then the best feature selection is "<selection>", with "<metric>" of <metric_value>
        """
        print(self.test_scenario4.__doc__)
        headers = ["data", "field", "objective", "output", "output_dir",
                   "kfold", "metric", "selection", "metric_value"]
        examples = [
            ['data/iris_2fd.csv', 'sepal length', 'species',
             'scenario_a_6/evaluation', 'scenario_a_6', '2', 'recall',
             'petal width', '100.00%']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_dataset(
                self, data=example["data"], output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            dataset_adv.i_filter_field_from_dataset(
                self, field=example["field"], output_dir=example["output_dir"])
            test_pred.i_check_create_new_dataset(self)
            test_pred.i_create_kfold_cross_validation_objective(
                self, k_folds=example["kfold"], objective=example["objective"],
                metric=example["metric"])
            test_pred.i_check_create_kfold_datasets(self, example["kfold"])
            test_pred.i_check_create_kfold_models(self, example["kfold"])
            test_pred.i_check_create_all_kfold_cross_validations(
                self, example["kfold"])
            test_pred.i_check_feature_selection(
                self, example["selection"], example["metric"],
                example["metric_value"])

    def test_scenario5(self):
        """
        Scenario: Successfully building nodes threshold analysis from dataset file:
            Given I create BigML dataset uploading train "<data>" file in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I create BigML nodes analysis from dataset file from <min_nodes> to <max_nodes> by <nodes_step> with <kfold>-cross-validation improving "<metric>"
            And I check that the <kfold>-datasets have been created
            And I check that the <kfold>-models have been created
            And I check that all the <kfold>-fold cross-validations have been created
            Then the best node threshold is "<node_threshold>", with "<metric>" of <metric_value>
        """
        print(self.test_scenario5.__doc__)
        headers = ["data", "output", "min_nodes", "max_nodes", "nodes_step",
                   "kfold", "metric", "node_threshold", "metric_value"]
        examples = [
            ['data/iris.csv', 'scenario_a_4/evaluation', '3', '14', '2', '2',
             'precision', '9', '94.71%']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_dataset(
                self, data=example["data"], output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_pred.i_create_nodes_analysis_from_dataset_file(
                self, min_nodes=example["min_nodes"],
                max_nodes=example["max_nodes"],
                nodes_step=example["nodes_step"],
                k_fold=example["kfold"],
                metric=example["metric"])
            test_pred.i_check_create_kfold_datasets(self, example["kfold"])
            test_pred.i_check_create_kfold_models(self, example["kfold"])
            test_pred.i_check_create_all_kfold_cross_validations(
                self, example["kfold"])
            test_pred.i_check_node_threshold(
                self, example["node_threshold"], example["metric"],
                example["metric_value"])

    def test_scenario6(self):
        """
            Scenario: Successfully building feature selection from dataset excluding features:
                Given I create BigML dataset uploading train "<data>" file in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I create BigML feature selection <kfold>-fold cross-validations excluding "<features>" with separator "<args_separator>" improving "<metric>"
                And I check that the <kfold>-datasets have been created
                And I check that the <kfold>-models have been created
                And I check that all the <kfold>-fold cross-validations have been created
                Then the best feature selection is "<selection>", with "<metric>" of <metric_value>
        """
        print(self.test_scenario6.__doc__)
        headers = ["data", "output", "kfold", "features", "args_separator",
                   "metric", "selection", "metric_value"]
        examples = [
            ['data/iris.csv', 'scenario_a_7/evaluation', '2',
             'petal length!sepal width', '!', 'accuracy', 'petal width',
             '95.33%']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_dataset(
                self, data=example["data"], output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_pred.i_create_kfold_cross_validation_separator_metric_no_fields(
                self, k_folds=example["kfold"], features=example["features"],
                args_separator=example["args_separator"],
                metric=example["metric"])
            test_pred.i_check_create_kfold_datasets(self, example["kfold"])
            test_pred.i_check_create_kfold_models(self, example["kfold"])
            test_pred.i_check_create_all_kfold_cross_validations(
                self, example["kfold"])
            test_pred.i_check_feature_selection(
                self, example["selection"], example["metric"],
                example["metric_value"])

    def test_scenario7(self):
        """
        Scenario: Successfully building feature selection for a category from dataset:
            Given I create BigML dataset uploading train "<data>" file with attributes "<attributes>" in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I create BigML feature selection <kfold>-fold cross-validations improving "<metric>" for category "<category>"
            And I check that the <kfold>-datasets have been created
            And I check that the <kfold>-models have been created
            And I check that all the <kfold>-fold cross-validations have been created
            Then the best feature selection is "<selection>", with "<metric>" of <metric_value>
        """
        print(self.test_scenario7.__doc__)
        headers = ["data", "attributes", "output", "kfold", "metric",
                   "category", "selection", "metric_value"]
        examples = [
            ['data/spam.csv', 'data/spam_attributes.json',
             'scenario_a_9/evaluation', '2', 'recall', 'spam',
             'Message', '58.69%']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_dataset_with_attributes(
                self, data=example["data"], attributes=example["attributes"],
                output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_pred.i_create_kfold_cross_validation_metric_category(
                self, k_folds=example["kfold"], metric=example["metric"],
                category=example["category"])
            test_pred.i_check_create_kfold_datasets(self, example["kfold"])
            test_pred.i_check_create_kfold_models(self, example["kfold"])
            test_pred.i_check_create_all_kfold_cross_validations(
                self, example["kfold"])
            test_pred.i_check_feature_selection(
                self, example["selection"], example["metric"],
                example["metric_value"])

    def test_scenario8(self):
        """
        Scenario: Successfully building a new dataset from an existing one and analyzing it
            Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I create a new BigML dataset using the specs in JSON file "<new_fields>" and a model with "<model_fields>"
            And I check that the new dataset has been created
            And I check that the model has been created
            And I create BigML nodes analysis from <min_nodes> to <max_nodes> by <nodes_step> with <kfold>-cross-validation improving "<metric>"
            And I check that the <kfold>-datasets have been created
            And I check that the <kfold>-models have been created
            And I check that all the <kfold>-fold cross-validations have been created
            Then the best node threshold is "<node_threshold>", with "<metric>" of <metric_value>
        """
        print(self.test_scenario8.__doc__)
        headers = ["data", "output_dir", "new_fields", "field", "model_fields",
                   "min_nodes", "max_nodes", "nodes_step", "kfold", "metric",
                   "node_threshold", "metric_value"]
        examples = [
            ['data/iris.csv', 'scenario_a_10', 'data/new_fields2.json',
             'outlier?', 'outlier?,species', '3', '14', '2', '2', 'precision',
             '5', '98.21%']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            dataset_adv.i_create_dataset(
                self, data=example["data"], output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            dataset_adv.i_create_dataset_new_fields(
                self, json_file=example["new_fields"],
                model_fields=example["model_fields"])
            test_pred.i_check_create_new_dataset(self)
            test_pred.i_check_create_model(self)
            test_pred.i_create_nodes_analysis(
                self, min_nodes=example["min_nodes"],
                max_nodes=example["max_nodes"],
                nodes_step=example["nodes_step"],
                k_fold=example["kfold"],
                metric=example["metric"])
            test_pred.i_check_create_kfold_datasets(self, example["kfold"])
            test_pred.i_check_create_kfold_models(self, example["kfold"])
            test_pred.i_check_create_all_kfold_cross_validations(
                self, example["kfold"])
            test_pred.i_check_node_threshold(
                self, example["node_threshold"], example["metric"],
                example["metric_value"])

    def test_scenario9(self):
        """
        Scenario: Successfully building random fields analysis from dataset:
            Given I create BigML dataset uploading train "<data>" file in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I create BigML random fields analysis with <kfold>-cross-validation improving "<metric>"
            And I check that the <kfold>-datasets have been created
            And I check that the <kfold>-random trees have been created
            And I check that all the <kfold>-fold cross-validations have been created
            Then the best random candidates number is "<random_candidates>", with "<metric>" of <metric_value>
        """
        print(self.test_scenario9.__doc__)
        headers = ["data", "output", "kfold", "metric", "random_candidates",
                   "metric_value"]
        examples = [
            ['data/iris.csv', 'scenario_a_11/evaluation', '2', 'precision',
             '4', '96.09%']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_dataset(self, data=example["data"],
                output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_pred.i_create_random_analysis(
                self, k_fold=example["kfold"], metric=example["metric"])
            test_pred.i_check_create_kfold_datasets(self, example["kfold"])
            test_pred.i_check_create_kfold_random_forest(
                self, example["kfold"])
            test_pred.i_check_create_all_kfold_cross_validations(
                self, example["kfold"])
            test_pred.i_check_random_candidates(
                self, example["random_candidates"], example["metric"],
                example["metric_value"])

    def test_scenario10(self):
        """
        Scenario: Successfully building feature selection from dataset setting objective:
            Given I create BigML dataset uploading train "<data>" file in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I create BigML feature selection <kfold>-fold cross-validation with options "<options>"
            And I check that the <kfold>-datasets have been created
            And I check that the <kfold>-models have been created
            And I check that all the <kfold>-fold cross-validations have been created
            Then the predictions file "<predictions_file>" is like "<estimated_file>"
        """
        print(self.test_scenario10.__doc__)
        headers = ["data", "output", "kfold", "options", "predictions_file",
                   "estimated_file"]
        examples = [
            ['data/iris.csv', 'scenario_a_12/evaluation', '2',
             ' --exclude-features="petal length,sepal length"' +
             ' --predictions-csv',
             'scenario_a_12/test/kfold2_pred/predictions.csv',
             'check_files/analyze_predictions_iris.csv'],
            ['data/iris.csv', 'scenario_a_13/evaluation', '2',
             ' --exclude-features="species,sepal length"' +
             ' --predictions-csv --objective 0',
             'scenario_a_13/test/kfold6_pred/predictions.csv',
             'check_files/analyze_predictions_iris2.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_dataset(
                self, data=example["data"], output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_pred.i_create_kfold_cross_validation_options(
                self, k_folds=example["kfold"], options=example["options"])
            test_pred.i_check_create_kfold_datasets(self, example["kfold"])
            test_pred.i_check_create_kfold_models(self, example["kfold"])
            test_pred.i_check_create_all_kfold_cross_validations(
                self, example["kfold"])
            test_pred.i_check_predictions_file(
                self, example["predictions_file"],
                example["estimated_file"])


    def test_scenario11(self):
        """
        Scenario: Successfully building feature selection from dataset setting objective:
            Given I create BigML dataset uploading train "<data>" file in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I create BigML feature selection <kfold>-fold cross-validation with options "<options>"
            And I check that the <kfold>-datasets have been created
            And I check that the <kfold>-ensembles have been created
            And I check that all the <kfold>-fold cross-validations have been created
            Then the predictions file "<predictions_file>" is like "<estimated_file>"
        """
        print(self.test_scenario11.__doc__)
        headers = ["data", "output", "kfold", "options", "predictions_file",
                   "estimated_file"]
        examples = [
            ['data/iris.csv', 'scenario_a_14/evaluation', '2', ' --exclude-features="petal length,sepal length" --predictions-csv --number-of-models 2','scenario_a_14/test/kfold2_pred/predictions.csv', 'check_files/analyze_predictions_iris_e.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_dataset(
                self, data=example["data"], output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_pred.i_create_kfold_cross_validation_options(
                self, k_folds=example["kfold"], options=example["options"])
            test_pred.i_check_create_kfold_datasets(self, example["kfold"])
            test_pred.i_check_create_kfold_ensembles(self, example["kfold"])
            test_pred.i_check_create_all_kfold_cross_validations(
                self, example["kfold"])
            test_pred.i_check_predictions_file(
                self, example["predictions_file"], example["estimated_file"])
