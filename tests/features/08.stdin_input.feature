Feature: Create model and predictions from stdin streamed data
    In order to create model and predictions from stdin streamed data
    I need to send to stdin a training set
    Then I need to create a dataset and a model and prediction

    Scenario: Successfully building a model from data streamed to stdin:
        Given I create a BigML source from stdin using train "<data>" file and logging in "<output_dir>"
        Then I check that the source has been created

        Examples:
        | data               | output_dir      |
        | ../data/iris.csv   | ./scenario_st_1 |

    Scenario: Successfully building predictions for data streamed to stdin:
        Given I create BigML resources uploading train "<data>" file to test "<test>" read from stdin and log predictions in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created 
        And I check that the model has been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        | data               | test                    | output                            |predictions_file           |
        | ../data/iris.csv   | ../data/test_iris.csv   | ./scenario_st_2/predictions.csv   | ./check_files/predictions_iris.csv   |
