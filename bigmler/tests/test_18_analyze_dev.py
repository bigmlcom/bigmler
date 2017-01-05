# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2017 BigML
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


""" Testing analyze subcommand in development mode

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

class TestAnalyzeDev(object):

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
            Scenario: Successfully building feature selection from dataset in dev mode:
                Given I want to use api in DEV mode
                And I create BigML dataset in dev mode uploading train "<data>" file in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I create BigML feature selection <kfold>-fold cross-validations improving "<metric>" in dev mode
                And I check that the <kfold>-datasets have been created
                And I check that the <kfold>-models have been created
                And I check that all the <kfold>-fold cross-validations have been created
                Then the best feature selection is "<selection>", with "<metric>" of <metric_value>

                Examples:
                | data                | output                    | kfold | metric   | selection   | metric_value |
                | ../data/iris_2f.csv | ./scenario_a_2/evaluation | 2     | accuracy | petal width | 100.00%       |
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris_2f.csv', 'scenario_a_2/evaluation', '2', 'accuracy', 'petal width', '100.00%']]
        for example in examples:
            print "\nTesting with:\n", example
            common.i_want_api_dev_mode(self)
            test_pred.i_create_dev_dataset(self, data=example[0], output=example[1])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_pred.i_create_kfold_cross_validation_in_dev(self, k_folds=example[2], metric=example[3])
            test_pred.i_check_create_kfold_datasets(self, example[2])
            test_pred.i_check_create_kfold_models(self, example[2])
            test_pred.i_check_create_all_kfold_cross_validations(self, example[2])
            test_pred.i_check_feature_selection(self, example[4], example[3], example[5])
