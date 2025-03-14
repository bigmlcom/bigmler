# -*- coding: utf-8 -*-
#!/usr/bin/env python
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#
# Copyright 2015-2025 BigML
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


""" Testing advanced dataset creation (multidatasets)

"""
from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)


import bigmler.tests.dataset_advanced_steps as dataset_adv
import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.basic_anomaly_prediction_steps as test_anomaly
import bigmler.tests.basic_logistic_r_steps as test_logistic



def setup_module():
    """Setup for the module

    """
    common_setup_module()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()


class TestDatasetAdvanced:
    """Testing advanced dataset commands"""

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
            Scenario: Successfully building a new dataset from an existing one
                Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I create a new BigML dataset using the specs in JSON file "<new_fields>" and a model with "<model_fields>"
                And I check that the new dataset has been created
                And I check that the model has been created
                Then I check that the new dataset has field "<field>"
        """
        print(self.test_scenario1.__doc__)
        headers = ["data", "output_dir", "new_fields", "field",
            "model_fields"]
        examples = [
            ['data/iris.csv', 'scenario_d_1', 'data/new_fields.json', 'outlier?', 'petal length,outlier?,species']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            dataset_adv.i_create_dataset(self, data=example["data"],
                output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            dataset_adv.i_create_dataset_new_fields(
                self, json_file=example["new_fields"],
                model_fields=example["model_fields"])
            test_pred.i_check_create_new_dataset(self)
            test_pred.i_check_create_model(self)
            dataset_adv.i_check_dataset_has_field(self, example["field"])

    def test_scenario2(self):
        """
            Scenario: Successfully updating a dataset with attributes in a JSON file
                Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I update the dataset using the specs in JSON file "<new_fields>"
                Then I check that property "<property>" for field id "<field_id>" is "<value>" of type "<type>"
        """
        print(self.test_scenario2.__doc__)
        headers = ["data", "output_dir", "new_fields", "property",
                   "field_id", "value", "type"]
        examples = [
            ['data/iris.csv', 'scenario_d_2', 'data/attributes.json', 'preferred', '000001', 'false', 'boolean'],
            ['data/iris.csv', 'scenario_d_2_b', 'data/attributes_col.json', 'preferred', '000001', 'false', 'boolean']
        ]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            dataset_adv.i_create_dataset(
                self, data=example["data"], output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            dataset_adv.i_update_dataset_new_properties(
                self, json_file=example["new_fields"])
            dataset_adv.i_check_dataset_has_property(
                self, attribute=example["property"],
                field_id=example["field_id"], value=example["value"],
                attr_type=example["type"])

    def test_scenario3(self):
        """
            Scenario: Successfully exporting a dataset to a CSV file
                Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I export the dataset to the CSV file "<csv_file>"
                Then file "<csv_file>" is like file "<data>"

                Examples:
                |data |output_dir  |csv_file |
                |../data/iris.csv | ./scenario_d_3 |dataset.csv
        """
        print(self.test_scenario3.__doc__)
        headers = ["data", "output_dir", "csv_file"]
        examples = [
            ['data/iris.csv', 'scenario_d_3', 'dataset.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            dataset_adv.i_create_dataset(
                self, data=example["data"], output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            dataset_adv.i_export_the_dataset(self, example["csv_file"])
            dataset_adv.i_files_equal(self, example["csv_file"],
                                      example["data"])

    def test_scenario4(self):
        """
            Scenario: Successfully building a multi-dataset
                Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I create a BigML dataset from previous source and store logs in "<output_dir>"
                And I check that the dataset has been created
                And I create a multi-dataset from the datasets file and store logs in "<output_dir2>"
                And I check that the multi-dataset has been created
                Then I check that the multi-dataset's origin are the datasets in "<output_dir>"
        """
        print(self.test_scenario4.__doc__)
        headers = ["data", "output_dir", "output_dir2"]
        examples = [
            ['data/iris.csv', 'scenario_d_4', 'scenario_d_4a']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            dataset_adv.i_create_dataset(self, data=example["data"],
                                         output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            dataset_adv.i_create_dataset_from_source(
                self, output_dir=example["output_dir"])
            test_pred.i_check_create_dataset(self, suffix=None)
            dataset_adv.i_create_multi_dataset(
                self, example["output_dir2"])
            dataset_adv.i_check_create_multi_dataset(self)
            dataset_adv.i_check_multi_dataset_origin(
                self, output_dir=example["output_dir"])

    def test_scenario5(self):
        """
            Scenario: Successfully building a filtered dataset from a dataset
                Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I create a BigML filtered dataset with filter "<filter_exp>" from previous dataset and store logs in "<output_dir>"
                And I check that the dataset has been created
                And the number of records in the dataset is <filtered_records>
        """
        print(self.test_scenario5.__doc__)
        headers = ["data", "output_dir", "filtered_records", "filter_exp"]
        examples = [
            ['data/iris.csv', 'scenario_d_5', '50',
             '(= (f "000004") "Iris-setosa")']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            dataset_adv.i_create_dataset(self, data=example["data"],
                                         output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            dataset_adv.i_create_filtered_dataset_from_dataset(
                self, filter_exp=example["filter_exp"],
                output_dir=example["output_dir"])
            test_pred.i_check_create_dataset(self, suffix='gen ')
            test_anomaly.i_check_dataset_lines_number(
                self, example["filtered_records"])

    def test_scenario6(self):
        """
            Scenario: Successfully exporting fields summary from a dataset
                Given I create a BigML dataset from "<data>" and a summary file "<summary_file>" for its fields and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                Then the expected field "<expected_file>" is like "<summary_file>"
        """
        print(self.test_scenario6.__doc__)
        headers = ["data", "output_dir", "summary_file", "expected_file"]
        examples = [
            ['data/iris.csv', 'scenario_d_6', 'fields_summary.csv',
             'check_files/fields_summary.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            dataset_adv.i_create_dataset_with_summary(
                self, data=example["data"],
                summary_file=example["summary_file"],
                output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            dataset_adv.i_files_equal(
                self, example["summary_file"], example["expected_file"])

    def test_scenario7(self):
        """
            Scenario: Successfully importing fields summary to a dataset
                Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I import fields attributes in file "<summary_file>" to dataset
                Then the field "<field_id>" has "<attribute>" equal to "<attribute_value>"
        """
        print(self.test_scenario7.__doc__)
        headers = ["data", "output_dir", "summary_file", "field_id",
                   "attribute", "attribute_value"]
        examples = [
            ['data/iris.csv', 'scenario_d_7',
             'data/fields_summary_modified.csv', '000000',
             'name', 'sepal_length']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            dataset_adv.i_create_dataset(
                self, data=example["data"], output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            dataset_adv.i_import_fields(self, summary=example["summary_file"])
            dataset_adv.field_attribute_value(
                self, field=example["field_id"],
                attribute=example["attribute"],
                attribute_value=example["attribute_value"])

    def test_scenario8(self):
        """
            Scenario: Successfully building a cluster from a sampled dataset
                Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I create a BigML cluster with params "<params>" from dataset in "<output_dir>"
                And I check that the cluster has been created
                And the cluster params are "<params_json>"
        """
        print(self.test_scenario8.__doc__)
        headers = ["data", "output_dir", "params", "params_json"]
        examples = [
            ['data/iris.csv', 'scenario_d_8',
             '--sample-rate 0.2 --replacement',
             '{"sample_rate": 0.2, "replacement": true}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            dataset_adv.i_create_dataset(self, data=example["data"],
                                         output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            dataset_adv.i_create_cluster_with_params_from_dataset(
                self, cluster_params=example["params"],
                output_dir=example["output_dir"])
            test_pred.i_check_create_cluster(self)
            dataset_adv.i_check_cluster_params(
                self, params_json=example["params_json"])

    def test_scenario9(self):
        """
            Scenario: Successfully building an anomaly detector from a sampled dataset
                Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I create a BigML anomaly with params "<params>" from dataset in "<output_dir>"
                And I check that the anomaly has been created
                And the anomaly params are "<params_json>"
        """
        print(self.test_scenario9.__doc__)
        headers = ["data", "output_dir", "params", "params_json"]
        examples = [
            ['data/iris.csv', 'scenario_d_9',
             '--sample-rate 0.2 --replacement',
             '{"sample_rate": 0.2, "replacement": true}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            dataset_adv.i_create_dataset(self, data=example["data"],
                                         output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            dataset_adv.i_create_anomaly_with_params_from_dataset(
                self, params=example["params"],
                output_dir=example["output_dir"])
            test_pred.i_check_create_anomaly(self)
            dataset_adv.i_check_anomaly_params(
                self, params_json=example["params_json"])

    def test_scenario10(self):
        """
            Scenario: Successfully building logistic regression from a sampled dataset
                Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I create a BigML logistic regression with params "<params>" from dataset in "<output_dir>"
                And I check that the logistic regression has been created
                And the logistic regression params are "<params_json>"
        """
        print(self.test_scenario10.__doc__)
        headers = ["data", "output_dir", "params", "params_json"]
        examples = [
            ['data/iris.csv', 'scenario_d_10',
             '--sample-rate 0.2 --replacement',
             '{"sample_rate": 0.2, "replacement": true}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            dataset_adv.i_create_dataset(self, data=example["data"],
                                         output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            dataset_adv.i_create_logistic_with_params_from_dataset(
                self, params=example["params"],
                output_dir=example["output_dir"])
            test_logistic.i_check_create_lr_model(self)
            dataset_adv.i_check_logistic_params(
                self, params_json=example["params_json"])

    def test_scenario11(self):
        """
            Scenario: Successfully building association from a sampled dataset
                Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I create a BigML association with params "<params>" from dataset in "<output_dir>"
                And I check that the association has been created
                And the association params are "<params_json>"
        """
        print(self.test_scenario11.__doc__)
        headers = ["data", "output_dir", "params", "params_json"]
        examples = [
            ['data/iris.csv', 'scenario_d_11',
             '--sample-rate 0.2 --replacement',
             '{"sample_rate": 0.2, "replacement": true}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            dataset_adv.i_create_dataset(self, data=example["data"],
                                         output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            dataset_adv.i_create_association_with_params_from_dataset(
                self, params=example["params"],
                output_dir=example["output_dir"])
            test_pred.i_check_create_association(self)
            dataset_adv.i_check_association_params(
                self, params_json=example["params_json"])

    def test_scenario12(self):
        """
            Scenario: Successfully building dataset juxtaposing datasets
                Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I create a BigML dataset from "<data>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I create a new dataset juxtaposing both datasets and store
logs in "<output_dir>"
                And I check that the dataset has been created
                And I check that datasets have been juxtaposed
        """
        print(self.test_scenario12.__doc__)
        headers = ["data", "output_dir"]
        examples = [
            ['data/iris.csv', 'scenario_d_12']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            datasets = []
            dataset_adv.i_create_dataset(self, data=example["data"],
                                         output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            datasets.append(world.dataset)
            dataset_adv.i_create_dataset(self, data=example["data"],
                                         output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            datasets.append(world.dataset)
            dataset_adv.i_create_juxtaposed(
                self, output_dir=example["output_dir"])
            test_pred.i_check_create_dataset(self, suffix="gen ")
            dataset_adv.i_check_juxtaposed(self, datasets)

    def test_scenario13(self):
        """
            Scenario: Successfully building dataset using sql transformations
                Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I create a BigML dataset from "<data>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I create a new dataset joining both datasets and store
logs in "<output_dir>"
                And I check that the dataset has been created
                And I check that datasets have been joined
        """
        print(self.test_scenario12.__doc__)
        headers = ["data", "output_dir", "sql_query", "rows"]
        #pylint: disable=locally-disabled,anomalous-backslash-in-string
        examples = [
            ['data/iris.csv', 'scenario_d_13', "select A.*,B.* from A join B "
             "on A.\`000000\` = B.\`000000\`", 900]]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            datasets = []
            dataset_adv.i_create_dataset(self, data=example["data"],
                                         output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            datasets.append(world.dataset)
            dataset_adv.i_create_dataset(self, data=example["data"],
                                         output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            datasets.append(world.dataset)
            dataset_adv.i_create_join(self, output_dir=example["output_dir"],
                                      sql=example["sql_query"])
            test_pred.i_check_create_dataset(self, suffix="gen ")
            dataset_adv.i_check_joined(self, example["rows"])
