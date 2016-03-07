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


""" Testing dataset creation with unicode characters

"""
from __future__ import absolute_import


from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, teardown_class)


import bigmler.tests.dataset_advanced_steps as dataset_adv
import bigmler.tests.basic_tst_prediction_steps as test_pred


def setup_module():
    """Setup for the module

    """
    common_setup_module()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestUnicode(object):

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
            Scenario: Successfully building test predictions from dataset specifying objective field and model fields
                Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I create BigML resources using dataset, objective field <objective> and model fields <fields> to test "<test>" and log predictions in "<output>"
                And I check that the model has been created
                And I check that the predictions are ready
                Then the local prediction file is like "<predictions_file>"

                Examples:
                |data    | output_dir               | test                    | output                         |predictions_file                        | objective | fields   |
                | ../data/iris_2fb.csv| ./scénario1 | ../data/test_iris2fb.csv   | ./scénario1/predictions.csv   | ./check_files/predictions_iris_2fb.csv   | spécies     | "pétal width" |
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris_2fb.csv', u'scénario1', 'data/test_iris2fb.csv', u'scénario1/predictions.csv', 'check_files/predictions_iris_2fb.csv', u'spécies', u'"pétal width"']]
        for example in examples:
            print "\nTesting with:\n", example
            dataset_adv.i_create_dataset(self, data=example[0], output_dir=example[1])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)
            test_pred.i_create_resources_from_dataset_objective_model(self, objective=example[5], fields=example[6], test=example[2], output=example[3])
            test_pred.i_check_create_model(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[4])
