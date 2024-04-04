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


""" Testing associations

"""

from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)


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

class TestAssociation:
    """Testing associaton commands"""

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
        Scenario: Successfully building association from scratch:
            Given I create BigML association uploading train "<data>" file and log resources in "<output_dir>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the association has been created
        """
        print(self.test_scenario1.__doc__)
        headers = ["data", "output_dir"]
        examples = [
            ['data/spam.csv', 'scenario_ass_1_r'],
            ['data/movies.csv', 'scenario_ass_1_i'],
            ['data/iris.csv', 'scenario_ass_1']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_association.i_create_association(
                self, data=example["data"], output_dir=example["output_dir"])
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
        """
        print(self.test_scenario2.__doc__)
        headers = ["scenario", "kwargs", "output_dir"]
        examples = [
            ['scenario_ass_1',
             '{"data": "data/iris.csv", "output_dir": "scenario_ass_1"}',
             'scenario_ass_2']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_association.i_create_association_from_source(
                self, output_dir=example["output_dir"])
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_association(self)

    def test_scenario3(self):
        """
        Scenario: Successfully building test predictions from dataset
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML association using dataset and log predictions in "<output_dir>"
            And I check that the association has been created
        """
        print(self.test_scenario3.__doc__)
        headers = ["scenario", "kwargs", "output_dir"]
        examples = [
            ['scenario_ass_1',
             '{"data": "data/iris.csv", "output_dir": "scenario_ass_1"}',
             'scenario_ass_3']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_pred.i_have_previous_scenario_or_reproduce_it(
                self, example["scenario"], example["kwargs"])
            test_association.i_create_association_from_dataset(
                self, output_dir=example["output_dir"])
            test_pred.i_check_create_association(self)
