# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015 BigML
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


""" Testing Anomaly Detector scores

"""
from world import world, setup_module, teardown_module, teardown_class

import basic_tst_prediction_steps as test_pred
import basic_anomaly_prediction_steps as test_anomaly


class TestAnomaly(object):

    def teardown(self):
        """Calling generic teardown for every method

        """
        teardown_class()

    def setup(self):
        """No setup operations for every method at present

        """
        pass

    def test_scenario1(self):
        """
            Scenario: Successfully building test anomaly scores from scratch:
                Given I create BigML resources uploading train "<data>" file to create anomaly scores for "<test>" and log predictions in "<output>"
                And I check that the source has been created
                And I check that the dataset has been created
                And I check that the anomaly detector has been created
                And I check that the anomaly scores are ready
                Then the local anomaly scores file is like "<predictions_file>"

                Examples:
                | data                 | test               | output                           |predictions_file           |
                | ../data/tiny_kdd.csv | ../data/test_kdd.csv | ./scenario_an_1_r/anomaly_scores.csv | ./check_files/anomaly_scores_kdd.csv |
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/tiny_kdd.csv', 'data/test_kdd.csv', 'scenario_an_1_r/anomaly_scores.csv', 'check_files/anomaly_scores_kdd.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            test_anomaly.i_create_all_anomaly_resources(self, data=example[0], test=example[1], output=example[2])
            test_pred.i_check_create_source(self)
            test_pred.i_check_create_dataset(self)
            test_anomaly.i_check_create_anomaly(self)
            test_anomaly.i_check_create_anomaly_scores(self)
            test_anomaly.i_check_anomaly_scores(self, example[3])

    def test_scenario2(self):
        """
            Scenario: Successfully building test predictions from source
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using source to find anomaly scores for "<test>" and log predictions in "<output>"
                And I check that the dataset has been created
                And I check that the anomaly detector has been created
                And I check that the anomaly scores are ready
                Then the local anomaly scores file is like "<predictions_file>"

                Examples:
                |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
                | scenario_an_1| {"data": "../data/tiny_kdd.csv", "output": "./scenario_an_1/anomaly_scores.csv", "test": "../data/test_kdd.csv"}   | ../data/test_kdd.csv   | ./scenario_an_2/anomaly_scores.csv   | ./check_files/anomaly_scores_kdd.csv   |

        """
        print self.test_scenario2.__doc__
        examples = [
            ['scenario_an_1', '{"data": "data/tiny_kdd.csv", "output": "scenario_an_1/anomaly_scores.csv", "test": "data/test_kdd.csv"}', 'data/test_kdd.csv', 'scenario_an_2/anomaly_scores.csv', 'check_files/anomaly_scores_kdd.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            test_anomaly.i_create_anomaly_resources_from_source(self, test=example[2], output=example[3])
            test_pred.i_check_create_dataset(self)
            test_anomaly.i_check_create_anomaly(self)
            test_anomaly.i_check_create_anomaly_scores(self)
            test_anomaly.i_check_anomaly_scores(self, example[4])

    def test_scenario3(self):
        """
            Scenario: Successfully building test predictions from dataset
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using dataset to find anomaly scores for "<test>" and log predictions in "<output>"
                And I check that the anomaly detector has been created
                And I check that the anomaly scores are ready
                Then the local anomaly scores file is like "<predictions_file>"

                Examples:
                |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
                | scenario_an_1| {"data": "../data/tiny_kdd.csv", "output": "./scenario_an_1/anomaly_scores.csv", "test": "../data/test_kdd.csv"}   | ../data/test_kdd.csv   | ./scenario_an_3/anomaly_scores.csv   | ./check_files/anomaly_scores_kdd.csv   |

        """
        print self.test_scenario3.__doc__
        examples = [
            ['scenario_an_1', '{"data": "data/tiny_kdd.csv", "output": "scenario_an_1/anomaly_scores.csv", "test": "data/test_kdd.csv"}', 'data/test_kdd.csv', 'scenario_an_3/anomaly_scores.csv', 'check_files/anomaly_scores_kdd.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            test_anomaly.i_create_anomaly_resources_from_dataset(self, test=example[2], output=example[3])
            test_anomaly.i_check_create_anomaly(self)
            test_anomaly.i_check_create_anomaly_scores(self)
            test_anomaly.i_check_anomaly_scores(self, example[4])

    def test_scenario4(self):
        """
            Scenario: Successfully building test predictions from anomaly
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using anomaly detector to find anomaly scores for "<test>" and log predictions in "<output>"
                And I check that the anomaly scores are ready
                Then the local anomaly scores file is like "<predictions_file>"

                Examples:
                |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
                | scenario_an_1| {"data": "../data/tiny_kdd.csv", "output": "./scenario_an_1/anomaly_scores.csv", "test": "../data/test_kdd.csv"}   | ../data/test_kdd.csv   | ./scenario_an_4/anomaly_scores.csv   | ./check_files/anomaly_scores_kdd.csv   |

        """
        print self.test_scenario4.__doc__
        examples = [
            ['scenario_an_1', '{"data": "data/tiny_kdd.csv", "output": "scenario_an_1/anomaly_scores.csv", "test": "data/test_kdd.csv"}', 'data/test_kdd.csv', 'scenario_an_4/anomaly_scores.csv', 'check_files/anomaly_scores_kdd.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            test_anomaly.i_create_anomaly_resources_from_anomaly_detector(self, test=example[2], output=example[3])
            test_anomaly.i_check_create_anomaly_scores(self)
            test_anomaly.i_check_anomaly_scores(self, example[4])

    def test_scenario5(self):
        """
            Scenario: Successfully building test predictions from anomaly detector file
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using anomaly detector in file "<anomaly_file>" to find anomaly scores for "<test>" and log predictions in "<output>"
                And I check that the anomaly scores are ready
                Then the local anomaly scores file is like "<predictions_file>"

                Examples:
                |scenario    | kwargs                                                  | anomaly_file        | test                  | output                      |predictions_file                    |
                | scenario_an_1| {"data": "../data/tiny_kdd.csv", "output": "./scenario_an_1/anomaly_scores.csv", "test": "../data/test_kdd.csv"}   | ./scenario_an_1/anomalies | ../data/test_kdd.csv | ./scenario_an_5/anomaly_scores.csv | ./check_files/anomaly_scores_kdd.csv |

        """
        print self.test_scenario5.__doc__
        examples = [
            ['scenario_an_1', '{"data": "data/tiny_kdd.csv", "output": "scenario_an_1/anomaly_scores.csv", "test": "data/test_kdd.csv"}', 'scenario_an_1/anomalies',  'data/test_kdd.csv', 'scenario_an_5/anomaly_scores.csv', 'check_files/anomaly_scores_kdd.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            test_anomaly.i_create_anomaly_resources_from_anomaly_file(self, anomaly_file=example[2], test=example[3], output=example[4])
            test_anomaly.i_check_create_anomaly_scores(self)
            test_anomaly.i_check_anomaly_scores(self, example[5])

    def test_scenario6(self):
        """
            Scenario: Successfully building test predictions from anomaly
                Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
                And I create BigML resources using local anomaly detector in "<scenario>" to find anomaly scores for "<test>" and log predictions in "<output>"
                And I check that the anomaly scores are ready
                Then the local anomaly scores file is like "<predictions_file>"

                Examples:
                |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
                | scenario_an_1| {"data": "../data/tiny_kdd.csv", "output": "./scenario_an_1/anomaly_scores.csv", "test": "../data/test_kdd.csv"}   | ../data/test_kdd.csv   | ./scenario_an_6/anomaly_scores.csv   | ./check_files/anomaly_scores_kdd.csv   |

        """
        print self.test_scenario6.__doc__
        examples = [
            ['scenario_an_1', '{"data": "data/tiny_kdd.csv", "output": "scenario_an_1/anomaly_scores.csv", "test": "data/test_kdd.csv"}', 'data/test_kdd.csv', 'scenario_an_6/anomaly_scores.csv', 'check_files/anomaly_scores_kdd.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            test_pred.i_have_previous_scenario_or_reproduce_it(self, example[0], example[1])
            test_anomaly.i_create_anomaly_resources_from_local_anomaly_detector(self, example[0], test=example[2], output=example[3])
            test_anomaly.i_check_create_anomaly_scores(self)
            test_anomaly.i_check_anomaly_scores(self, example[4])
