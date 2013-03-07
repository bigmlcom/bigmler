Feature: Upload source and produce evaluation
    In order produce an evaluation
    I need to upload a train set
    Then I need to create a dataset and a model and an evaluation

    Scenario: Successfully building evaluations from start:
        Given I create BigML resources uploading train "<data>" file to evaluate and log evaluation in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created 
        And I check that the model has been created
        And I check that the evaluation has been created
        Then the evaluation file is like "<json_evaluation_file>"

        Examples:
        | data             | output                   | json_evaluation_file    |
        | ../data/iris.csv | ./scenario_e1/evaluation | ./check_files/evaluation_iris.json |


    Scenario: Successfully building evaluations from source
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs> 
        And I create BigML resources using source to evaluate and log evaluation in "<output>"
        And I check that the dataset has been created 
        And I check that the model has been created
        And I check that the evaluation has been created
        Then the evaluation file is like "<json_evaluation_file>"

        Examples:
        |scenario    | kwargs                                                  | data             | output_prev              | output                   | json_evaluation_file    |
        | scenario_e1| {"data": "../data/iris.csv", "output": "./scenario_e1/predictions.csv"}   | ../data/iris.csv | ./scenario_e1/evaluation | ./scenario_e2/evaluation | ./check_files/evaluation_iris.json |

    Scenario: Successfully building evaluations from dataset
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs> 
        And I create BigML resources using dataset to evaluate and log evaluation in "<output>"
        And I check that the model has been created
        And I check that the evaluation has been created
        Then the evaluation file is like "<json_evaluation_file>"

        Examples:
        |scenario    | kwargs                                                  | data             | output_prev              | output                   | json_evaluation_file    |
        | scenario_e1| {"data": "../data/iris.csv", "output": "./scenario_e1/predictions.csv"}   | ../data/iris.csv | ./scenario_e1/evaluation | ./scenario_e3/evaluation | ./check_files/evaluation_iris.json |

    Scenario: Successfully building evaluation from model and test file
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs> 
        And I create BigML resources using test file "<test>" to evaluate a model and log evaluation in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created 
        And I check that the evaluation has been created
        Then the evaluation file is like "<json_evaluation_file>"

        Examples:
        |scenario    | kwargs                                                  | data             | output_prev              | test             | output                   | json_evaluation_file     |
        | scenario_e1| {"data": "../data/iris.csv", "output": "./scenario_e1/predictions.csv"}   | ../data/iris.csv | ./scenario_e1/evaluation | ../data/iris.csv | ./scenario_e4/evaluation | ./check_files/evaluation_iris2.json |


    Scenario: Successfully building evaluation from model and dataset
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs> 
        And I create BigML resources using a dataset to evaluate a model and log evaluation in "<output>"
        And I check that the evaluation has been created
        Then the evaluation file is like "<json_evaluation_file>"

        Examples:
        |scenario    | kwargs                                                  | data             | output_prev              | output                   | json_evaluation_file     |
        | scenario_e1| {"data": "../data/iris.csv", "output": "./scenario_e1/predictions.csv"}   | ../data/iris.csv | ./scenario_e1/evaluation | ./scenario_e5/evaluation | ./check_files/evaluation_iris2.json |
