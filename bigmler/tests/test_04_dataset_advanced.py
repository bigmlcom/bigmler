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


""" Testing advanced dataset creation (multidatasets)

"""
from world import world, setup_module, teardown_module, teardown_class


import dataset_advanced_steps as dataset_adv
import basic_tst_prediction_steps as test_pred


class TestDatasetAdvanced(object):

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
            Scenario: Successfully building a new dataset from an existing one
                Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I create a new BigML dataset using the specs in JSON file "<new_fields>" and a model with "<model_fields>"
                And I check that the new dataset has been created
                And I check that the model has been created
                Then I check that the new dataset has field "<field>"

                Examples:
                |data |output_dir  |new_fields | field | model_fields
                |../data/iris.csv | ./scenario_d_1 |../data/new_fields.json| outlier? |petal length,outlier?,species
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', 'scenario_d_1', 'data/new_fields.json', u'outlier?', u'petal length,outlier?,species']]
        for example in examples:
            print "\nTesting with:\n", example
            dataset_adv.i_create_dataset(self, data=example[0], output_dir=example[1])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            dataset_adv.i_create_dataset_new_fields(self, json_file=example[2], model_fields=example[4])
            test_pred.i_check_create_new_dataset(self)
            test_pred.i_check_create_model(self)
            dataset_adv.i_check_dataset_has_field(self, example[3])

    def test_scenario2(self):
        """
            Scenario: Successfully updating a dataset with attributes in a JSON file
                Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I update the dataset using the specs in JSON file "<new_fields>"
                Then I check that property "<property>" for field id "<field_id>" is "<value>" of type "<type>"

                Examples:
                |data |output_dir  |new_fields | property | field_id | value | type
                |../data/iris.csv | ./scenario_d_2 |../data/attributes.json| preferred | 000001 | false | boolean
        """
        print self.test_scenario2.__doc__
        examples = [
            ['data/iris.csv', 'scenario_d_2', 'data/attributes.json', 'preferred', '000001', 'false', 'boolean']]
        for example in examples:
            print "\nTesting with:\n", example
            dataset_adv.i_create_dataset(self, data=example[0], output_dir=example[1])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            dataset_adv.i_update_dataset_new_properties(self, json_file=example[2])
            dataset_adv.i_check_dataset_has_property(self, attribute=example[3], field_id=example[4], value=example[5], type=example[6])

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
                |../data/iris.csv | ./scenario_d_4 |dataset.csv
        """
        print self.test_scenario3.__doc__
        examples = [
            ['data/iris.csv', 'scenario_d_4', 'dataset.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            dataset_adv.i_create_dataset(self, data=example[0], output_dir=example[1])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            dataset_adv.i_export_the_dataset(self, example[2])
            dataset_adv.i_files_equal(self, example[2], example[0])

    def test_scenario4(self):
        """
            Scenario: Successfully building a multi-dataset
                Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I create a BigML dataset from "<data>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I create a multi-dataset from the datasets file and store logs in "<output_dir2>"
                And I check that the multi-dataset has been created
                Then I check that the multi-dataset's origin are the datasets in "<output_dir>"

                Examples:
                |data |output_dir  |output_dir2 |
                |../data/iris.csv | ./scenario_d_3 | ./scenario_d_4|
        """
        print self.test_scenario4.__doc__
        examples = [
            ['data/iris.csv', 'scenario_d_3', 'scenario_d_4']]
        for example in examples:
            print "\nTesting with:\n", example
            dataset_adv.i_create_dataset(self, data=example[0], output_dir=example[1])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            dataset_adv.i_create_dataset(self, data=example[0], output_dir=example[1])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            dataset_adv.i_create_multi_dataset(self, example[2])
            dataset_adv.i_check_create_multi_dataset(self)
            dataset_adv.i_check_multi_dataset_origin(self, output_dir=example[1])
