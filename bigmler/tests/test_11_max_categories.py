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


""" Testing splitting models according to max categories

"""



from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, teardown_class)


import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.max_categories_tst_prediction_steps as max_cat


def setup_module():
    """Setup for the module

    """
    common_setup_module()
    test = TestMaxCategories()
    test.setup_scenario1()


def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()


class TestMaxCategories(object):

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

    def setup_scenario1(self):
        """
            Scenario: Successfully building test predictions from training data using datasets with max categories
                Given I create BigML resources from "<data>" with <max_categories> as categories limit and <objective> as objective field to test "<test>" and log predictions in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the max_categories datasets have been created
                And I check that the models have been created
                And I check that the predictions are ready
                Then the local prediction file is like "<predictions_file>"

                Examples:
                |data |max_categories | objective | test                        | output                          |predictions_file           |
                |../data/iris.csv |1| species |../data/test_iris.csv | ./scenario_mc_1/predictions.csv | ./check_files/predictions_mc.csv |
        """
        print(self.setup_scenario1.__doc__)
        examples = [
            ['data/iris.csv', '1', 'species', 'data/test_iris.csv', 'scenario_mc_1/predictions.csv', 'check_files/predictions_mc.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            max_cat.i_create_all_mc_resources(self, example[0], max_categories=example[1], objective=example[2], test=example[3], output=example[4])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            max_cat.i_check_create_max_categories_datasets(self)
            test_pred.i_check_create_models(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[5])

    def test_scenario2(self):
        """
            Scenario: Successfully building test predictions from source using datasets with max categories
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources with <max_categories> as categories limit and <objective> as objective field using source to test "<test>" and log predictions in "<output>"
                And I check that the dataset has been created
                And I check that the max_categories datasets have been created
                And I check that the models have been created
                And I check that the predictions are ready
                Then the local prediction file is like "<predictions_file>"

                Examples:
                |scenario    | kwargs                                                  |max_categories| objective | test                    | output                        |predictions_file           |
                | scenario_mc_1| {"data": "../data/iris.csv", "max_categories": "1", "objective": "species", "output": "./scenario_mc_1/predictions.csv", "test": "../data/test_iris.csv"}   |1| species | ../data/test_iris.csv   | ./scenario_mc_2/predictions.csv   | ./check_files/predictions_mc.csv   |
        """
        print(self.test_scenario2.__doc__)
        examples = [
            ['scenario_mc_1', '{"data": "data/iris.csv", "max_categories": "1", "objective": "species", "output": "scenario_mc_1/predictions.csv", "test": "data/test_iris.csv"}', '1', 'species', 'data/test_iris.csv', 'scenario_mc_2/predictions.csv', 'check_files/predictions_mc.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            max_cat.i_create_all_mc_resources_from_source(self, max_categories=example[2], objective=example[3], test=example[4], output=example[5])
            test_pred.i_check_create_dataset(self, suffix=None)
            max_cat.i_check_create_max_categories_datasets(self)
            test_pred.i_check_create_models(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[6])

    def test_scenario3(self):
        """
            Scenario: Successfully building test predictions from dataset using datasets with max categories
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources with <max_categories> as categories limit and <objective> as objective field using dataset to test "<test>" and log predictions in "<output>"
                And I check that the max_categories datasets have been created
                And I check that the models have been created
                And I check that the predictions are ready
                Then the local prediction file is like "<predictions_file>"

                Examples:
                |scenario    | kwargs                                                  |max_categories|objective | test                    | output                        |predictions_file           |
                | scenario_mc_1| {"data": "../data/iris.csv", "max_categories": "1", "objective": "species", "output": "./scenario_mc_1/predictions.csv", "test": "../data/test_iris.csv"}   |1| species |../data/test_iris.csv   | ./scenario_mc_3/predictions.csv   | ./check_files/predictions_mc.csv   |
        """
        print(self.test_scenario3.__doc__)
        examples = [
            ['scenario_mc_1', '{"data": "data/iris.csv", "max_categories": "1", "objective": "species", "output": "scenario_mc_1/predictions.csv", "test": "data/test_iris.csv"}', '1', 'species', 'data/test_iris.csv', 'scenario_mc_3/predictions.csv', 'check_files/predictions_mc.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            max_cat.i_create_all_mc_resources_from_dataset(self, max_categories=example[2], objective=example[3], test=example[4], output=example[5])
            max_cat.i_check_create_max_categories_datasets(self)
            test_pred.i_check_create_models(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[6])

    def test_scenario4(self):
        """
            Scenario: Successfully building ensembles test predictions from models file with max categories
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using models in file "<models_file>" to test "<test>" and log predictions with combine method in "<output>"
                And I check that the predictions are ready
                Then the local prediction file is like "<predictions_file>"

                Examples:
                |scenario    | kwargs                                                  |models_file| test                    | output                        |predictions_file           |
                | scenario_mc_1| {"data": "../data/iris.csv", "max_categories": "1", "objective": "species", "output": "./scenario_mc_1/predictions.csv", "test": "../data/test_iris.csv"}   | scenario_mc_1/models | ../data/test_iris.csv   | ./scenario_mc_4/predictions.csv   | ./check_files/predictions_mc.csv   |
        """
        print(self.test_scenario4.__doc__)
        examples = [
            ['scenario_mc_1', '{"data": "data/iris.csv", "max_categories": "1", "objective": "species", "output": "scenario_mc_1/predictions.csv", "test": "data/test_iris.csv"}', 'scenario_mc_1/models', 'data/test_iris.csv', 'scenario_mc_4/predictions.csv', 'check_files/predictions_mc.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            max_cat.i_create_all_mc_resources_from_models(self, models_file=example[2], test=example[3], output=example[4])
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[5])

    def test_scenario5(self):
        """
            Scenario: Successfully building test predictions from dataset using datasets and model fields with max categories
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources with <max_categories> as categories limit and <objective> as objective field and model fields "<model_fields>" using dataset to test "<test>" and log predictions in "<output>"
                And I check that the max_categories datasets have been created
                And I check that the models have been created
                And I check that the predictions are ready
                Then the local prediction file is like "<predictions_file>"

                Examples:
                |scenario    | kwargs                                                  |max_categories|objective | model_fields | test                    | output                        |predictions_file           |
                | scenario_mc_1| {"data": "../data/iris.csv", "max_categories": "1", "objective": "species", "output": "./scenario_mc_1/predictions.csv", "test": "../data/test_iris.csv"}   |1| species |sepal length,sepal width |../data/test_iris.csv   | ./scenario_mc_5/predictions.csv   | ./check_files/predictions_mc2.csv   |

        """
        print(self.test_scenario5.__doc__)
        examples = [
            ['scenario_mc_1', '{"data": "data/iris.csv", "max_categories": "1", "objective": "species", "output": "scenario_mc_1/predictions.csv", "test": "data/test_iris.csv"}', '1', 'species', 'sepal length,sepal width', 'data/test_iris.csv', 'scenario_mc_5/predictions.csv', 'check_files/predictions_mc2.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            max_cat.i_create_all_mc_resources_from_dataset_with_model_fields(self, max_categories=example[2], objective=example[3], model_fields=example[4], test=example[5], output=example[6])
            max_cat.i_check_create_max_categories_datasets(self)
            test_pred.i_check_create_models(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[7])
