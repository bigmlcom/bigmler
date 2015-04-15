Feature: Upload source and produce remote batch anomaly scores test predictions
    In order to produce test predictions
    I need to upload a train set and a test set
    Then I need to create a dataset and an anomaly and a batch anomaly scores prediction to predict


    Scenario: Successfully building test anomaly score predictions from scratch:
        Given I create BigML resources uploading train "<data>" file to find anomaly scores for "<test>" remotely with mapping file "<fields_map>" and log predictions in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created
        And I check that the anomaly detector has been created
        And I check that the source has been created from the test file
        And I check that the dataset has been created from the test file
        And I check that the batch anomaly scores prediction has been created
        And I check that the anomaly scores are ready
        Then the local anomaly scores file is like "<predictions_file>"

        Examples:
        | data               | test                    | fields_map | output                        |predictions_file           |
        | ../data/grades.csv | ../data/grades_perm.csv | ../data/grades_fields_map_perm.csv | ./scenario_ab_1_r/anomalies.csv | ./check_files/anomaly_scores_grades.csv |

    Scenario: Successfully building test anomaly score predictions from test split:
        Given I create BigML resources uploading train "<data>" file to find anomaly scores with test split "<test_split>" remotely and log predictions in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created
        And I check that the anomaly detector has been created
        And I check that the train dataset has been created
        And I check that the dataset has been created from the test file
        And I check that the batch anomaly scores prediction has been created
        And I check that the anomaly scores are ready
        Then the local anomaly scores file is like "<predictions_file>"

        Examples:
        | data             | test_split | output                 |predictions_file           |
        | ../data/iris.csv | 0.2 | ./scenario_ab_2/anomalies.csv | ./check_files/anomaly_scores_iris.csv |

    Scenario: Successfully building test anomaly score predictions from test split in a dataset:
        Given I create BigML resources uploading train "<data>" file to find anomaly scores with test split "<test_split>" remotely saved to dataset with no CSV output and log resources in "<output_dir>"
        And I check that the source has been created
        And I check that the dataset has been created
        And I check that the anomaly detector has been created
        And I check that the train dataset has been created
        And I check that the dataset has been created from the test file
        And I check that the batch anomaly scores prediction has been created
        Then I check that the batch anomaly scores dataset exists
        And no local CSV file is created

        Examples:
        | data             | test_split | output_dir      |
        | ../data/iris.csv | 0.2        | ./scenario_ab_3 |

    Scenario: Successfully building test anomaly score predictions from training set as a dataset:
        Given I create BigML resources uploading train "<data>" file to find anomaly scores for the training set remotely saved to dataset with no CSV output and log resources in "<output_dir>"
        And I check that the source has been created
        And I check that the dataset has been created
        And I check that the anomaly detector has been created
        And I check that the batch anomaly scores prediction has been created
        Then I check that the batch anomaly scores dataset exists
        And no local CSV file is created

        Examples:
        | data             | output_dir      |
        | ../data/iris.csv | ./scenario_ab_4 |
