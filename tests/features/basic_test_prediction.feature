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
        | data               | test                    | output                        |predictions_file           |
        | ../data/grades.csv | ../data/test_grades.csv | ./scenario1_r/predictions.csv | ./check_files/predictions_grades.csv |
        | ../data/iris.csv   | ../data/test_iris.csv   | ./scenario1/predictions.csv   | ./check_files/predictions_iris.csv   |



    Scenario: Successfully building test predictions from source
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML resources using source to test "<test>" and log predictions in "<output>"
        And I check that the dataset has been created 
        And I check that the model has been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
        | scenario1| {"data": "../data/iris.csv", "output": "./scenario1/predictions.csv", "test": "../data/test_iris.csv"}   | ../data/test_iris.csv   | ./scenario2/predictions.csv   | ./check_files/predictions_iris.csv   |

    Scenario: Successfully building test predictions from dataset
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML resources using dataset to test "<test>" and log predictions in "<output>"
        And I check that the model has been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
        | scenario1| {"data": "../data/iris.csv", "output": "./scenario1/predictions.csv", "test": "../data/test_iris.csv"}   | ../data/test_iris.csv   | ./scenario3/predictions.csv   | ./check_files/predictions_iris.csv   |

    Scenario: Successfully building test predictions from model
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>        
        And I create BigML resources using model to test "<test>" and log predictions in "<output>"
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
        | scenario1| {"data": "../data/iris.csv", "output": "./scenario1/predictions.csv", "test": "../data/test_iris.csv"}   | ../data/test_iris.csv   | ./scenario4/predictions.csv   | ./check_files/predictions_iris.csv   |


    Scenario: Successfully building test predictions from ensemble
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs> 
        And I create BigML resources using ensemble of <number_of_models> models to test "<test>" and log predictions in "<output>"
        And I check that the models have been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | number_of_models | test                    | output                        |predictions_file                      |
        | scenario1| {"data": "../data/iris.csv", "output": "./scenario1/predictions.csv", "test": "../data/test_iris.csv"}   | 10               | ../data/test_iris.csv   | ./scenario5/predictions.csv   | ./check_files/predictions_iris.csv   |


    Scenario: Successfully building test predictions from models file
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I have previously executed "<scenario2>" or reproduce it with arguments <kwargs2> 
        And I create BigML resources using models in file "<models_file>" to test "<test>" and log predictions in "<output>"
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  |scenario2    | kwargs2                                                  | models_file        | test                  | output                      |predictions_file                    |
        | scenario1| {"data": "../data/iris.csv", "output": "./scenario1/predictions.csv", "test": "../data/test_iris.csv"}   | scenario5| {"number_of_models": 10, "test": "../data/test_iris.csv", "output": "./scenario5/predictions.csv"}   | ./scenario5/models | ../data/test_iris.csv | ./scenario6/predictions.csv | ./check_files/predictions_iris.csv |


    Scenario: Successfully building test predictions from dataset file
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML resources using dataset in file "<dataset_file>" to test "<test>" and log predictions in "<output>"
        And I check that the model has been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | dataset_file        | test                  | output                      |predictions_file         |
        | scenario1| {"data": "../data/iris.csv", "output": "./scenario1/predictions.csv", "test": "../data/test_iris.csv"}   | ./scenario1/dataset | ../data/test_iris.csv | ./scenario7/predictions.csv | ./check_files/predictions_iris.csv |


    Scenario: Successfully combining test predictions from existing directories
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I have previously executed "<scenario2>" or reproduce it with arguments <kwargs2>
        Given I combine BigML predictions files in "<directory1>" and "<directory2>" into "<output>"
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  |scenario2    | kwargs2                                                  | directory1  | directory2  | output                      |predictions_file         |
        | scenario1| {"data": "../data/iris.csv", "output": "./scenario1/predictions.csv", "test": "../data/test_iris.csv"}   | scenario5| {"number_of_models": 10, "output": "./scenario5/predictions.csv", "test": "../data/test_iris.csv"}   | ./scenario1 | ./scenario5 | ./scenario8/predictions.csv | ./check_files/predictions_iris.csv |

    Scenario: Successfully combining test predictions from existing directories
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I have previously executed "<scenario2>" or reproduce it with arguments <kwargs2>
        And I combine BigML predictions files in "<directory1>" and "<directory2>" into "<output>" with method "<method>"
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  |scenario2    | kwargs2                                                  | directory1  | directory2  | output                         |predictions_file                    | method                 |
        | scenario1| {"data": "../data/iris.csv", "output": "./scenario1/predictions.csv", "test": "../data/test_iris.csv"}   | scenario5| {"number_of_models": 10, "output": "./scenario5/predictions.csv", "test": "../data/test_iris.csv"}   | ./scenario1 | ./scenario5 | ./scenario9/predictions_c.csv  | ./check_files/predictions_iris.csv | "confidence weighted"  |
        | scenario1| {"data": "../data/iris.csv", "output": "./scenario1/predictions.csv", "test": "../data/test_iris.csv"}   | scenario5| {"number_of_models": 10, "output": "./scenario5/predictions.csv", "test": "../data/test_iris.csv"}   | ./scenario1 | ./scenario5 | ./scenario9/predictions_p.csv  | ./check_files/predictions_iris_p.csv | "probability weighted" |
        | scenario1| {"data": "../data/grades.csv", "output": "./scenario1r/predictions.csv", "test": "../data/test_grades.csv"}   | scenario1_r| {"data": "../data/grades.csv", "output": "./scenario1_r/predictions.csv", "test": "../data/test_grades.csv"}   | ./scenario1_r | ./scenario1_r | ./scenario10/predictions_c.csv | ./check_files/predictions_grades.csv | "confidence weighted"  |
        | scenario1| {"data": "../data/grades.csv", "output": "./scenario1r/predictions.csv", "test": "../data/test_grades.csv"}   | scenario1_r| {"data": "../data/grades.csv", "output": "./scenario1_r/predictions.csv", "test": "../data/test_grades.csv"}   | ./scenario1_r | ./scenario1_r | ./scenario10/predictions_p.csv | ./check_files/predictions_grades_p.csv | "probability weighted" |

    Scenario: Successfully building test predictions from dataset specifying objective field and model fields
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML resources using dataset, objective field <objective> and model fields <fields> to test "<test>" and log predictions in "<output>"
        And I check that the model has been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | test                    | output                         |predictions_file                        | objective | fields   |
        | scenario1| {"data": "../data/iris.csv", "output": "./scenario1/predictions.csv", "test": "../data/test_iris.csv"}   | ../data/test_iris.csv   | ./scenario11/predictions.csv   | ./check_files/predictions_iris_b.csv   | 0         | "petal length","petal width" |
        
