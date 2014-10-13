Feature: Create predictions with models using missing splits
    In order to create models and predictions with missing splits
    I need to upload a train set with missing values
    Then I need to create a dataset and a model and a local model to predict

    Scenario: Successfully building test predictions with missing-splits model:
        Given I create BigML resources uploading train "<data>" file to test "<test>" with a missing-splits model and log predictions in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created 
        And I check that the model has been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        | data               | test                          | output                            |predictions_file           |
        | ../data/iris_missing.csv   | ../data/test_iris_missing.csv   | ./scenario_mspl_1/predictions.csv | ./check_files/predictions_iris_missing.csv   |


    Scenario: Successfully building test predictions from scratch:
        Given I create BigML resources uploading train "<data>" file to test "<test>" remotely with a missing-splits model and log predictions in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created 
        And I check that the model has been created
        And I check that the source has been created from the test file
        And I check that the dataset has been created from the test file
        And I check that the batch prediction has been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        | data               | test                    | output                        |predictions_file           |
        | ../data/iris_missing.csv   | ../data/test_iris_missing.csv   | ./scenario_mspl_2/predictions.csv   | ./check_files/predictions_iris_missing.csv
