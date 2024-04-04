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


""" Testing predictions uploading from stdin

"""
from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)


import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.stdin_input_steps as stdin


def setup_module():
    """Setup for the module

    """
    common_setup_module()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestStdin:
    """Testing reading from stdin """

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
            Scenario: Successfully building a model from data streamed to stdin:
                Given I create a BigML source from stdin using train "<data>" file and logging in "<output_dir>"
                Then I check that the source has been created
        """
        print(self.test_scenario1.__doc__)
        headers = ["data", "output_dir"]
        examples = [
            ['data/iris.csv', 'scenario_st_1']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            stdin.i_create_source_from_stdin(
                self, data=example["data"], output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)

    def test_scenario2(self):
        """
            Scenario: Successfully building predictions for data streamed to stdin:
                Given I create BigML resources uploading train "<data>" file to test "<test>" read from stdin with name "<name>" and log predictions in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the model has been created
                And I check that the predictions are ready
                Then the local prediction file is like "<predictions_file>"

                Examples:
                | data               | test                    | output                            |predictions_file           | name |
                | ../data/iris.csv   | ../data/test_iris.csv   | ./scenario_st_2/predictions.csv   | ./check_files/predictions_iris.csv   | Source name: áéí |
        """
        print(self.test_scenario2.__doc__)
        headers = ["data", "test", "output", "predictions_file", "name"]
        examples = [
            ['data/iris.csv', 'data/test_iris.csv',
             'scenario_st_2/predictions.csv',
             'check_files/predictions_iris.csv', 'Source name: áéí']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            stdin.i_create_all_resources_to_test_from_stdin(
                self, data=example["data"], test=example["test"],
                name=example["name"], output=example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_model(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example["predictions_file"])
