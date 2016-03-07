# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2016 BigML
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


""" Testing associations

"""
from __future__ import absolute_import


from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, teardown_class)


import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.basic_association_steps as test_association


def setup_module():
    """Setup for the module

    """
    common_setup_module()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestAssociation(object):

    def teardown(self):
        """Calling generic teardown for every method

        """
        print "\nEnd of tests in: %s\n-------------------\n" % __name__
        teardown_class()

    def setup(self):
        """
            Debug information
        """
        print "\n-------------------\nTests in: %s\n" % __name__

    def test_scenario1(self):
        """
            Scenario: Successfully building association from scratch:
                Given I create BigML association uploading train "<data>" file and log resources in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the association has been created

                Examples:
                | data               | output_dir
                | ../data/grades.csv |  ./scenario_ass_1_r
                | ../data/diabetes.csv   | ./scenario_ass_1
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/spam.csv', 'scenario_ass_1_r'],
            ['data/movies.csv', 'scenario_ass_1_i'],
            ['data/iris.csv', 'scenario_ass_1']]
        for example in examples:
            print "\nTesting with:\n", example
            test_association.i_create_association(self, data=example[0], output_dir=example[1])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_association(self)

    def test_scenario2(self):
        """
            Scenario: Successfully building association from source
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML association using source and log resources in "<output_dir>"
                And I check that the dataset has been created
                And I check that the association has been created

                Examples:
                |scenario    | kwargs                                                  | output_dir
                | scenario_ass_1| {"data": "../data/iris.csv", "output_dir": "./scenario_ass_1/}   | ./scenario_ass_2   |
        """
        print self.test_scenario2.__doc__
        examples = [
            ['scenario_ass_1', '{"data": "data/iris.csv", "output_dir": "scenario_ass_1"}', 'scenario_ass_2']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            test_association.i_create_association_from_source(self, output_dir=example[2])
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_association(self)

    def test_scenario3(self):
        """
            Scenario: Successfully building test predictions from dataset
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML association using dataset and log predictions in "<output_dir>"
                And I check that the association has been created

                Examples:
                |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
                | scenario_ass_1| {"data": "../data/iris.csv", "output_dir": "./scenario_c_1"}   | ../data/diabetes.csv   | ./scenario_c_3/centroids.csv   | ./check_files/centroids_diabetes.csv   |

        """
        print self.test_scenario3.__doc__
        examples = [
            ['scenario_ass_1', '{"data": "data/iris.csv", "output_dir": "scenario_ass_1"}', 'scenario_ass_3']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            test_association.i_create_association_from_dataset(self, output_dir=example[2])
            test_pred.i_check_create_association(self)
