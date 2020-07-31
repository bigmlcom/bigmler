# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2020 BigML
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


""" Testing Multi-label ensembles

"""



from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, teardown_class)

import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.ml_tst_prediction_steps as ml_pred
import bigmler.tests.ml_tst_evaluation_steps as ml_eval
import bigmler.tests.evaluation_steps as evaluation


def setup_module():
    """Setup for the module

    """
    common_setup_module()
    test = TestMLEnsembles()
    test.setup_scenario1()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()


class TestMLEnsembles(object):

    def teardown(self):
        """Calling generic teardown for every method

        """
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)
        teardown_class()

    def setup(self):
        """
            Debug information
        """
        print("\n-------------------\nTests in: %s\n" % __name__)

    def setup_scenario1(self):
        """
            Scenario: Successfully building multi-label test predictions from start:
                Given I create BigML multi-label resources tagged as "<tag>" with "<label_separator>" label separator and <number_of_labels> labels uploading train "<data>" file with "<training_separator>" field separator and <number_of_models> models ensembles to test "<test>" and log predictions in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the models in the ensembles have been created
                Then I check that the predictions are ready

                Examples:
                |tag |label_separator |number_of_labels | data                   |training_separator |number_of_models | test                        | output                                   |
                |my_multilabel_1|:|7| ../data/multilabel.csv |,|10| ../data/test_multilabel.csv | ./scenario_mle_1/predictions.csv
        """
        print(self.setup_scenario1.__doc__)
        examples = [
            ['my_multilabel_1', ':', '7', 'data/multilabel.csv', ',', '10', 'data/test_multilabel.csv', 'scenario_mle_1/predictions.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            ml_pred.i_create_all_ml_resources_and_ensembles(self, tag=example[0], label_separator=example[1], number_of_labels=example[2], data=example[3], training_separator=example[4], number_of_models=example[5], test=example[6], output=example[7])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_pred.i_check_create_models_in_ensembles(self, in_ensemble=True)
            test_pred.i_check_create_predictions(self)

    def test_scenario2(self):
        """
            Scenario: Successfully building test predictions from source
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML multi-label resources using source and <number_of_models> models ensembles to test "<test>" and log predictions in "<output>"
                And I check that the dataset has been created
                And I check that the models in the ensembles have been created
                Then I check that the predictions are ready

                Examples:
                |scenario    | kwargs                                                  |number_of_models |test                    | output                               |
                | scenario_mle_1| {"tag": "my_multilabel_1", "data": "../data/multilabel.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "./scenario_mle_1/predictions.csv", "test": "../data/test_multilabel.csv", "number_of_models": 10}   |10| ../data/test_multilabel.csv   | ./scenario_mle_2/predictions.csv
        """
        print(self.test_scenario2.__doc__)
        examples = [
            ['scenario_mle_1', '{"tag": "my_multilabel_1", "data": "data/multilabel.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "scenario_mle_1/predictions.csv", "test": "data/test_multilabel.csv", "number_of_models": 10}', '10', 'data/test_multilabel.csv', 'scenario_mle_2/predictions.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            ml_pred.i_create_resources_and_ensembles_from_source(self, multi_label='multi-label ', number_of_models=example[2], test=example[3], output=example[4])
            test_pred.i_check_create_dataset(self)
            test_pred.i_check_create_models_in_ensembles(self, in_ensemble=True)
            test_pred.i_check_create_predictions(self)

    def test_scenario3(self):
        """
            Scenario: Successfully building test predictions from dataset
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML multi-label resources using dataset and <number_of_models> models ensembles to test "<test>" and log predictions in "<output>"
                And I check that the models in the ensembles have been created
                Then I check that the predictions are ready

                Examples:
                |scenario    | kwargs                                                  | number_of_models |test                    | output                                   |
                | scenario_mle_1| {"tag": "my_multilabel_1", "data": "../data/multilabel.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "./scenario_mle_1/predictions.csv", "test": "../data/test_multilabel.csv", "number_of_models": 10}    |10| ../data/test_multilabel.csv   | ./scenario_mle_3/predictions.csv
        """
        print(self.test_scenario3.__doc__)
        examples = [
            ['scenario_mle_1', '{"tag": "my_multilabel_1", "data": "data/multilabel.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "scenario_mle_1/predictions.csv", "test": "data/test_multilabel.csv", "number_of_models": 10}', '10', 'data/test_multilabel.csv', 'scenario_mle_3/predictions.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            ml_pred.i_create_resources_and_ensembles_from_source(self, multi_label='multi-label', number_of_models=example[2], test=example[3], output=example[4])
            test_pred.i_check_create_dataset(self)
            test_pred.i_check_create_models_in_ensembles(self, in_ensemble=True)
            test_pred.i_check_create_predictions(self)
