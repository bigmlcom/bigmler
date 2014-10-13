Feature: Produce model analysis from a dataset in dev mode
    In order to produce a k-fold cross-validation, feature or nodes selection
    I need to upload a train set
    Then I need to create a dataset and ask for the k-fold cross-validation

    Scenario: Successfully building feature selection from dataset in dev mode:
        Given I want to use api in DEV mode
        And I create BigML dataset in dev mode uploading train "<data>" file in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created
        And I create BigML feature selection <kfold>-fold cross-validations improving "<metric>" in dev mode
        And I check that the <kfold>-datasets have been created
        And I check that the <kfold>-models have been created
        And I check that all the <kfold>-fold cross-validations have been created
        Then the best feature selection is "<selection>", with "<metric>" of <metric_value>

        Examples:
        | data                | output                    | kfold | metric   | selection   | metric_value |
        | ../data/iris_2f.csv | ./scenario_a_2/evaluation | 2     | accuracy | petal width | 100.00%       |
