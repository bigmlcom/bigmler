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


""" Testing Anomaly Detector scores

"""

from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)

import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.basic_anomaly_prediction_steps as test_anomaly



def setup_module():
    """Setup for the module

    """
    common_setup_module()
    test = TestAnomaly()
    test.bigml = {"method": "setup_scenario1"}
    test.setup_scenario1()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()


class TestAnomaly:
    """Testing anomaly scores"""

    def setup_method(self, method):
        """Debug information """
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
        Scenario: Successfully building test anomaly scores from scratch:
            Given I create BigML resources uploading train "<data>" file to create anomaly scores for "<test>" and log predictions in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the anomaly detector has been created
            And I check that the anomaly scores are ready
            Then the local anomaly scores file is like "<predictions_file>"
        """
        print(self.setup_scenario1.__doc__)
        headers = ["data", "test", "output", "predictions_file"]
        examples = [
            ['data/tiny_kdd.csv', 'data/test_kdd.csv', 'scenario_an_1/anomaly_scores.csv', 'check_files/anomaly_scores_kdd.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_anomaly.i_create_all_anomaly_resources(
                self, data=example["data"], test=example["test"],
                output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_anomaly.i_check_create_anomaly(self)
            test_anomaly.i_check_create_anomaly_scores(self)
            test_anomaly.i_check_anomaly_scores(
                self, example["predictions_file"])

    def test_scenario2(self):
        """
        Scenario: Successfully building test predictions from source
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML resources using source to find anomaly scores for "<test>" and log predictions in "<output>"
            And I check that the dataset has been created
            And I check that the anomaly detector has been created
            And I check that the anomaly scores are ready
            Then the local anomaly scores file is like "<predictions_file>"
        """
        print(self.test_scenario2.__doc__)
        headers = ["scenario", "kwargs", "test", "output", "predictions_file"]
        examples = [
            ['scenario_an_1', '{"data": "data/tiny_kdd.csv",' +
             ' "output": "scenario_an_1/anomaly_scores.csv",' +
             ' "test": "data/test_kdd.csv"}', 'data/test_kdd.csv',
             'scenario_an_2/anomaly_scores.csv',
             'check_files/anomaly_scores_kdd.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_anomaly.i_create_anomaly_resources_from_source(
                self, test=example["test"], output=example["output"])
            test_pred.i_check_create_dataset(self)
            test_anomaly.i_check_create_anomaly(self)
            test_anomaly.i_check_create_anomaly_scores(self)
            test_anomaly.i_check_anomaly_scores(
                self, example["predictions_file"])

    def test_scenario3(self):
        """
        Scenario: Successfully building test predictions from dataset
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML resources using dataset to find anomaly scores for "<test>" and log predictions in "<output>"
            And I check that the anomaly detector has been created
            And I check that the anomaly scores are ready
            Then the local anomaly scores file is like "<predictions_file>"
        """
        print(self.test_scenario3.__doc__)
        headers = ["scenario", "kwargs", "test", "output", "predictions_file"]
        examples = [
            ['scenario_an_1', '{"data": "data/tiny_kdd.csv",' +
             ' "output": "scenario_an_1/anomaly_scores.csv",' +
             ' "test": "data/test_kdd.csv"}', 'data/test_kdd.csv',
             'scenario_an_3/anomaly_scores.csv',
             'check_files/anomaly_scores_kdd.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_anomaly.i_create_anomaly_resources_from_dataset(
                self, test=example["test"], output=example["output"])
            test_anomaly.i_check_create_anomaly(self)
            test_anomaly.i_check_create_anomaly_scores(self)
            test_anomaly.i_check_anomaly_scores(
                self, example["predictions_file"])

    def test_scenario4(self):
        """
            Scenario: Successfully building test predictions from anomaly
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using anomaly detector to find anomaly scores for "<test>" and log predictions in "<output>"
                And I check that the anomaly scores are ready
                Then the local anomaly scores file is like "<predictions_file>"
        """
        print(self.test_scenario4.__doc__)
        headers = ["scenario", "kwargs", "test", "output", "predictions_file"]
        examples = [
            ['scenario_an_1', '{"data": "data/tiny_kdd.csv",' +
             ' "output": "scenario_an_1/anomaly_scores.csv",' +
             ' "test": "data/test_kdd.csv"}', 'data/test_kdd.csv',
             'scenario_an_4/anomaly_scores.csv',
             'check_files/anomaly_scores_kdd.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_anomaly.i_create_anomaly_resources_from_anomaly_detector(
                self, test=example["test"], output=example["output"])
            test_anomaly.i_check_create_anomaly_scores(self)
            test_anomaly.i_check_anomaly_scores(
                self, example["predictions_file"])

    def test_scenario5(self):
        """
            Scenario: Successfully building test predictions from anomaly detector file
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using anomaly detector in file "<anomaly_file>" to find anomaly scores for "<test>" and log predictions in "<output>"
                And I check that the anomaly scores are ready
                Then the local anomaly scores file is like "<predictions_file>"
        """
        print(self.test_scenario5.__doc__)
        headers = ["scenario", "kwargs", "anomaly_file", "test", "output",
                   "predictions_file"]
        examples = [
            ['scenario_an_1', '{"data": "data/tiny_kdd.csv",' +
             ' "output": "scenario_an_1/anomaly_scores.csv",' +
             ' "test": "data/test_kdd.csv"}', 'scenario_an_1/anomalies',
             'data/test_kdd.csv', 'scenario_an_5/anomaly_scores.csv',
             'check_files/anomaly_scores_kdd.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_anomaly.i_create_anomaly_resources_from_anomaly_file(
                self, anomaly_file=example["anomaly_file"],
                test=example["test"], output=example["output"])
            test_anomaly.i_check_create_anomaly_scores(self)
            test_anomaly.i_check_anomaly_scores(
                self, example["predictions_file"])

    def test_scenario6(self):
        """
        Scenario: Successfully building test predictions from anomaly
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML resources using local anomaly detector in "<scenario>" to find anomaly scores for "<test>" and log predictions in "<output>"
            And I check that the anomaly scores are ready
            Then the local anomaly scores file is like "<predictions_file>"
        """
        print(self.test_scenario6.__doc__)
        headers = ["scenario", "kwargs", "test", "output", "predictions_file"]
        examples = [
            ['scenario_an_1', '{"data": "data/tiny_kdd.csv",' +
             ' "output": "scenario_an_1/anomaly_scores.csv",' +
             ' "test": "data/test_kdd.csv"}', 'data/test_kdd.csv',
             'scenario_an_6/anomaly_scores.csv',
             'check_files/anomaly_scores_kdd.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_anomaly.i_create_anomaly_resources_from_local_anomaly_detector(
                self, example["scenario"], test=example["test"],
                output=example["output"])
            test_anomaly.i_check_create_anomaly_scores(self)
            test_anomaly.i_check_anomaly_scores(
                self, example["predictions_file"])

    def test_scenario7(self):
        """
        Scenario: Successfully building anomalous dataset test predictions from anomaly
            Given I create BigML anomaly detector from data <data> with options <options> and generate a new dataset of anomalies in "<output_dir>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the anomaly detector has been created
            Then I check that the new top anomalies dataset has been created
            And the top anomalies in the anomaly detector are <top_anomalies>
            And the forest size in the anomaly detector is <forest_size>
            And the number of records in the top anomalies dataset is <top_anomalies>
        """
        print(self.test_scenario7.__doc__)
        headers = ["data", "options", "output_dir", "top_anomalies",
                   "forest_size"]
        examples = [
            ['data/tiny_kdd.csv', '--top-n 15 --forest-size 40 ',
             'scenario_an_7', '15', '40']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_anomaly.i_create_anomaly_resources_with_options(
                self, example["data"], example["options"],
                output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_anomaly.i_check_create_anomaly(self)
            test_pred.i_check_create_dataset(self, suffix='gen ')
            test_anomaly.i_check_top_anomalies(self, example["top_anomalies"])
            test_anomaly.i_check_forest_size(self, example["forest_size"])
            test_anomaly.i_check_dataset_lines_number(
                self, example["top_anomalies"])

    def test_scenario8(self):
        """
        Scenario: Successfully building anomaly detector from dataset with id fields
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create anomaly detector with "<id_fields>" and log predictions in "<output_dir>"
            And I check that the anomaly detector is ready
            Then the anomaly detector has id fields "<id_fields>"
        """
        print(self.test_scenario8.__doc__)
        headers = ["scenario", "kwargs", "id_fields", "output_dir"]
        examples = [
            ['scenario_an_1', '{"data": "data/tiny_kdd.csv",' +
             ' "output": "scenario_an_1/anomaly_scores.csv",' +
             ' "test": "data/test_kdd.csv"}', '["000004", "000005"]',
             'scenario_an_8']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_anomaly.i_create_anomaly_with_id_fields(
                self, id_fields=example["id_fields"],
                output_dir=example["output_dir"])
            test_anomaly.i_check_create_anomaly(self)
            test_anomaly.i_check_anomaly_has_id_fields(
                self, example["id_fields"])
