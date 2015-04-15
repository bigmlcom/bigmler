Feature: Upload source and produce test predictions
    In order produce test predictions
    I need to upload a train set
    Then I need to create a dataset and a model and a local model to predict

    Scenario: Successfully building test predictions from start with no headers:
        Given I create BigML resources uploading train "<data>" file with no headers to test "<test>" with no headers and log predictions in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created
        And I check that the model has been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        | data               | test                    | output                        |predictions_file           |
        | ../data/iris_nh.csv   | ../data/test_iris_nh.csv   | ./scenario1_nh/predictions.csv   | ./check_files/predictions_iris.csv   |

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
        And I check that the ensemble has been created
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


    Scenario: Successfully building cross-validation from dataset
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create a BigML cross-validation with rate <rate> using the dataset in file "<dataset_file>" and log results in "<output>"
        And I check that the models have been created
        And I check that the evaluations have been created
        Then the cross-validation json model info is like the one in "<cv_file>"

        Examples:
        |scenario    | kwargs                                                  | rate | dataset_file | output                         |cv_file |
        | scenario1| {"data": "../data/iris.csv", "output": "./scenario1/predictions.csv", "test": "../data/test_iris.csv"}   | 0.05 | ./scenario1/dataset | ./scenario12/cross-validation   | ./check_files/cross_validation.json   |

    Scenario: Successfully building a source with a given locale and storing its result
        Given I create a BigML source from file "<data>" with locale "<locale>", field attributes "<field_attributes>" and types file "<types>" storing results in "<output>"
        Then I check that the stored source file exists
        And the locale of the source is "<bigml_locale>"
        And the type of field "<field_id>" is "<type>"
        And the label of field "<field_id>" is "<label>"

        Examples:
        |data             | locale        | field_attributes | types             | output                    | bigml_locale | field_id | type | label
        | ../data/iris.csv| es_ES.UTF-8   |../data/field_attributes.txt |../data/types.txt |./scenario13/store_file    | es_ES        | 000004   | text | species label


    Scenario: Successfully building test predictions from start with user-given separator:
        Given I create BigML resources uploading train "<data>" file to test "<test>" and log predictions in "<output>" with "<separator>" as test field separator
        And I check that the source has been created
        And I check that the dataset has been created
        And I check that the model has been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        | data               | test                    | separator | output                        |predictions_file           |
        | ../data/iris.csv   | ../data/test_iris.tsv   | "\t"        |./scenario14/predictions.csv   | ./check_files/predictions_iris.csv   |

    Scenario: Successfully building test predictions from start with different prediction file format:
        Given I create BigML resources uploading train "<data>" file to test "<test>" and log predictions in "<output>" with prediction options "<options>"
        And I check that the source has been created
        And I check that the dataset has been created
        And I check that the model has been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        | data               | test                    | output                        |options     |predictions_file           |
        | ../data/iris.csv   | ../data/test_iris.csv   |./scenario15/predictions.csv   |--prediction-header --prediction-fields 'petal length,petal width' --prediction-info full | ./check_files/predictions_iris_h.csv   |

    Scenario: Successfully building threshold test predictions from ensemble
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML resources using ensemble of <number_of_models> models with replacement to test "<test>" and log predictions in "<output>"
        And I check that the ensemble has been created
        And I check that the predictions are ready
        And I create BigML resources using the previous ensemble with different thresholds to test "<test>" and log predictions in "<output2>" and "<output3>"
        Then local predictions for different thresholds in "<output2>" and "<output3>" are different

        Examples:
        |scenario    | kwargs                                                  | number_of_models | test                    | output                  | output2 | output3
        | scenario1| {"data": "../data/iris.csv", "output": "./scenario1/predictions.csv", "test": "../data/test_iris.csv"}   | 10              | ../data/test_iris.csv   | ./scenario16/predictions.csv   | ./scenario16/predictions2.csv | ./scenario16/predictions3.csv

    Scenario: Successfully building test predictions from local model
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML resources using local model in "<scenario>" to test "<test>" and log predictions in "<output>"
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
        | scenario1| {"data": "../data/iris.csv", "output": "./scenario1/predictions.csv", "test": "../data/test_iris.csv"}   | ../data/test_iris.csv   | ./scenario17/predictions.csv   | ./check_files/predictions_iris.csv   |

    Scenario: Successfully building test predictions from ensemble
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        Given I have previously executed "<scenario2>" or reproduce it with arguments <kwargs2>
        And I create BigML resources using local ensemble of <number_of_models> models in "<scenario2>" to test "<test>" and log predictions in "<output>"
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  |scenario2    | kwargs2                                                  | number_of_models | test                    | output                        |predictions_file                      |
        | scenario1| {"data": "../data/iris.csv", "output": "./scenario1/predictions.csv", "test": "../data/test_iris.csv"}   | scenario5| {"number_of_models": 10, "output": "./scenario5/predictions.csv", "test": "../data/test_iris.csv"}       | 10               | ../data/test_iris.csv   | ./scenario18/predictions.csv   | ./check_files/predictions_iris.csv   |

    Scenario: Successfully building test predictions from start using median:
        Given I create BigML resources uploading train "<data>" file using the median to test "<test>" and log predictions in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created
        And I check that the model has been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        | data               | test                    | output                       |predictions_file           |
        | ../data/grades.csv | ../data/test_grades.csv | ./scenario19/predictions.csv | ./check_files/predictions_grades_median.csv |


    Scenario: Successfully building test predictions using median from ensemble
        Given I create BigML resources from "<data>" using ensemble of <number_of_models> models to test "<test>" using median and log predictions in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created
        And I check that the ensemble has been created
        And I check that the models in the ensembles have been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |data               | number_of_models | test                      | output                         | predictions_file                         |
        | ../data/grades.csv| 5                | ../data/test_grades.csv   | ./scenario20/predictions.csv   | ./check_files/predictions_grades_median_e.csv   |
