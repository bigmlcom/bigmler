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


""" Testing prediction creation

"""


from bigmler.tests.world import world, common_setup_module, \
    common_teardown_module, show_method, show_doc


import bigmler.tests.basic_tst_prediction_steps as test_pred


def setup_module():
    """Setup for the module

    """
    common_setup_module()
    test = TestPrediction()
    test.bigml = {"method": "setup_scenario02"}
    test.setup_scenario02()
    test.bigml = {"method": "setup_scenario06"}
    test.setup_scenario06()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()


class TestPrediction:
    """Testing supervised predictions"""

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

    def test_scenario01(self):
        """
        Scenario: Successfully building test predictions from start with no headers:
            Given I create BigML resources uploading train "<data>" file with no headers to test "<test>" with no headers and log predictions in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the model has been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        headers = ["data", "test", "output", "predictions_file"]
        examples = [
            ['data/iris_nh.csv', 'data/test_iris_nh.csv',
             'scenario1_nh/predictions.csv',
             'check_files/predictions_iris.csv']]
        show_doc(self.test_scenario01, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_all_resources_with_no_headers(
                self, example["data"], example["test"], example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def setup_scenario02(self):
        """
        Scenario: Successfully building test predictions from start:
            Given I create BigML resources uploading train "<data>" file to test "<test>" and log predictions in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the model has been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        headers = ["data", "test", "output", "predictions_file"]
        examples = [
            ['data/grades.csv', 'data/test_grades.csv',
             'scenario1_r/predictions.csv',
             'check_files/predictions_grades.csv'],
            ['data/iris.csv', 'data/test_iris.csv',
             'scenario1/predictions.csv', 'check_files/predictions_iris.csv']]
        show_doc(self.setup_scenario02, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_all_resources(
                self, example["data"], example["test"], example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario03(self):
        """
        Scenario: Successfully building test predictions from source
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML resources using source to test "<test>" and log predictions in "<output>"
            And I check that the dataset has been created
            And I check that the model has been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        headers = ["scenario", "kwargs", "test", "output", "predictions_file"]
        examples = [
            ['scenario1', '{"data": "data/iris.csv",' +
             ' "output": "scenario1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}', 'data/test_iris.csv',
             'scenario2/predictions.csv', 'check_files/predictions_iris.csv']]
        show_doc(self.test_scenario03, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_create_resources_from_source(
                self, None, test=example["test"], output=example["output"])
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario04(self):
        """
        Scenario: Successfully building test predictions from dataset
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML resources using dataset to test "<test>" and log predictions in "<output>"
            And I check that the model has been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        headers = ["scenario", "kwargs", "test", "output", "predictions_file"]
        examples = [
            ['scenario1', '{"data": "data/iris.csv",' +
             ' "output": "scenario1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}', 'data/test_iris.csv',
             'scenario3/predictions.csv', 'check_files/predictions_iris.csv']]
        show_doc(self.test_scenario04, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_create_resources_from_dataset(
                self, None, test=example["test"], output=example["output"])
            test_pred.i_check_create_model(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario05(self):
        """
        Scenario: Successfully building test predictions from model
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML resources using model to test "<test>" and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        headers = ["scenario", "kwargs", "test", "output", "predictions_file"]
        examples = [
            ['scenario1', '{"data": "data/iris.csv",' +
             ' "output": "scenario1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}', 'data/test_iris.csv',
             'scenario4/predictions.csv', 'check_files/predictions_iris.csv']]
        show_doc(self.test_scenario05, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_create_resources_from_model(
                self, test=example["test"], output=example["output"])
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def setup_scenario06(self):
        """
        Scenario: Successfully building test predictions from ensemble
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML resources using ensemble of <number_of_models> models to test "<test>" and log predictions in "<output>"
            And I check that the ensemble has been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        headers = ["scenario", "kwargs", "number_of_models", "test", "output",
                   "predictions_file"]
        examples = [
            ['scenario1', '{"data": "data/iris.csv",' +
             ' "output": "scenario1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}', '10', 'data/test_iris.csv',
             'scenario5/predictions.csv', 'check_files/predictions_iris.csv']]
        show_doc(self.setup_scenario06, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_create_resources_from_ensemble(
                self, number_of_models=example["number_of_models"],
                test=example["test"],
                output=example["output"])
            test_pred.i_check_create_ensemble(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario07(self):
        """
        Scenario: Successfully building test predictions from models file
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I have previously executed "<scenario2>" or reproduce it with arguments <kwargs2>
            And I create BigML resources using models in file "<models_file>" to test "<test>" and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        print(self.test_scenario07.__doc__)
        headers = ["scenario", "kwargs", "scenario2", "kwargs2", "models_file",
                   "test", "output", "predictions_file"]
        examples = [
            ['scenario1', '{"data": "data/iris.csv",' +
             ' "output": "scenario1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}',
             'scenario5', '{"number_of_models": 10,' +
             ' "test": "data/test_iris.csv",' +
             ' "output": "scenario5/predictions.csv"}',
             'scenario5/models', 'data/test_iris.csv',
             'scenario6/predictions.csv', 'check_files/predictions_iris.csv']]
        show_doc(self.test_scenario07, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario2"], example["kwargs2"])
            test_pred.i_create_resources_from_models_file(
                self, multi_label=None, models_file=example["models_file"],
                test=example["test"], output=example["output"])
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario08(self):
        """
        Scenario: Successfully building test predictions from dataset file
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML resources using dataset in file "<dataset_file>" to test "<test>" and log predictions in "<output>"
            And I check that the model has been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        headers = ["scenario", "kwargs", "dataset_file", "test", "output",
                   "predictions_file"]
        examples = [
            ['scenario1', '{"data": "data/iris.csv",' +
             ' "output": "scenario1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}', 'scenario1/dataset',
             'data/test_iris.csv', 'scenario7/predictions.csv',
             'check_files/predictions_iris.csv']]
        show_doc(self.test_scenario08, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_create_resources_from_dataset_file(
                self, dataset_file=example["dataset_file"],
                test=example["test"], output=example["output"])
            test_pred.i_check_create_model(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario09(self):
        """
        Scenario: Successfully combining test predictions from existing directories
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I have previously executed "<scenario2>" or reproduce it with arguments <kwargs2>
            Given I combine BigML predictions files in "<directory1>" and "<directory2>" into "<output>"
            Then the local prediction file is like "<predictions_file>"
        """
        headers =["scenario", "kwargs", "scenario2", "kwargs2", "directory1",
                  "directory2", "output", "predictions_file"]
        examples = [
            ['scenario1', '{"data": "data/iris.csv",' +
             ' "output": "scenario1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}',
             'scenario5', '{"number_of_models": 10,' +
             ' "test": "data/test_iris.csv",' +
             ' "output": "scenario5/predictions.csv"}',
             'scenario1', 'scenario5', 'scenario8/predictions.csv',
             'check_files/predictions_iris.csv']]
        show_doc(self.test_scenario09, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario2"], example["kwargs2"])
            test_pred.i_find_predictions_files(
                self, directory1=example["directory1"],
                directory2=example["directory2"],
                output=example["output"])
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario10(self):
        """
        Scenario: Successfully combining test predictions from existing directories
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I have previously executed "<scenario2>" or reproduce it with arguments <kwargs2>
            And I combine BigML predictions files in "<directory1>" and "<directory2>" into "<output>" with method "<method>"
            Then the local prediction file is like "<predictions_file>"
        """
        headers = ["scenario", "kwargs", "scenario2", "kwargs2", "directory1",
                   "directory2", "output", "predictions_file", "method"]
        examples = [
            ['scenario1', '{"data": "data/iris.csv",' +
             ' "output": "scenario1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}',
             'scenario5', '{"number_of_models": 10,' +
             ' "output": "scenario5/predictions.csv",' +
             ' "test": "data/test_iris.csv"}',
             'scenario1', 'scenario5', 'scenario9/predictions_c.csv',
             'check_files/predictions_iris.csv', '"confidence weighted"'],
            ['scenario1', '{"data": "data/iris.csv",' +
             ' "output": "scenario1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}',
             'scenario5', '{"number_of_models": 10,' +
             ' "output": "scenario5/predictions.csv",' +
             ' "test": "data/test_iris.csv"}',
             'scenario1', 'scenario5', 'scenario9/predictions_p.csv',
             'check_files/predictions_iris_p.csv', '"probability weighted"'],
            ['scenario1_r', '{"data": "data/grades.csv",' +
              ' "output": "scenario1_r/predictions.csv",' +
              ' "test": "data/test_grades.csv"}',
              'scenario1_r', '{"data": "data/grades.csv",' +
              ' "output": "scenario1_r/predictions.csv",' +
              ' "test": "data/test_grades.csv"}',
             'scenario1_r', 'scenario1_r', 'scenario10/predictions_c.csv',
             'check_files/predictions_grades.csv', '"confidence weighted"'],
            ['scenario1_r', '{"data": "data/grades.csv",' +
             ' "output": "scenario1_r/predictions.csv",' +
             ' "test": "data/test_grades.csv"}',
             'scenario1_r', '{"data": "data/grades.csv",' +
             ' "output": "scenario1_r/predictions.csv",' +
             ' "test": "data/test_grades.csv"}',
             'scenario1_r', 'scenario1_r', 'scenario10/predictions_p.csv',
             'check_files/predictions_grades_p.csv', '"probability weighted"']]
        show_doc(self.test_scenario10, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario2"], example["kwargs2"])
            test_pred.i_find_predictions_files_with_method(
                self, directory1=example["directory1"],
                directory2=example["directory2"],
                output=example["output"], method=example["method"])
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario11(self):
        """
        Scenario: Successfully building test predictions from dataset specifying objective field and model fields
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML resources using dataset, objective field <objective> and model fields <fields> to test "<test>" and log predictions in "<output>"
            And I check that the model has been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        headers = ["scenario", "kwargs", "test", "output", "predictions_file",
                   "objective", "fields"]
        examples = [
            ['scenario1', '{"data": "data/iris.csv",' +
             ' "output": "scenario1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}', 'data/test_iris.csv',
             'scenario11/predictions.csv',
             'check_files/predictions_iris_b.csv', '0',
             '"petal length","petal width"']]
        show_doc(self.test_scenario11, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_create_resources_from_dataset_objective_model(
                self, objective=example["objective"], fields=example["fields"],
                test=example["test"], output=example["output"])
            test_pred.i_check_create_model(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario12(self):
        """
        Scenario: Successfully building cross-validation from dataset
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create a BigML cross-validation with rate <rate> using the dataset in file "<dataset_file>" and log results in "<output>"
            And I check that the models have been created
            And I check that the evaluations have been created
            Then the cross-validation json model info is like the one in "<cv_file>"
        """
        headers = ["scenario", "kwargs", "rate", "dataset_file", "output",
                   "cv_file"]
        examples = [
            ['scenario1', '{"data": "data/iris.csv",' +
             ' "output": "scenario1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}', '0.05', 'scenario1/dataset',
             'scenario12/cross-validation',
             'check_files/cross_validation.json']]
        show_doc(self.test_scenario12, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_create_cross_validation_from_dataset(
                self, rate=example["rate"],
                dataset_file=example["dataset_file"],
                output=example["output"])
            test_pred.i_check_create_models(self)
            test_pred.i_check_create_evaluations(
                self, number_of_evaluations=None)
            test_pred.i_check_cross_validation(
                self, example["cv_file"])

    def test_scenario13(self):
        """
        Scenario: Successfully building a source with a given locale and storing its result
            Given I create a BigML source from file "<data>" with locale "<locale>", field attributes "<field_attributes>" and types file "<types>" storing results in "<output>"
            Then I check that the stored source file exists
            And the locale of the source is "<bigml_locale>"
            And the type of field "<field_id>" is "<type>"
            And the label of field "<field_id>" is "<label>"
        """
        headers = ["data", "locale", "field_attributes", "types", "output",
                   "bigml_locale", "field_id", "type", "label"]
        examples = [
            ['data/iris.csv', 'es_ES.UTF-8', 'data/field_attributes.txt', 'data/types.txt', 'scenario13/store_file', 'es_ES', '000004', 'text', 'species label']]
        show_doc(self.test_scenario13, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_source_with_locale(
                self, data=example["data"], locale=example["locale"],
                field_attributes=example["field_attributes"],
                types=example["types"], output=example["output"])
            test_pred.i_check_stored_source(self)
            test_pred.i_check_source_locale(self, example["bigml_locale"])
            test_pred.i_check_source_type(
                self, example["field_id"], example["type"])
            test_pred.i_check_source_label(
                self, example["field_id"], example["label"])

    def test_scenario14(self):
        """
        Scenario: Successfully building test predictions from start with user-given separator:
            Given I create BigML resources uploading train "<data>" file to test "<test>" and log predictions in "<output>" with "<separator>" as test field separator
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the model has been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        headers = ["data", "test", "separator", "output", "predictions_file"]
        examples = [
            ['data/iris.csv', 'data/test_iris.tsv', '"\t"',
             'scenario14/predictions.csv', 'check_files/predictions_iris.csv']]
        show_doc(self.test_scenario14, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_all_resources_with_separator(
                self, data=example["data"], test=example["test"],
                output=example["output"], separator=example["separator"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario15(self):
        """
        Scenario: Successfully building test predictions from start with different prediction file format:
            Given I create BigML resources uploading train "<data>" file to test "<test>" and log predictions in "<output>" with prediction options "<options>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the model has been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        headers = ["data", "test", "output", "options", "predictions_file"]
        examples = [
            ['data/iris.csv', 'data/test_iris.csv',
             'scenario15/predictions.csv',
             '--prediction-header --prediction-fields \'petal length,' +
             'petal width\' --prediction-info full',
             'check_files/predictions_iris_h.csv']]
        show_doc(self.test_scenario15, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_all_resources_with_options(
                self, data=example["data"], test=example["test"],
                output=example["output"], options=example["options"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario16(self):
        """
        Scenario: Successfully building threshold test predictions from ensemble
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML resources using ensemble of <number_of_models> models with replacement to test "<test>" and log predictions in "<output>"
            And I check that the ensemble has been created
            And I check that the predictions are ready
            And I create BigML resources using the previous ensemble with different thresholds to test "<test>" and log predictions in "<output2>" and "<output3>"
            Then local predictions for different thresholds in "<output2>" and "<output3>" are different
        """
        headers = ["scenario", "kwargs", "number_of_models", "test", "output",
                   "output2", "output3"]
        examples = [
            ['scenario1', '{"data": "data/iris.csv",' +
             ' "output": "scenario1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}', '10', 'data/test_iris.csv',
             'scenario16/predictions.csv', 'scenario16/predictions2.csv',
             'scenario16/predictions3.csv']]
        show_doc(self.test_scenario16, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_create_resources_from_ensemble_with_replacement(
                self, number_of_models=example["number_of_models"],
                test=example["test"], output=example["output"])
            test_pred.i_check_create_ensemble(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_create_resources_from_ensemble_with_threshold(
                self, test=example["test"], output2=example["output2"],
                output3=example["output3"])
            test_pred.i_check_predictions_with_different_thresholds(
                self, example["output2"], example["output3"])

    def test_scenario17(self):
        """
        Scenario: Successfully building test predictions from local model
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML resources using local model in "<scenario>" to test "<test>" and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        headers = ["scenario", "kwargs", "test", "output", "predictions_file"]
        examples = [
            ['scenario1', '{"data": "data/iris.csv",' +
             ' "output": "scenario1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}', 'data/test_iris.csv',
             'scenario17/predictions.csv', 'check_files/predictions_iris.csv']]
        show_doc(self.test_scenario17, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_create_resources_from_local_model(
                self, directory=example["scenario"], test=example["test"],
                output=example["output"])
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario18(self):
        """
        Scenario: Successfully building test predictions from ensemble
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            Given I have previously executed "<scenario2>" or reproduce it with arguments <kwargs2>
            And I create BigML resources using local ensemble of <number_of_models> models in "<scenario2>" to test "<test>" and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        headers = ["scenario", "kwargs", "scenario2", "kwargs2",
                   "number_of_models", "directory", "test",
                   "output", "predictions_file"]
        examples = [
            ['scenario1', '{"data": "data/iris.csv",' +
             ' "output": "scenario1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}',
             'scenario5', '{"number_of_models": 10,' +
             ' "output": "scenario5/predictions.csv",' +
             ' "test": "data/test_iris.csv"}',
             '10', 'scenario5', 'data/test_iris.csv',
             'scenario18/predictions.csv', 'check_files/predictions_iris.csv']]
        show_doc(self.test_scenario18, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario2"], example["kwargs2"])
            test_pred.i_create_resources_from_local_ensemble(
                self, number_of_models=example["number_of_models"],
                directory=example["directory"], test=example["test"],
                output=example["output"])
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario19(self):
        """
            Scenario: Successfully building test predictions from start using median:
                Given I create BigML resources uploading train "<data>" file using the median to test "<test>" and log predictions in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the model has been created
                And I check that the predictions are ready
                Then the local prediction file is like "<predictions_file>"
        """
        headers = ["data", "test", "output", "predictions_file"]
        examples = [
            ['data/grades.csv', 'data/test_grades.csv',
             'scenario19/predictions.csv',
             'check_files/predictions_grades_median.csv']]
        show_doc(self.test_scenario19, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_all_resources_with_median(
                self, data=example["data"], test=example["test"],
                output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario20(self):
        """
        Scenario: Successfully building test predictions using median from ensemble
                Given I create BigML resources from "<data>" using ensemble of <number_of_models> models to test "<test>" using median and log predictions in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the ensemble has been created
                And I check that the models in the ensembles have been created
                And I check that the predictions are ready
                Then the local prediction file is like "<predictions_file>"
        """
        headers = ["data", "number_of_models", "test", "output",
                   "predictions_file"]
        examples = [
            ['data/grades.csv', '5', 'data/test_grades.csv',
             'scenario20/predictions.csv',
             'check_files/predictions_grades_median_e.csv']]
        show_doc(self.test_scenario20, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_resources_from_ensemble_using_median(
                self, data=example["data"],
                number_of_models=example["number_of_models"],
                test=example["test"], output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_ensemble(self)
            test_pred.i_check_create_models_in_ensembles(self, in_ensemble=True)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario21(self):
        """
        Scenario 1: Successfully building test predictions from ensemble
                And I create BigML resources from "<data>" using ensemble of <number_of_models> models to test "<test>" and log predictions in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the ensemble has been created
                And I check that the models in the ensembles have been created
                And I check that the predictions are ready
                Then the local prediction file is like "<predictions_file>"

                Examples:
                |data               | number_of_models | test                      | output                         | predictions_file                         |
        """
        headers = ["data", "number_of_models", "test", "output",
                   "predictions_file"]
        examples = [
            ['data/grades.csv', '5', 'data/test_grades.csv',
             'scenario21/predictions.csv',
             'check_files/predictions_grades_e.csv']]
        show_doc(self.test_scenario21, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_resources_in_prod_from_ensemble(
                self, data=example["data"],
                number_of_models=example["number_of_models"],
                test=example["test"], output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_ensemble(self)
            test_pred.i_check_create_models_in_ensembles(
                self, in_ensemble=True)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario22(self):
        """
        Scenario: Successfully building threshold test predictions remotely from ensemble
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML resources using ensemble of <number_of_models> models with replacement to test "<test>" and log predictions in "<output>"
            And I check that the ensemble has been created
            And I check that the predictions are ready
            And I create BigML resources using the previous ensemble with different thresholds "<threshold_class>" to remotely test "<test>" and log predictions in "<output2>" and "<output3>"
            Then local predictions for different thresholds in "<output2>" and "<output3>" are different
        """
        headers = ["scenario", "kwargs", "number_of_models", "test", "output",
                   "output2", "output3", "threshold_class"]
        examples = [
            ['scenario1', '{"data": "data/iris.csv",' +
             ' "output": "scenario1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}', '10', 'data/test_iris.csv',
             'scenario22/predictions.csv', 'scenario22/predictions2.csv',
             'scenario22/predictions3.csv', 'Iris-virginica']]
        show_doc(self.test_scenario22, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_create_resources_from_ensemble_with_replacement(
                self, number_of_models=example["number_of_models"],
                test=example["test"], output=example["output"])
            test_pred.i_check_create_ensemble(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_create_resources_from_ensemble_with_threshold_rem(
                self, test=example["test"], output2=example["output2"],
                output3=example["output3"],
                threshold_class=example["threshold_class"])
            test_pred.i_check_predictions_with_different_thresholds(
                self, example["output2"], example["output3"])

    def test_scenario23(self):
        """
        Scenario: Successfully building test predictions from boosted ensemble
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML resources using boosted ensemble in <iterations> iterations to test "<test>" and log predictions in "<output>"
            And I check that the ensemble has been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        headers = ["scenario", "kwargs", "iterations", "test", "output",
                   "predictions_file"]
        examples = [
            ['scenario1', '{"data": "data/iris.csv", "output": "scenario1/predictions.csv", "test": "data/test_iris.csv"}', '10', 'data/test_iris.csv', 'scenario23/predictions.csv', 'check_files/predictions_iris_boost.csv']]
        show_doc(self.test_scenario23, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_create_resources_from_boosted_ensemble(
                self, iterations=example["iterations"], test=example["test"],
                output=example["output"])
            test_pred.i_check_create_ensemble(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])


    def test_scenario24(self):
        """
        Scenario: Successfully  test predictions remotely from boosted ensemble
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML resources using boosted ensemble in <iterations> iterations to remotely test "<test>" and log predictions in "<output>"
            And I check that the ensemble has been created
            And I check that the predictions are ready
            And I check that the batch prediction is ready
            And I check that the bath predictions datset is ready
            Then the local prediction file is like "<predictions_file>"
        """
        headers = ["scenario", "kwargs", "iterations", "test", "output",
                   "predictions_file"]
        examples = [
            ['scenario1', '{"data": "data/iris.csv", "output": "scenario1/predictions.csv", "test": "data/test_iris.csv"}', '10', 'data/test_iris.csv', 'scenario24/predictions.csv', 'check_files/predictions_iris_boost.csv']]
        show_doc(self.test_scenario24, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_create_resources_remotely_from_boosted_ensemble(
                self, iterations=example["iterations"], test=example["test"],
                output=example["output"])
            test_pred.i_check_create_ensemble(self)
            test_pred.i_check_create_batch_prediction(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"],
                headers=True)

    def test_scenario25(self):
        """
        Scenario: Successfully building test predictions from model with operating point
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML resources using model with operating point "<operating_point>" to test "<test>" and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        headers = ["scenario", "kwargs", "test", "output",
                   "predictions_file", "operating_point"]
        examples = [
            ['scenario1', '{"data": "data/iris.csv",' +
             ' "output": "scenario1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}', 'data/test_iris.csv',
             'scenario25/predictions_p.csv',
             'check_files/predictions_iris_op_prob.csv',
             "data/operating_point_prob.json"],
            ['scenario1', '{"data": "data/iris.csv",' +
             ' "output": "scenario1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}', 'data/test_iris.csv',
             'scenario25/predictions_c.csv',
             'check_files/predictions_iris_op_conf.csv',
             "data/operating_point_conf.json"]]

        show_doc(self.test_scenario25, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_create_resources_from_model_with_op(
                self, operating_point=example["operating_point"],
                test=example["test"], output=example["output"])
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario26(self):
        """
        Scenario: Successfully building test predictions from ensemble
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            Given I have previously executed "<scenario2>" or reproduce it with arguments <kwargs2>
            And I create BigML resources using local ensemble of <number_of_models> models in "<scenario2>" to test "<test>" and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        headers = ["scenario", "kwargs", "scenario2", "kwargs2",
                   "number_of_models", "directory", "test", "output",
                   "predictions_file", "operating_point"]
        examples = [
            ['scenario1', '{"data": "data/iris.csv",' +
             ' "output": "scenario1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}',
             'scenario5', '{"number_of_models": 10,' +
             ' "output": "scenario5/predictions.csv",' +
             ' "test": "data/test_iris.csv"}',
             '10', 'scenario5', 'data/test_iris.csv',
             'scenario26/predictions_p.csv',
             'check_files/predictions_iris_e_op_prob.csv',
             'data/operating_point_prob.json'],
            ['scenario1', '{"data": "data/iris.csv",' +
             ' "output": "scenario1/predictions.csv",' +
             ' "test": "data/test_iris.csv"}',
             'scenario5', '{"number_of_models": 10,' +
             '"output": "scenario5/predictions.csv",' +
             '"test": "data/test_iris.csv"}',
             '10', 'scenario5', 'data/test_iris.csv',
             'scenario26/predictions_c.csv',
             'check_files/predictions_iris_e_op_conf.csv',
             'data/operating_point_conf.json']]
        show_doc(self.test_scenario26, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario2"], example["kwargs2"])
            test_pred.i_create_resources_from_local_ensemble_with_op(
                self, number_of_models=example["number_of_models"],
                directory=example["directory"],
                test=example["test"], output=example["output"],
                operating_point=example["operating_point"])
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario27(self):
        """
        Scenario: Successfully building test predictions from start with split field:
            Given I create BigML resources uploading train "<data>" file with split field "<split_field>" and objective "<objeciive>" and log in "<output-dir>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the model has been created
            And I check that the first node has <children> branches
        """
        headers = ["data", "split_field", "objective", "output_dir",
                   "children"]
        examples = [
            ['data/iris.csv', 'sepal length', '000004', 'scenario27', 3]]
        show_doc(self.test_scenario27, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_all_resources_with_split_field(
                self, example["data"], example["objective"],
                example["split_field"], example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_pred.i_check_first_node_children(
                self, example["children"], example["objective"])

    def test_scenario28(self):
        """
        Scenario: Successfully building test predictions from start with focus field:
            Given I create BigML resources uploading train "<data>" file with focus field "<focus_field>" and objective "<objeciive>" and log in "<output-dir>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the model has been created
            And I check that the first node has <children> branches
        """
        headers = ["data", "focus_field", "objective", "output_dir",
                   "children"]
        examples = [
            ['data/iris.csv', 'sepal length', '000004', 'scenario28', 2]]
        show_doc(self.test_scenario28, examples)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_create_all_resources_with_focus_field(
                self, example["data"], example["objective"],
                example["focus_field"], example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_pred.i_check_first_node_children(
                self, example["children"], example["objective"])
