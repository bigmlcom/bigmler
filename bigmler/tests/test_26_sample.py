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


""" Testing samples

"""

from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)

import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.sample_steps as test_sample
import bigmler.tests.dataset_advanced_steps as dataset


def setup_module():
    """Setup for the module

    """
    common_setup_module()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestSamples:
    """Testing sample commands"""

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
        Scenario: Successfully building a new sample from a dataset
            Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
            And I check that the source has been created
            And I check that the dataset has been created
            Then I create a new sample from the dataset and get the sample using options "<options>" storing logs in "<output_dir>"
            And I check that the sample has been created
            And the sample file is like "<sample_CSV>"
        """
        print(self.test_scenario1.__doc__)
        headers = ["data", "output_dir", "options", "sample_CSV"]
        examples = [
            ['data/iris.csv', 'scenario_smp_1',
             '--occurrence --sample-header --row-index',
             'check_files/sample_iris.csv'],
            ['data/iris.csv', 'scenario_smp_2',
             '--precision 0 --rows 10 --row-offset 10 --unique',
             'check_files/sample_iris2.csv'],
            ['data/iris.csv', 'scenario_smp_3',
             '--row-order-by="-petal length" --row-fields ' +
             '"petal length,petal width" --mode linear',
             'check_files/sample_iris3.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            dataset.i_create_dataset(self, data=example["data"],
                                     output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_sample.i_create_sample(
                self, options=example["options"],
                output_dir=example["output_dir"])
            test_sample.i_check_create_sample(self)
            test_sample.i_check_sample_file(
                self, check_sample_file=example["sample_CSV"])

    def test_scenario2(self):
        """
        Scenario: Successfully building a new sample from a dataset
            Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
            And I check that the source has been created
            And I check that the dataset has been created
            Then I create a new sample from the dataset and get the sample using options "<options>" storing logs in "<output_dir>"
            And I check that the sample has been created
            And the sample JSON is like the one in "<sample_JSON_file>"
        """
        print(self.test_scenario2.__doc__)
        headers = ["data", "output_dir", "options", "sample_JSON"]
        examples = [
            ['data/iris.csv', 'scenario_smp_4',
             '--stat-field "petal length"',
             'check_files/stat_info.json']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            dataset.i_create_dataset(
                self, data=example["data"], output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_sample.i_create_sample(
                self, options=example["options"],
                output_dir=example["output_dir"])
            test_sample.i_check_create_sample(self)
            test_sample.i_check_sample_json(
                self, check_sample_file=example["sample_JSON"])
