# -*- coding: utf-8 -*-
#!/usr/bin/env python
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#
# Copyright 2019-2024 BigML
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


""" Testing PCA projections creation

"""

from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)


import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.basic_batch_tst_prediction_steps as batch_pred
import bigmler.tests.basic_pca_steps as pca_proj

def setup_module():
    """Setup for the module

    """
    common_setup_module()
    test = TestProjection()
    test.bigml = {"method": "setup_scenario02"}
    test.setup_scenario02()


def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()


class TestProjection:
    """Testing Projections"""

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
        Scenario: Successfully building PCA test projections from start with no headers:
            Given I create BigML PCA resources uploading train "<data>" file with no headers to test "<test>" with no headers and log projections in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the PCA model has been created
            And I check that the projections are ready
            Then the local projections file is like "<projections_file>"
        """
        print(self.test_scenario01.__doc__)
        headers = ["data", "test", "output", "projections_file"]
        examples = [
            ['data/grades_nh.csv', 'data/test_grades_nh.csv',
             'scenario1_pca_nh/projections.csv',
             'check_files/projections_grades_pca.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            pca_proj.i_create_all_pca_resources_with_no_headers(
                self, example["data"], example["test"], example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            pca_proj.i_check_create_pca_model(self)
            test_pred.i_check_create_projections(self)
            test_pred.i_check_projections(self, example["projections_file"])

    def setup_scenario02(self):
        """
        Scenario: Successfully building test projections from start:
            Given I create BigML PCA resources uploading train "<data>" file to test "<test>" and log projections in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the model has been created
            And I check that the projections are ready
            Then the local projection file is like "<projections_file>"
        """
        print(self.setup_scenario02.__doc__)
        headers = ["data", "test", "output", "projections_file"]
        examples = [
            ['data/grades.csv', 'data/test_grades_no_missings.csv',
             'scenario1_pca/projections.csv',
             'check_files/projections_grades_pca.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            pca_proj.i_create_all_pca_resources(
                self, example["data"], example["test"], example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            pca_proj.i_check_create_pca_model(self)
            test_pred.i_check_create_projections(self)
            test_pred.i_check_projections(self, example["projections_file"])

    def test_scenario03(self):
        """
        Scenario: Successfully building test projections from source
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML linear regression resources using source to test "<test>" and log projections in "<output>"
            And I check that the dataset has been created
            And I check that the model has been created
            And I check that the projections are ready
            Then the local projections file is like "<projections_file>"
        """
        print(self.test_scenario03.__doc__)
        headers = ["scenario", "kwargs", "test", "output", "projections_file"]
        examples = [
            ['scenario1_pca', '{"data": "data/grades.csv",' +
             ' "output": "scenario1_pca/projections.csv",' +
             ' "test": "data/test_grades_no_missings.csv"}',
             'data/test_grades_no_missings.csv',
             'scenario2_pca/projections.csv',
             'check_files/projections_grades_pca.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            pca_proj.i_create_pca_resources_from_source(
                self, test=example["test"], output=example["output"])
            test_pred.i_check_create_dataset(self, suffix=None)
            pca_proj.i_check_create_pca_model(self)
            test_pred.i_check_create_projections(self)
            test_pred.i_check_projections(self, example["projections_file"])

    def test_scenario04(self):
        """
        Scenario: Successfully building test projections from dataset
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML linear regression resources using dataset to test "<test>" and log projections in "<output>"
            And I check that the model has been created
            And I check that the projections are ready
            Then the local projection file is like "<projections_file>"
        """
        print(self.test_scenario04.__doc__)
        headers = ["scenario", "kwargs", "test", "output", "projections_file"]
        examples = [
            ['scenario1_pca', '{"data": "data/grades.csv",' +
             ' "output": "scenario1_pca/projections.csv",' +
             ' "test": "data/test_grades_no_missings.csv"}',
             'data/test_grades_no_missings.csv',
             'scenario3_pca/projections.csv',
             'check_files/projections_grades_pca.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            pca_proj.i_create_pca_resources_from_dataset(
                self, test=example["test"], output=example["output"])
            pca_proj.i_check_create_pca_model(self)
            test_pred.i_check_create_projections(self)
            test_pred.i_check_projections(self, example["projections_file"])

    def test_scenario05(self):
        """
        Scenario: Successfully building test projections from model
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML linear regression resources using model to test "<test>" and log projections in "<output>"
            And I check that the projections are ready
            Then the local projection file is like "<projections_file>"
        """
        print(self.test_scenario05.__doc__)
        headers = ["scenario", "kwargs", "test", "output", "projections_file"]
        examples = [
            ['scenario1_pca', '{"data": "data/grades.csv",' +
             ' "output": "scenario1_pca/projections.csv",' +
             ' "test": "data/test_grades_no_missings.csv"}',
             'data/test_grades_no_missings.csv',
             'scenario4_pca/projections.csv',
             'check_files/projections_grades_pca.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            pca_proj.i_create_pca_resources_from_model(
                self, test=example["test"], output=example["output"])
            test_pred.i_check_create_projections(self)
            test_pred.i_check_projections(self, example["projections_file"])

    def test_scenario06(self):
        """
        Scenario: Successfully building batch test projections from model
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML linear regression resources using model to test "<test>" as a batch projection and log projections in "<output>"
            And I check that the projections are ready
            Then the local projection file is like "<projections_file>"
        """
        print(self.test_scenario06.__doc__)
        headers = ["scenario", "kwargs", "test", "output", "projections_file"]
        examples = [
            ['scenario1_pca', '{"data": "data/grades.csv",' +
             ' "output": "scenario1_pca/projections.csv",' +
             ' "test": "data/test_grades_no_missings.csv"}',
             'data/test_grades_no_missings.csv',
             'scenario5_pca/projections.csv',
             'check_files/projections_grades_pca.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            pca_proj.i_create_pca_resources_from_model_remote(
                self, test=example["test"], output=example["output"])
            batch_pred.i_check_create_batch_projection(self)
            test_pred.i_check_create_projections(self)
            test_pred.i_check_projections(self, example["projections_file"])
