# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2016-2020 BigML
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


""" Testing topic model predictions creation

"""


from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module,
                                 teardown_class)


import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.basic_batch_tst_prediction_steps as batch_pred
import bigmler.tests.basic_topic_model_steps as topic_pred

def setup_module():
    """Setup for the module

    """
    common_setup_module()
    test = TestTopicModel()
    test.setup_scenario02()


def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()


class TestTopicModel(object):

    def setup(self):
        """
            Debug information
        """
        print("\n-------------------\nTests in: %s\n" % __name__)

    def teardown(self):
        """Calling generic teardown for every method

        """
        self.world = teardown_class()
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)

    def test_scenario01(self):
        """
        Scenario: Successfully building topic model test distributions from dataset:
            Given I created the dataset in setup_scenario02
            And I create BigML topic model resources from dataset to test "<test>" with options "<options>" and log predictions in "<output>"
            And I check that the topic model has been created
            And I check that the topic distributions are ready
            Then the local topic distribution file is like "<topic_distribution_file>"

            Examples:
            | test                    | options                  | output                                   |topic_distribution_file           |
            | ../data/spam.csv        | --test-separator="\t --prediction-header"     |./scenario1_td/topic_distributions.csv   | ./check_files/topic_distributions_spam.csv   |


        """
        print(self.test_scenario01.__doc__)
        examples = [
            ['data/spam.csv', '--test-separator="\t" --prediction-header',
             'scenario1_td/topic_distributions.csv',
             'check_files/topic_distributions_spam.csv',
             './check_files/topic_distributions_spam.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            topic_pred.i_create_all_td_resources_from_dataset( \
                self, example[0], example[1], example[2])
            topic_pred.i_check_create_topic_model(self)
            topic_pred.i_check_create_topic_distributions(self)
            topic_pred.i_check_topic_distributions(self, example[3])


    def setup_scenario02(self):
        """
        Scenario: Successfully building text source from local file:
            Given I create BigML dataset uploading train "<data>" file with attributes "<attributes>" in "<output>"
            And I check that the source has been created
            Then I check that the dataset has been created

            Examples:
            | data               | attributes                     | output                 |
            | ../data/spam.csv   | ../data/spam_attributes.json   |  scenario2_td/topic_distributions.csv  |
        """
        print(self.setup_scenario02.__doc__)
        examples = [
            ['data/spam.csv', 'data/spam_attributes.json', 'scenario2_td/topic_distributions.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            test_pred.i_create_dataset_with_attributes( \
                self, data=example[0], attributes=example[1], output=example[2])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self, suffix=None)



    def test_scenario03(self):
        """
        Scenario: Successfully building test predictions from source
            Given I created the dataset in setup_scenario02
            And I create BigML topic model resources from source to test "<test>" with options "<options>" and log predictions in "<output>"
            And I check that the dataset has been created
            And I check that the topic model has been created
            And I check that the topic distributions are ready
            Then the local topic distribution file is like "<topic_distribution_file>"

            Examples:
            | test                    | options                  | output                                   |topic_distribution_file           |
            | ../data/spam.csv        | --test-separator="\t --prediction-header"     |./scenario3_td/topic_distributions.csv   | ./check_files/topic_distributions_spam.csv   |


        """
        print(self.test_scenario03.__doc__)
        examples = [
            ['data/spam.csv', '--test-separator="\t" --prediction-header',
             'scenario3_td/topic_distributions.csv',
             'check_files/topic_distributions_spam.csv',
             './check_files/topic_distributions_spam.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            topic_pred.i_create_all_td_resources_from_source( \
                self, example[0], example[1], example[2])
            test_pred.i_check_create_dataset(self, suffix=None)
            topic_pred.i_check_create_topic_model(self)
            topic_pred.i_check_create_topic_distributions(self)
            topic_pred.i_check_topic_distributions(self, example[3])


    def test_scenario04(self):
        """
        Scenario: Successfully building test predictions from topic model
            Given I created the dataset in setup_scenario02
            And I create topic model from dataset
            And I create BigML topic model resources from model to test "<test>" with options "<options>" and log predictions in "<output>"
            And I check that the dataset has been created
            And I check that the topic distributions are ready
            Then the local topic distribution file is like "<topic_distribution_file>"

            Examples:
            | test                    | options                  | output                                   |topic_distribution_file           |
            | ../data/spam.csv        | --test-separator="\t --prediction-header"     |./scenario4_td/topic_distributions.csv   | ./check_files/topic_distributions_spam.csv   |


        """
        print(self.test_scenario04.__doc__)
        examples = [
            ['data/spam.csv', '--test-separator="\t" --prediction-header',
             'scenario4_td/topic_distributions.csv',
             'check_files/topic_distributions_spam.csv',
             './check_files/topic_distributions_spam.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            topic_pred.i_create_topic_model_from_dataset(self, example[2])
            topic_pred.i_check_create_topic_model(self)
            topic_pred.i_create_all_td_resources_from_model( \
                self, example[0], example[1], example[2])
            topic_pred.i_check_create_topic_distributions(self)
            topic_pred.i_check_topic_distributions(self, example[3])


    def test_scenario05(self):
        """
        Scenario: Successfully building batch topic distributions from topic model
            Given I created the dataset in setup_scenario02
            And I create BigML batch topic distribution resources from dataset to test "<test>" and log predictions in "<output>"
            And I check that the topic model has been created
            And I check that the batch topic distribution is ready
            Then the local topic distribution file is like "<predictions_file>"

            Examples:
            | test                    | options                  | output                                   |topic_distribution_file           |
            | ../data/spam.csv        | --test-separator="\t --prediction-header" | ./scenario5_td/topic_distributions.csv   | ./check_files/topic_distributions_spam.csv   |


        """
        print(self.test_scenario05.__doc__)
        examples = [
            ['data/spam.csv', '--test-separator="\t" --prediction-header',
             'scenario5_td/topic_distributions.csv',
             'check_files/topic_distributions_spam.csv',
             './check_files/topic_distributions_spam.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            topic_pred.i_create_topic_model_from_dataset(self, example[2])
            topic_pred.i_check_create_topic_model(self)
            topic_pred.i_create_topic_distribution_from_model_remote(self, test=example[0], options=example[1], output=example[2])
            topic_pred.i_check_create_topic_distributions(self)
            # the check between local and remote predictions is removed till we
            # add new options in the local side to match the remote ones
            # topic_pred.i_check_topic_distributions(self, example[3])
