Feature: Upload multi-label source and produce evaluations
    In order to create an evaluation
    I need to upload a training set
    Then I need to create a dataset and a model and an evaluation


    Scenario: Successfully building multi-label evaluations from scratch
        Given I create BigML multi-label resources tagged as "<tag>" with "<label_separator>" label separator and "<number_of_labels>" labels uploading train "<data>" file with "<training_separator>" field separator to evaluate and log evaluation in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created 
        And I check that the models have been created
        And I check that the <number_of_labels> evaluations have been created
        And I check that the evaluation is ready
        Then the evaluation file is like "<json_evaluation_file>"

        Examples:
        |tag |label_separator |number_of_labels| data                   |training_separator |  output                          |json_evaluation_file           
        |my_multilabel_e_1|:|7| ../data/multilabel.csv |,| ./scenario_ml_e1/evaluation | ./check_files/evaluation_ml.json 

    Scenario: Successfully building multi-label evaluations from source
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML multi-label resources using source to evaluate and log evaluation in "<output>"
        And I check that the dataset has been created 
        And I check that the models have been created
        And I check that the <number_of_labels> evaluations have been created
        And I check that the evaluation is ready
        Then the evaluation file is like "<json_evaluation_file>"

        Examples:
        |scenario    | kwargs                                                  | number_of_labels                    | output                        |json_evaluation_file          |
        | scenario_ml_e1| {"tag": "my_multilabel_e_1", "data": "../data/multilabel.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "./scenario_ml_e1/evaluation"}   | 7 | ./scenario_ml_e2/evaluation   | ./check_files/evaluation_ml.json   |

    Scenario: Successfully building multi-label evaluations from dataset
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML multi-label resources using dataset to evaluate and log evaluation in "<output>"
        And I check that the models have been created
        And I check that the <number_of_labels> evaluations have been created
        And I check that the evaluation is ready
        Then the evaluation file is like "<json_evaluation_file>"

        Examples:
        |scenario    | kwargs                                                  | number_of_labels                    | output                        |json_evaluation_file          |
        | scenario_ml_e1| {"tag": "my_multilabel_e_1", "data": "../data/multilabel.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "./scenario_ml_e1/evaluation"}   | 7 | ./scenario_ml_e3/evaluation   | ./check_files/evaluation_ml.json   |

    Scenario: Successfully building multi-label evaluations from models file
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML multi-label resources using models in file "<models_file>" to evaluate and log evaluation in "<output>"
        And I check that the <number_of_labels> evaluations have been created
        And I check that the evaluation is ready
        Then the evaluation key "<key>" value for the model is greater than <value>

        Examples:
        |scenario    | kwargs                                                  | models_file | number_of_labels                    | output                        |key          | value
        | scenario_ml_e1| {"tag": "my_multilabel_e_1", "data": "../data/multilabel.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "./scenario_ml_e1/evaluation"}   | ./scenario_ml_e1/models | 7 | ./scenario_ml_e4/evaluation   | average_phi   | 0.8200

    Scenario: Successfully building multi-label evaluations from models retrieved by tag
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML multi-label resources using models tagged as "<tag>" to evaluate and log evaluation in "<output>"
        And I check that the <number_of_labels> evaluations have been created
        And I check that the evaluation is ready
        Then the evaluation key "<key>" value for the model is greater than <value>

        Examples:
        |scenario    | kwargs                                                  | tag | number_of_labels                    | output                        |key          | value
        | scenario_ml_e1| {"tag": "my_multilabel_e_1", "data": "../data/multilabel.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "./scenario_ml_e1/evaluation"}   | my_multilabel_e_1 | 7 | ./scenario_ml_e5/evaluation   | average_phi   | 0.8200
