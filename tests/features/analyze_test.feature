Feature: Produce k-fold cross-validation form a dataset
    In order to produce a k-fold cross-validation
    I need to upload a train set
    Then I need to create a dataset and ask for the k-fold cross-validation

    Scenario: Successfully building k-fold cross-validation from dataset:
        Given I create BigML dataset uploading train "<data>" file in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created
        And I create BigML <kfold>-fold cross-validation
        And I check that the <kfold>-datasets have been created
        And I check that the <kfold>-models have been created
        And I check that the <kfold>-fold cross-validation has been created
        Then the evaluation file is like "<json_evaluation_file>"

        Examples:
        | data             | output                    | kfold | json_evaluation_file               |
        | ../data/iris.csv | ./scenario_a_1/evaluation | 2     | ./check_files/evaluation_kfold.json |

    Scenario: Successfully building feature selection from dataset:
        Given I create BigML dataset uploading train "<data>" file in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created
        And I create BigML feature selection <kfold>-fold cross-validations
        And I check that the <kfold>-datasets have been created
        And I check that the <kfold>-models have been created
        And I check that all the <kfold>-fold cross-validations have been created
        Then the best feature selection is "<selection>"

        Examples:
        | data                  | output                    | kfold | selection               |
        | ../data/iris_2f.csv | ./scenario_a_2/evaluation | 2     | petal width |
