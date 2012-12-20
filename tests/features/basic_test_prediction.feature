Feature: Upload source and produce test predictions
    In order produce test predictions
    I need to upload a train set
    Then I need to create a dataset and a model and a local model to predict

    Scenario: Successfully building test predictions from start:
        Given I create BigML resources uploading train "<data>" file to test "<test>" and log predictions in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created 
        And I check that the model has been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        | data             | test                  | output                      |predictions_file         |
        | ../data/iris.csv | ../data/test_iris.csv | ./scenario1/predictions.csv | ./predictions_check.csv |


    Scenario: Successfully building test predictions from source
        Given I create BigML resources using source to test "<test>" and log predictions in "<output>"
        And I check that the dataset has been created 
        And I check that the model has been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        | test                  | output                      |predictions_file         |
        | ../data/test_iris.csv | ./scenario2/predictions.csv | ./predictions_check.csv |

    Scenario: Successfully building test predictions from dataset
        Given I create BigML resources using dataset to test "<test>" and log predictions in "<output>"
        And I check that the model has been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        | test                  | output                      |predictions_file         |
        | ../data/test_iris.csv | ./scenario3/predictions.csv | ./predictions_check.csv |

    Scenario: Successfully building test predictions from model
        Given I create BigML resources using model to test "<test>" and log predictions in "<output>"
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        | test                  | output                      |predictions_file         |
        | ../data/test_iris.csv | ./scenario4/predictions.csv | ./predictions_check.csv |


    Scenario: Successfully building test predictions from ensemble
        Given I create BigML resources using ensemble of <number_of_models> models to test "<test>" and log predictions in "<output>"
        And I check that the models have been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        | number_of_models | test                  | output                      |predictions_file         |
        | 10               | ../data/test_iris.csv | ./scenario5/predictions.csv | ./predictions_check.csv |


    Scenario: Successfully building test predictions from models file
        Given I create BigML resources using models in file "<models_file>" to test "<test>" and log predictions in "<output>"
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        | models_file        | test                  | output                      |predictions_file         |
        | ./scenario5/models | ../data/test_iris.csv | ./scenario6/predictions.csv | ./predictions_check.csv |


    Scenario: Successfully building test predictions from dataset file
        Given I create BigML resources using dataset in file "<dataset_file>" to test "<test>" and log predictions in "<output>"
        And I check that the model has been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        | dataset_file        | test                  | output                      |predictions_file         |
        | ./scenario2/dataset | ../data/test_iris.csv | ./scenario7/predictions.csv | ./predictions_check.csv |
