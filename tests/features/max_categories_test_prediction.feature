Feature: Create datasets with a maximum of categories and produce test predictions
    In order to produce test predictions
    I need to create a set of datasets with a maximum of categories each
    Then I need to create a model per dataset to predict

    Scenario: Successfully building test predictions from training data using datasets with max categories
        Given I create BigML resources from "<data>" with <max_categories> as categories limit and <objective> as objective field to test "<test>" and log predictions in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created
        And I check that the max_categories datasets have been created
        And I check that the models have been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |data |max_categories | objective | test                        | output                          |predictions_file           |
        |../data/iris.csv |1| species |../data/test_iris.csv | ./scenario_mc_1/predictions.csv | ./check_files/predictions_mc.csv |


    Scenario: Successfully building test predictions from source using datasets with max categories
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML resources with <max_categories> as categories limit and <objective> as objective field using source to test "<test>" and log predictions in "<output>"
        And I check that the dataset has been created
        And I check that the max_categories datasets have been created
        And I check that the models have been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  |max_categories| objective | test                    | output                        |predictions_file           |
        | scenario_mc_1| {"data": "../data/iris.csv", "max_categories": "1", "objective": "species", "output": "./scenario_mc_1/predictions.csv", "test": "../data/test_iris.csv"}   |1| species | ../data/test_iris.csv   | ./scenario_mc_2/predictions.csv   | ./check_files/predictions_mc.csv   |


    Scenario: Successfully building test predictions from dataset using datasets with max categories
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML resources with <max_categories> as categories limit and <objective> as objective field using dataset to test "<test>" and log predictions in "<output>"
        And I check that the max_categories datasets have been created
        And I check that the models have been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  |max_categories|objective | test                    | output                        |predictions_file           |
        | scenario_mc_1| {"data": "../data/iris.csv", "max_categories": "1", "objective": "species", "output": "./scenario_mc_1/predictions.csv", "test": "../data/test_iris.csv"}   |1| species |../data/test_iris.csv   | ./scenario_mc_3/predictions.csv   | ./check_files/predictions_mc.csv   |


    Scenario: Successfully building ensembles test predictions from models file with max categories
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML resources using models in file "<models_file>" to test "<test>" and log predictions with combine method in "<output>"
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  |models_file| test                    | output                        |predictions_file           |
        | scenario_mc_1| {"data": "../data/iris.csv", "max_categories": "1", "objective": "species", "output": "./scenario_mc_1/predictions.csv", "test": "../data/test_iris.csv"}   | scenario_mc_1/models | ../data/test_iris.csv   | ./scenario_mc_4/predictions.csv   | ./check_files/predictions_mc.csv   |
