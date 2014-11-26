Feature: Upload source and produce anomaly scores for test data
    In order produce anomaly score predictions
    I need to upload a train set
    Then I need to create a dataset and an anomaly detector and a local anomaly detector to predict

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

    Scenario: Successfully building test predictions from dataset
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML resources using dataset to find anomaly scores for "<test>" and log predictions in "<output>"
        And I check that the anomaly detector has been created
        And I check that the anomaly scores are ready
        Then the local anomaly scores file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
        | scenario_an_1| {"data": "../data/tiny_kdd.csv", "output": "./scenario_an_1/anomaly_scores.csv", "test": "../data/test_kdd.csv"}   | ../data/test_kdd.csv   | ./scenario_an_3/anomaly_scores.csv   | ./check_files/anomaly_scores_kdd.csv   |

    Scenario: Successfully building test predictions from anomaly
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>        
        And I create BigML resources using anomaly detector to find anomaly scores for "<test>" and log predictions in "<output>"
        And I check that the anomaly scores are ready
        Then the local anomaly scores file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
        | scenario_an_1| {"data": "../data/tiny_kdd.csv", "output": "./scenario_an_1/anomaly_scores.csv", "test": "../data/test_kdd.csv"}   | ../data/test_kdd.csv   | ./scenario_an_4/anomaly_scores.csv   | ./check_files/anomaly_scores_kdd.csv   |

    Scenario: Successfully building test predictions from anomaly detector file
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML resources using anomaly detector in file "<anomaly_file>" to find anomaly scores for "<test>" and log predictions in "<output>"
        And I check that the anomaly scores are ready
        Then the local anomaly scores file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | anomaly_file        | test                  | output                      |predictions_file                    |
        | scenario_an_1| {"data": "../data/tiny_kdd.csv", "output": "./scenario_an_1/anomaly_scores.csv", "test": "../data/test_kdd.csv"}   | ./scenario_an_1/anomalies | ../data/test_kdd.csv | ./scenario_an_5/anomaly_scores.csv | ./check_files/anomaly_scores_kdd.csv |

    Scenario: Successfully building test predictions from anomaly
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>        
        And I create BigML resources using local anomaly detector in "<scenario>" to find anomaly scores for "<test>" and log predictions in "<output>"
        And I check that the anomaly scores are ready
        Then the local anomaly scores file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
        | scenario_an_1| {"data": "../data/tiny_kdd.csv", "output": "./scenario_an_1/anomaly_scores.csv", "test": "../data/test_kdd.csv"}   | ../data/test_kdd.csv   | ./scenario_an_6/anomaly_scores.csv   | ./check_files/anomaly_scores_kdd.csv   |
