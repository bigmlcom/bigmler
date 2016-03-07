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


""" Testing report generation

"""
from __future__ import absolute_import


from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, teardown_class)

import bigmler.tests.basic_tst_prediction_steps as test_pred


def setup_module():
    """Setup for the module

    """
    common_setup_module()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestReport(object):

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
            Scenario: Successfully generating reports in Gazibit:
                Given I create BigML resources and share them uploading train "<data>" file to evaluate and log evaluation and reports in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created and shared
                And I check that the model has been created and shared
                Then I check that the evaluation has been created and shared
                And I check that the Gazibit report has been created
                And I check that the Gazibit shared report has been created

                Examples:
                | data               | output                      |
                | ../data/iris.csv   | ./scenario_rpt_1/evaluation |
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', 'scenario_rpt_1/evaluation']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_create_all_resources_to_evaluate_and_report(self, data=example[0], output=example[1])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset_shared(self)
            test_pred.i_check_create_model_shared(self)
            test_pred.i_check_create_evaluation_shared(self)
            test_pred.i_check_gazibit_reports(self, shared=None)
            test_pred.i_check_gazibit_reports(self, shared='shared ')
