# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2019-2020 BigML
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
                                 common_teardown_module,
                                 teardown_class)


import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.basic_batch_tst_prediction_steps as batch_pred
import bigmler.tests.basic_pca_steps as pca_proj

def setup_module():
    """Setup for the module

    """
    common_setup_module()
    test = TestProjection()
    test.setup_scenario02()


def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()


class TestProjection(object):

    def setup(self):
        """
            Debug information
        """
        print("\n-------------------\nTests in: %s\n" % __name__)

    def teardown(self):
        """Calling generic teardown for every method

        """
        self.world = teardown_class()
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)

    def test_scenario01(self):
        """
        Scenario: Successfully building PCA test projections from start with no headers:
            Given I create BigML PCA resources uploading train "<data>" file with no headers to test "<test>" with no headers and log projections in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the PCA model has been created
            And I check that the projections are ready
            Then the local projections file is like "<projections_file>"

            Examples:
            | data               | test                    | output                        |projections_file           |



        """
        print(self.test_scenario01.__doc__)
        examples = [
            ['data/grades_nh.csv', 'data/test_grades_nh.csv', 'scenario1_pca_nh/projections.csv', 'check_files/projections_grades_pca.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            pca_proj.i_create_all_pca_resources_with_no_headers(self, example[0], example[1], example[2])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            pca_proj.i_check_create_pca_model(self)
            test_pred.i_check_create_projections(self)
            test_pred.i_check_projections(self, example[3])


    def setup_scenario02(self):
        """
        Scenario: Successfully building test projections from start:
            Given I create BigML PCA resources uploading train "<data>" file to test "<test>" and log projections in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the model has been created
            And I check that the projections are ready
            Then the local projection file is like "<projections_file>"

            Examples:
            | data               | test                    | output                        |projections_file           |
            | ../data/grades.csv   | ../data/test_grades.csv   | ./scenario1_pca/projections.csv   | ./check_files/projections_grades_pca.csv   |
        """
        print(self.setup_scenario02.__doc__)
        examples = [
            ['data/grades.csv', 'data/test_grades_no_missings.csv', 'scenario1_pca/projections.csv', 'check_files/projections_grades_pca.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            pca_proj.i_create_all_pca_resources(self, example[0], example[1], example[2])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            pca_proj.i_check_create_pca_model(self)
            test_pred.i_check_create_projections(self)
            test_pred.i_check_projections(self, example[3])

    def test_scenario03(self):
        """
        Scenario: Successfully building test projections from source
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML linear regression resources using source to test "<test>" and log projections in "<output>"
            And I check that the dataset has been created
            And I check that the model has been created
            And I check that the projections are ready
            Then the local projections file is like "<projections_file>"

            Examples:
            |scenario    | kwargs                                                  | test                    | output                        |projections_file           |
            | scenario1| {"data": "../data/grades.csv", "output": "./scenario1_lrr/projections.csv", "test": "../data/test_grades.csv"}   | ../data/test_grades.csv   | ./scenario2/projections.csv   | ./check_files/projections_grades.csv   |
        """
        print(self.test_scenario03.__doc__)
        examples = [
            ['scenario1_pca', '{"data": "data/grades.csv", "output": "scenario1_pca/projections.csv", "test": "data/test_grades_no_missings.csv"}', 'data/test_grades_no_missings.csv', 'scenario2_pca/projections.csv', 'check_files/projections_grades_pca.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            pca_proj.i_create_pca_resources_from_source(self, test=example[2], output=example[3])
            test_pred.i_check_create_dataset(self, suffix=None)
            pca_proj.i_check_create_pca_model(self)
            test_pred.i_check_create_projections(self)
            test_pred.i_check_projections(self, example[4])


    def test_scenario04(self):
        """
        Scenario: Successfully building test projections from dataset
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML linear regression resources using dataset to test "<test>" and log projections in "<output>"
            And I check that the model has been created
            And I check that the projections are ready
            Then the local projection file is like "<projections_file>"

            Examples:
            |scenario    | kwargs                                                  | test                    | output                        |projections_file           |


        """
        print(self.test_scenario04.__doc__)
        examples = [
            ['scenario1_pca', '{"data": "data/grades.csv", "output": "scenario1_pca/projections.csv", "test": "data/test_grades_no_missings.csv"}', 'data/test_grades_no_missings.csv', 'scenario3_pca/projections.csv', 'check_files/projections_grades_pca.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            pca_proj.i_create_pca_resources_from_dataset(self, test=example[2], output=example[3])
            pca_proj.i_check_create_pca_model(self)
            test_pred.i_check_create_projections(self)
            test_pred.i_check_projections(self, example[4])



    def test_scenario05(self):
        """
        Scenario: Successfully building test projections from model
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML linear regression resources using model to test "<test>" and log projections in "<output>"
            And I check that the projections are ready
            Then the local projection file is like "<projections_file>"

            Examples:
            |scenario    | kwargs                                                  | test                    | output                        |projections_file           |

        """
        print(self.test_scenario05.__doc__)
        examples = [
            ['scenario1_pca', '{"data": "data/grades.csv", "output": "scenario1_pca/projections.csv", "test": "data/test_grades_no_missings.csv"}', 'data/test_grades_no_missings.csv', 'scenario4_pca/projections.csv', 'check_files/projections_grades_pca.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            pca_proj.i_create_pca_resources_from_model(self, test=example[2], output=example[3])
            test_pred.i_check_create_projections(self)
            test_pred.i_check_projections(self, example[4])

    def test_scenario06(self):
        """
        Scenario: Successfully building batch test projections from model
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML linear regression resources using model to test "<test>" as a batch projection and log projections in "<output>"
            And I check that the projections are ready
            Then the local projection file is like "<projections_file>"

            Examples:
            |scenario    | kwargs                                                  | test                    | output                        |projections_file           |


        """
        print(self.test_scenario06.__doc__)
        examples = [
            ['scenario1_pca', '{"data": "data/grades.csv", "output": "scenario1_pca/projections.csv", "test": "data/test_grades_no_missings.csv"}', 'data/test_grades_no_missings.csv', 'scenario5_pca/projections.csv', 'check_files/projections_grades_pca.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            pca_proj.i_create_pca_resources_from_model_remote(self, test=example[2], output=example[3])
            batch_pred.i_check_create_batch_projection(self)
            test_pred.i_check_create_projections(self)
            test_pred.i_check_projections(self, example[4])
