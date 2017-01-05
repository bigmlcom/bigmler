# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2016-2017 BigML
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


""" Testing predictions in development mode

"""
from __future__ import absolute_import


from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, teardown_class)

import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.dataset_advanced_steps as dataset
import bigmler.tests.common_steps as common


def setup_module():
    """Setup for the module

    """
    common_setup_module()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestPredictionDev(object):

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
            Scenario 1: Successfully building test predictions from ensemble
                    Given I want to use api in DEV mode
                    And I create BigML resources in DEV from "<data>" using ensemble of <number_of_models> models to test "<test>" and log predictions in "<output>"
                    And I check that the source has been created
                    And I check that the dataset has been created
                    And I check that the ensemble has been created
                    And I check that the models in the ensembles have been created
                    And I check that the predictions are ready
                    Then the local prediction file is like "<predictions_file>"

                    Examples:
                    |data               | number_of_models | test                      | output                         | predictions_file                         |
                    | ../data/grades.csv| 5                | ../data/test_grades.csv   | ./scenario1_dev/predictions.csv   | ./check_files/predictions_grades_e.csv   |
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/grades.csv', '5', 'data/test_grades.csv', 'scenario1_dev/predictions.csv', 'check_files/predictions_grades_e.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            common.i_want_api_dev_mode(self)
            test_pred.i_create_resources_in_dev_from_ensemble( \
                self, data=example[0], number_of_models=example[1],
                test=example[2], output=example[3])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_check_create_ensemble(self)
            test_pred.i_check_create_models_in_ensembles(self,
                                                         in_ensemble=True)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[4])
