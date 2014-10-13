Feature: Create shared datasets, models and evaluations
    In order to create shared resources
    I need to upload a train set
    Then I need to create a dataset and a model and an evaluation

    Scenario: Successfully building dataset, model and evaluation and share them:
        Given I create BigML resources and share them uploading train "<data>" file to evaluate and log evaluation in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created and shared
        And I check that the model has been created and shared
        Then I check that the evaluation has been created and shared

        Examples:
        | data               | output                     |
        | ../data/iris.csv   | ./scenario_sh_1/evaluation |
