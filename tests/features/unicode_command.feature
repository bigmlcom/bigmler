Feature: Upload source and produce test predictions with unicode arguments
    In order produce test predictions
    I need to upload a train set
    Then I need to create a dataset and a model and a local model to predict

    Scenario: Successfully building test predictions from dataset specifying objective field and model fields
        Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
        And I check that the source has been created
        And I check that the dataset has been created
        And I create BigML resources using dataset, objective field <objective> and model fields <fields> to test "<test>" and log predictions in "<output>"
        And I check that the model has been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |data    | output_dir               | test                    | output                         |predictions_file                        | objective | fields   |
        | ../data/iris_2fb.csv| ./scénario1 | ../data/test_iris2fb.csv   | ./scénario1/predictions.csv   | ./check_files/predictions_iris_2fb.csv   | spécies     | "pétal width" |
