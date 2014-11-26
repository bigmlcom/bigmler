Feature: Upload multi-label source and produce test predictions
    In order to produce test predictions
    I need to upload a train set
    Then I need to create a dataset an ensemble and local ensemble per label to predict

    Scenario: Successfully building multi-label test predictions from start:
        Given I create BigML multi-label resources tagged as "<tag>" with "<label_separator>" label separator and <number_of_labels> labels uploading train "<data>" file with "<training_separator>" field separator and <number_of_models> models ensembles to test "<test>" and log predictions in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created 
        And I check that the models in the ensembles have been created
        Then I check that the predictions are ready

        Examples:
        |tag |label_separator |number_of_labels | data                   |training_separator |number_of_models | test                        | output                                   |
        |my_multilabel_1|:|7| ../data/multilabel.csv |,|10| ../data/test_multilabel.csv | ./scenario_mle_1/predictions.csv


    Scenario: Successfully building test predictions from source
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML multi-label resources using source and <number_of_models> models ensembles to test "<test>" and log predictions in "<output>"
        And I check that the dataset has been created 
        And I check that the models in the ensembles have been created
        Then I check that the predictions are ready

        Examples:
        |scenario    | kwargs                                                  |number_of_models |test                    | output                               |
        | scenario_mle_1| {"tag": "my_multilabel_1", "data": "../data/multilabel.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "./scenario_mle_1/predictions.csv", "test": "../data/test_multilabel.csv", "number_of_models": 10}   |10| ../data/test_multilabel.csv   | ./scenario_mle_2/predictions.csv   

    Scenario: Successfully building test predictions from dataset
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML multi-label resources using dataset and <number_of_models> models ensembles to test "<test>" and log predictions in "<output>"
        And I check that the models in the ensembles have been created
        Then I check that the predictions are ready

        Examples:
        |scenario    | kwargs                                                  | number_of_models |test                    | output                                   |
        | scenario_mle_1| {"tag": "my_multilabel_1", "data": "../data/multilabel.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "./scenario_mle_1/predictions.csv", "test": "../data/test_multilabel.csv", "number_of_models": 10}    |10| ../data/test_multilabel.csv   | ./scenario_mle_3/predictions.csv    
