Feature: Produce model analysis from a dataset
    In order to produce a k-fold cross-validation, feature or nodes selection
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
        And I create BigML feature selection <kfold>-fold cross-validations improving "<metric>"
        And I check that the <kfold>-datasets have been created
        And I check that the <kfold>-models have been created
        And I check that all the <kfold>-fold cross-validations have been created
        Then the best feature selection is "<selection>", with "<metric>" of <metric_value>

        Examples:
        | data                | output                    | kfold | metric   | selection   | metric_value |
        | ../data/iris_2f.csv | ./scenario_a_2/evaluation | 2     | accuracy | petal width | 99.90%       |
        | ../data/iris_2f.csv | ./scenario_a_3/evaluation | 2     | phi      | petal width | 0.999000     |


    Scenario: Successfully building nodes threshold analysis from dataset:
        Given I create BigML dataset uploading train "<data>" file in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created
        And I create BigML nodes analysis from <min_nodes> to <max_nodes> by <nodes_step> with <kfold>-cross-validation improving "<metric>"
        And I check that the <kfold>-datasets have been created
        And I check that the <kfold>-models have been created
        And I check that all the <kfold>-fold cross-validations have been created
        Then the best node threshold is "<node_threshold>", with "<metric>" of <metric_value>

        Examples:
        | data                | output                  | min_nodes | max_nodes | nodes_step | kfold | metric   | node_threshold   | metric_value |
        | ../data/iris.csv | ./scenario_a_4/evaluation | 3         | 10        | 2         |2     | precision  | 7                | 95.40%         |
