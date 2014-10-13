Feature: Create predictions, batch predictions and evaluations with proportional missing strategy
    In order to create resources with proportional missing strategy
    I need to upload a train set with missing values
    Then I need to create a dataset and a model and a local model to predict

    Scenario: Successfully building test predictions with proportional missing strategy:
        Given I create BigML resources uploading train "<data>" file to test "<test>" with proportional missing strategy and log predictions in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created 
        And I check that the model has been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        | data               | test                          | output                            |predictions_file           |
        | ../data/iris.csv   | ../data/test_iris_nulls.csv   | ./scenario_mis_1/predictions.csv | ./check_files/predictions_iris_nulls.csv   |


    Scenario: Successfully building test predictions from scratch:
        Given I create BigML resources uploading train "<data>" file to test "<test>" remotely with proportional missing strategy and log predictions in "<output>"
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
        | ../data/iris.csv   | ../data/test_iris_nulls.csv   | ./scenario_mis_2/predictions.csv   | ./check_files/predictions_iris_nulls.csv   


    Scenario: Successfully building evaluations from start:
        Given I create BigML resources uploading train "<data>" file to create model and log in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created 
        And I check that the model has been created
        And I evaluate "<test>" with proportional missing strategy
        And I check that the source has been created
        And I check that the dataset has been created
        And I check that the evaluation has been created
        Then the evaluation file is like "<json_evaluation_file>"

        Examples:
        | data             | test                          | output                      | json_evaluation_file    |
        | ../data/iris.csv | ../data/iris_nulls.csv   | ./scenario_mis_3/evaluation | ./check_files/evaluation_iris_nulls.json |
