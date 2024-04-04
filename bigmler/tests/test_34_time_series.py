# -*- coding: utf-8 -*-
#!/usr/bin/env python
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#
# Copyright 2017-2024 BigML
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


""" Testing time series forecast creation

"""


from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)


import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.basic_time_series_steps as ts_pred


def setup_module():
    """Setup for the module

    """
    common_setup_module()
    test = TestPrediction()
    test.bigml = {"method": "setup_scenario02"}
    test.setup_scenario02()


def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()


class TestPrediction:
    """Testing time series predictions"""

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
        Scenario: Successfully building time series test predictions from start with no headers:
            Given I create BigML time series resources uploading train "<data>" file with no headers and log forecasts in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the time series model has been created
            Then the local forecast file is like "<forecast_file>"
        """
        print(self.test_scenario01.__doc__)
        headers = ["data", "output", "forecasts_file"]
        examples = [
            ['data/grades_nh.csv', 'scenario1_ts_nh/forecast',
             'check_files/forecasts_grades_final.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            ts_pred.i_create_all_ts_resources_with_no_headers(
                self, example["data"], example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            ts_pred.i_check_create_time_series(self)
            ts_pred.i_check_forecasts(self, example["forecasts_file"])

    def setup_scenario02(self):
        """
        Scenario: Successfully building test forecasts from start:
            Given I create BigML time series resources uploading train "<data>" file to test "<test>" and log forecasts in "<output>"
            And I check that the source has been created
            And I check that the dataset has been created
            And I check that the time series has been created
            Then the local forecasts file is like "<forecasts_file>"
        """
        print(self.setup_scenario02.__doc__)
        headers = ["data", "test", "output", "forecasts_file"]
        examples = [
            ['data/grades.csv', 'data/test_grades.json',
             'scenario1_ts/forecasts',
             'check_files/forecasts_grades_final.csv',
             'scenario1_ts/forecasts_000005.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            ts_pred.i_create_all_ts_resources(
                self, example["data"], example["test"], example["output"])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            ts_pred.i_check_create_time_series(self)
            ts_pred.i_check_forecasts(self, example["forecasts_file"])
