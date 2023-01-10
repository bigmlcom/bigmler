# -*- coding: utf-8 -*-
#!/usr/bin/env python
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#
# Copyright 2015-2023 BigML
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


""" Testing Multi-label predictions

"""
from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)

import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.ml_tst_prediction_steps as ml_pred


def setup_module():
    """Setup for the module

    """
    common_setup_module()
    test = TestMLM()
    test.bigml = {"method": "setup_scenario1"}
    test.setup_scenario1()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestMLM:
    """Testing multilabel commands"""

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

    def setup_scenario1(self):
        """
        Scenario: Successfully building multi-label test predictions from start:
            Given I create BigML multi-label resources tagged as "<tag>" with "<label_separator>" label separator and <number_of_labels> labels uploading train "<data>" file with "<training_separator>" field separator and "<ml_fields>" as multi-label fields using model_fields "<model_fields>" and objective "<objective>" to test "<test>" and log predictions in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the models have been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        print(self.setup_scenario1.__doc__)
        headers = ["tag", "label_separator", "number_of_labels", "data",
                   "training_separator", "ml_fields", "model_fields",
                   "objective", "test", "output", "predictions_file"]
        examples = [
            ['my_multilabelm_1', ':', '7', 'data/multilabel_multi.csv', ',',
             'type,class', '-type,-type - W,-type - A,-type - C,-type - S,' +
             '-type - R,-type - T,-type - P', 'class',
             'data/test_multilabel.csv',
             'scenario_mlm_1/predictions.csv',
             'check_files/predictions_ml.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            ml_pred.i_create_all_mlm_resources(self, tag=example["tag"],
                label_separator=example["label_separator"],
                number_of_labels=example["number_of_labels"],
                data=example["data"],
                training_separator=example["training_separator"],
                ml_fields=example["ml_fields"],
                model_fields=example["model_fields"],
                objective=example["objective"],
                test=example["test"],
                output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_pred.i_check_create_models(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario2(self):
        """
        Scenario: Successfully building test predictions from source
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML multi-label resources using source with objective "<objective>" and model fields "<model_fields>" to test "<test>" and log predictions in "<output>"
            And I check that the dataset has been created
            And I check that the models have been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        print(self.test_scenario2.__doc__)
        headers = ["scenario", "kwargs", "objective", "model_fields",
                   "test", "output", "predictions_file"]
        examples = [
            ['scenario_mlm_1', '{"tag": "my_multilabelm_1",' +
             ' "data": "data/multilabel_multi.csv", "label_separator": ":",' +
             ' "number_of_labels": 7, "training_separator": ",",' +
             ' "output": "scenario_mlm_1/predictions.csv",' +
             ' "test": "data/test_multilabel.csv",' +
             ' "ml_fields": "type,class", "model_fields": "-type,' +
             '-type - W,-type - A,-type - C,-type - S,-type - R,-type - T,' +
             '-type - P", "objective": "class"}', 'class',
             '-type,-type - W,-type - A,-type - C,-type - S,-type - R,' +
             '-type - T,-type - P', 'data/test_multilabel.csv',
             'scenario_mlm_2/predictions.csv',
             'check_files/predictions_ml_comma.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_create_resources_from_source_with_objective(
                self, multi_label='multi-label ',
                objective=example["objective"],
                model_fields=example["model_fields"],
                test=example["test"],
                output=example["output"])
            test_pred.i_check_create_dataset(self)
            test_pred.i_check_create_models(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario3(self):
        """
        Scenario: Successfully building test predictions from dataset
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML multi-label resources using dataset with objective "<objective>" and model fields "<model_fields>" to test "<test>" and log predictions in "<output>"
            And I check that the models have been created
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        print(self.test_scenario3.__doc__)
        headers = ["scenario", "kwargs", "objective", "model_fields",
                   "test", "output", "predictions_file"]
        examples = [
            ['scenario_mlm_1', '{"tag": "my_multilabelm_1",' +
             ' "data": "data/multilabel_multi.csv", "label_separator": ":",' +
             ' "number_of_labels": 7, "training_separator": ",",' +
             ' "output": "scenario_mlm_1/predictions.csv",' +
             ' "test": "data/test_multilabel.csv",' +
             ' "ml_fields": "type,class", "model_fields": "-type,' +
             '-type - W,-type - A,-type - C,-type - S,-type - R,' +
             '-type - T,-type - P", "objective": "class"}',
             'class', '-type,-type - W,-type - A,-type - C,' +
             '-type - S,-type - R,-type - T,-type - P',
             'data/test_multilabel.csv', 'scenario_mlm_3/predictions.csv',
             'check_files/predictions_ml_comma.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_create_resources_from_dataset_with_objective(
                self, multi_label='multi-label ',
                objective=example["objective"],
                model_fields=example["model_fields"],
                test=example["test"],
                output=example["output"])
            test_pred.i_check_create_models(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario4(self):
        """
        Scenario: Successfully building test predictions from models file
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML multi-label resources using models in file "<models_file>" with objective "<objective>" to test "<test>" and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
        """
        print(self.test_scenario4.__doc__)
        headers = ["scenario", "kwargs", "models_file", "objective",
                   "test", "output", "predictions_file"]
        examples = [
            ['scenario_mlm_1', '{"tag": "my_multilabelm_1",' +
             ' "data": "data/multilabel_multi.csv", "label_separator": ":",' +
             ' "number_of_labels": 7, "training_separator": ",",' +
             ' "output": "scenario_mlm_1/predictions.csv",' +
             ' "test": "data/test_multilabel.csv",' +
             ' "ml_fields": "type,class", "model_fields": "-type,' +
             '-type - W,-type - A,-type - C,-type - S,-type - R,' +
             '-type - T,-type - P", "objective": "class"}',
             'scenario_mlm_1/models', 'class', 'data/test_multilabel.csv',
             'scenario_mlm_4/predictions.csv',
             'check_files/predictions_ml_comma.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_pred.i_create_resources_from_models_file_with_objective(
                self, multi_label='multi-label ',
                models_file=example["models_file"],
                objective=example["objective"],
                test=example["test"], output=example["output"])
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario5(self):
        """
            Scenario: Successfully building test predictions from models retrieved by tag
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML multi-label resources with labels "<labels>" and objective "<objective>" using models tagged as "<tag>" to test "<test>" and log predictions in "<output>"
                And I check that the predictions are ready
                Then the local prediction file is like "<predictions_file>"
        """
        print(self.test_scenario5.__doc__)
        headers = ["scenario", "kwargs", "labels", "objective", "tag",
                   "test", "output", "predictions_file"]
        examples = [
            ['scenario_mlm_1', '{"tag": "my_multilabelm_1",' +
             ' "data": "data/multilabel_multi.csv",' +
             ' "label_separator": ":", "number_of_labels": 7,' +
             ' "training_separator": ",",' +
             ' "output": "scenario_mlm_1/predictions.csv",' +
             ' "test": "data/test_multilabel.csv",' +
             ' "ml_fields": "type,class", "model_fields": "-type,' +
             '-type - W,-type - A,-type - C,-type - S,-type - R,' +
             '-type - T,-type - P", "objective": "class"}', 'Adult,Student',
             'class', 'my_multilabelm_1', 'data/test_multilabel.csv',
             'scenario_mlm_5/predictions.csv',
             'check_files/predictions_ml_labels.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            ml_pred.i_predict_ml_from_model_tag_with_labels_with_objective(
                self, labels=example["labels"], objective=example["objective"],
                tag=example["tag"], test=example["test"],
                output=example["output"])
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])

    def test_scenario6(self):
        """
        Scenario: Successfully extending the multi-label source file:
            Given I create BigML a multi-label source with "<label_separator>" label separator and <number_of_labels> labels from train "<data>" file with "<training_separator>" field separator and "<ml_fields>" as multi-label fields and objective "<objective>" and output in "<output_dir>"
            And I check that the source has been created
            Then I check the extended file "<local_file>" has been created
            And the headers of the local extended file are "<headers>"
            And the first row of the local extended file is "<first_row>"
        """
        print(self.test_scenario6.__doc__)
        headers = ["label_separator", "number_of_labels", "data",
                   "training_separator", "ml_fields", "objective",
                   "output_dir", "local_file", "headers", "first_row"]
        examples = [
            [':', '7', 'data/multilabel_multi.csv', ',', 'type,class', 'class',
             'scenario_mlm_6', 'scenario_mlm_6/extended_multilabel_multi.csv',
             'color,year,price,first_name,last_name,sex,class,type,' +
             'class - Adult,class - Child,class - Pensioner,class - Retired,' +
             'class - Student,class - Teenager,class - Worker,type - A,' +
             'type - C,type - P,type - R,type - S,type - T,type - W',
             'Blue,1992,"1208,6988040134",John,Higgins,Male,' +
             'Worker:Adult,W:A:C:S:T:R:P,1,0,0,0,0,0,1,1,1,1,1,1,1,1'],
            [':', '7', 'data/multilabel_multi2.csv', ',',
             'Colors,Movies,Hobbies', 'Hobbies', 'scenario_mlm_7',
             'scenario_mlm_7/extended_multilabel_multi2.csv',
             'Registration Date,Age Range,Gender,Height,Weight,Points,' +
             'Colors,Movies,Hobbies,Colors - Black,Colors - Blue,' +
             'Colors - Green,Colors - Grey,Colors - Orange,' +
             'Colors - Pink,Colors - Purple,Colors - Red,Colors - White,' +
             'Colors - Yellow,Movies - Action,Movies - Adventure,' +
             'Movies - Comedy,Movies - Crime,Movies - Erotica,' +
             'Movies - Fantasy,Movies - Horror,Movies - Mystery,' +
             'Movies - Philosophical,Movies - Political,Movies - Romance,' +
             'Movies - Satire,Movies - Thriller,Hobbies - Barbacue,' +
             'Hobbies - Books,Hobbies - Chat,Hobbies - Cooking,' +
             'Hobbies - Dance,Hobbies - Disco,Hobbies - Dolls,' +
             'Hobbies - Family,Hobbies - Films,Hobbies - Fishing,' +
             'Hobbies - Friends,Hobbies - Jogging,Hobbies - Music,' +
             'Hobbies - Soccer,Hobbies - Toys,Hobbies - Travel,' +
             'Hobbies - Videogames,Hobbies - Walking',
             '2011-02-06,19-30,Female,140,47,11,White:Red,Comedy:Romance,' +
             'Friends:Music,0,0,0,0,0,0,0,1,1,0,0,0,1,0,0,0,0,0,0,0,1,0,' +
             '0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0']
]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            ml_pred.i_create_ml_source(
                self, label_separator=example["label_separator"],
                number_of_labels=example["number_of_labels"],
                data=example["data"],
                training_separator=example["training_separator"],
                multi_label_fields=example["ml_fields"],
                objective=example["objective"],
                output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            ml_pred.i_check_local_file(self, path=example["local_file"])
            ml_pred.i_check_headers_file(
                self, headers=example["headers"])
            ml_pred.i_check_first_row_file(
                self, first_row=example["first_row"])
