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


""" Testing fusion predictions creation

"""


from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module,
                                 teardown_class)


import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.basic_batch_tst_prediction_steps as batch_pred
import bigmler.tests.basic_fusion_steps as fs_pred
import bigmler.tests.basic_deepnet_steps as dn_pred
import bigmler.tests.evaluation_steps as evaluation


def setup_module():
    """Setup for the module

    """
    common_setup_module()
    test = TestPrediction()


def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()


class TestPrediction(object):

    def setup(self):
        """
            Debug information
        """
        print("\n-------------------\nTests in: %s\n" % __name__)
        self.setup_scenario01()

    def teardown(self):
        """Calling generic teardown for every method

        """
        self.world = teardown_class()
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)


    def setup_scenario01(self):
        """
        Scenario: Successfully building a model and deepnet

        """
        print(self.setup_scenario01.__doc__)
        examples = [
            ['data/iris.csv', 'scenario1_fs']]
        for example in examples:
            print("\nTesting with:\n", example)
            fs_pred.setup_for_fusion(self, train=example[0],
                                     output_dir=example[1])

    def test_scenario01(self):
        """
        Scenario: Successfully building test predictions from model
            And I create BigML fusion resources using models built on "<train>" to test "<test>" and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"

        """
        print(self.test_scenario01.__doc__)
        examples = [
            ['data/test_iris.csv', 'scenario1_fs/predictions.csv', 'check_files/predictions_iris_fs.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            fs_pred.i_create_fs_resources_from_model(self, test=example[0], output=example[1])
            fs_pred.i_check_create_fusion(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[2])

    def test_scenario02(self):
        """
        Scenario: Successfully building batch test predictions from model
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML fusion resources using model built from "<train>" to test "<test>" as a batch prediction and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"

        """
        print(self.test_scenario02.__doc__)
        examples = [
            ['data/test_iris.csv', 'scenario2_fs/predictions.csv', 'check_files/predictions_iris_fs.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            fs_pred.i_create_fs_resources_from_model_remote(self, test=example[0], output=example[1])
            fs_pred.i_check_create_fusion(self)
            batch_pred.i_check_create_batch_prediction(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[2])

    def test_scenario03(self):
        """
        Scenario: Successfully building batch test predictions from model with customized output
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML fusion resources using model built on "<train>" to test "<test>" as a batch prediction with output format "<batch-output>" and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"

        """
        print(self.test_scenario03.__doc__)
        examples = [
            ['data/test_iris.csv', 'data/batch_output.json', 'scenario3_fs/predictions.csv', 'check_files/predictions_iris_fs_prob.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            fs_pred.i_create_fs_resources_from_model_remote_with_options(self, test=example[0], output=example[2], options_file=example[1])
            fs_pred.i_check_create_fusion(self)
            batch_pred.i_check_create_batch_prediction(self)
            test_pred.i_check_create_predictions(self)
            test_pred.i_check_predictions(self, example[3])


    def test_scenario04(self):
        """
        Scenario: Successfully building evaluation from fusion
            Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
            And I create BigML fusion resources using model built from "<train>" to test "<test>" as an evaluation and log predictions in "<output>"
            And I check that the predictions are ready
            Then the local prediction file is like "<predictions_file>"
                Then the evaluation file is like "<json_evaluation_file>"

                Examples:
                | data             | output                   | json_evaluation_file    |
                | ../data/iris.csv | ./scenario_fs_e1/evaluation | ./check_files/evaluation_iris_dn.json |
        """
        print(self.test_scenario04.__doc__)
        examples = [
            ['scenario_fs_e1/evaluation', 'check_files/evaluation_iris_fs.json']]
        for example in examples:
            print("\nTesting with:\n", example)
            fs_pred.i_create_fs_resources_from_mode_and_evaluate(self, output=example[0])
            fs_pred.i_check_create_fusion(self)
            test_pred.i_check_create_evaluation(self)
            evaluation.then_the_evaluation_file_is_like(self, example[1])
