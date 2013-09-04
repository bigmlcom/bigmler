Feature: Upload multi-label source and produce test predictions
    In order produce test predictions
    I need to upload a train set
    Then I need to create a dataset a model and local model per label to predict

    Scenario: Successfully building multi-label test predictions from start:
        Given I create BigML multi-label resources tagged as "<tag>" with "<label_separator>" label separator and <number_of_labels> labels uploading train "<data>" file with "<training_separator>" field separator to test "<test>" and log predictions in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created 
        And I check that the models have been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |tag |label_separator |number_of_labels | data                   |training_separator | test                        | output                          |predictions_file           |
        |my_multilabel_1|:|7| ../data/multilabel.csv |,| ../data/test_multilabel.csv | ./scenario_ml_1/predictions.csv | ./check_files/predictions_ml.csv |


    Scenario: Successfully building test predictions from source
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML multi-label resources using source to test "<test>" and log predictions in "<output>"
        And I check that the dataset has been created 
        And I check that the models have been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
        | scenario_ml_1| {"tag": "my_multilabel_1", "data": "../data/multilabel.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "./scenario_ml_1/predictions.csv", "test": "../data/test_multilabel.csv"}   | ../data/test_multilabel.csv   | ./scenario_ml_2/predictions.csv   | ./check_files/predictions_ml_comma.csv   |

    Scenario: Successfully building test predictions from dataset
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML multi-label resources using dataset to test "<test>" and log predictions in "<output>"
        And I check that the models have been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
        | scenario_ml_1| {"tag": "my_multilabel_1", "data": "../data/multilabel.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "./scenario_ml_1/predictions.csv", "test": "../data/test_multilabel.csv"}    | ../data/test_multilabel.csv   | ./scenario_ml_3/predictions.csv   | ./check_files/predictions_ml_comma.csv   |


    Scenario: Successfully building test predictions from models file
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML multi-label resources using models in file "<models_file>" to test "<test>" and log predictions in "<output>"
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | models_file        | test                  | output                      |predictions_file                    |
        | scenario_ml_1| {"tag": "my_multilabel_1", "data": "../data/multilabel.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "./scenario_ml_1/predictions.csv", "test": "../data/test_multilabel.csv"}   | ./scenario_ml_1/models | ../data/test_multilabel.csv | ./scenario_ml_4/predictions.csv | ./check_files/predictions_ml_comma.csv |

    Scenario: Successfully building test predictions from models retrieved by tag
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML multi-label resources using models tagged as "<tag>" to test "<test>" and log predictions in "<output>"
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | tag       | test                  | output                      |predictions_file                    |
        | scenario_ml_6| {"tag": "my_multilabel_5", "data": "../data/multilabel.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "./scenario_ml_6/predictions.csv", "test": "../data/test_multilabel.csv"}    | my_multilabel_5 | ../data/test_multilabel.csv | ./scenario_ml_5/predictions.csv | ./check_files/predictions_ml_comma.csv |

