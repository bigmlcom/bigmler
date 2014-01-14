Feature: Upload multi-label source with multiple multi-label fields and produce test predictions
    In order to produce test predictions
    I need to upload a train set
    Then I need to create a dataset a model and local model per label to predict

    Scenario: Successfully building multi-label test predictions from start:
        Given I create BigML multi-label resources tagged as "<tag>" with "<label_separator>" label separator and <number_of_labels> labels uploading train "<data>" file with "<training_separator>" field separator and "<ml_fields>" as multi-label fields using model_fields "<model_fields>" and objective "<objective>" to test "<test>" and log predictions in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created 
        And I check that the models have been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |tag |label_separator |number_of_labels | data                   |training_separator | ml_fields | model_fields | objective | test                        | output                         |predictions_file           |
        |my_multilabelm_1|:|7| ../data/multilabel_multi.csv |,  | type,class | -type,-type - W,-type - A,-type - C,-type - S,-type - R,-type - T,-type - P | class |../data/test_multilabel.csv | ./scenario_mlm_1/predictions.csv | ./check_files/predictions_ml.csv |


    Scenario: Successfully building test predictions from source
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML multi-label resources using source with objective "<objective>" and model fields "<model_fields>" to test "<test>" and log predictions in "<output>"
        And I check that the dataset has been created 
        And I check that the models have been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | objective | model_fields | test                    | output                        |predictions_file           |
        | scenario_mlm_1| {"tag": "my_multilabelm_1", "data": "../data/multilabel_multi.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "./scenario_mlm_1/predictions.csv", "test": "../data/test_multilabel.csv", "ml_fields": "type,class", "model_fields": "-type,-type - W,-type - A,-type - C,-type - S,-type - R,-type - T,-type - P", "objective": "class"}   | class | -type,-type - W,-type - A,-type - C,-type - S,-type - R,-type - T,-type - P |../data/test_multilabel.csv   | ./scenario_mlm_2/predictions.csv   | ./check_files/predictions_ml_comma.csv   |

    Scenario: Successfully building test predictions from dataset
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML multi-label resources using dataset with objective "<objective>" and model fields "<model_fields>" to test "<test>" and log predictions in "<output>"
        And I check that the models have been created
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | objective | model_fields | test                    | output                        |predictions_file           |
        | scenario_mlm_1| {"tag": "my_multilabelm_1", "data": "../data/multilabel_multi.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "./scenario_mlm_1/predictions.csv", "test": "../data/test_multilabel.csv", "ml_fields": "type,class", "model_fields": "-type,-type - W,-type - A,-type - C,-type - S,-type - R,-type - T,-type - P", "objective": "class"}   | class | -type,-type - W,-type - A,-type - C,-type - S,-type - R,-type - T,-type - P |../data/test_multilabel.csv   | ./scenario_mlm_3/predictions.csv   | ./check_files/predictions_ml_comma.csv   |


    Scenario: Successfully building test predictions from models file
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML multi-label resources using models in file "<models_file>" with objective "<objective>" to test "<test>" and log predictions in "<output>"
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | models_file        | objective | test                  | output                      |predictions_file                    |
        | scenario_mlm_1| {"tag": "my_multilabelm_1", "data": "../data/multilabel_multi.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "./scenario_mlm_1/predictions.csv", "test": "../data/test_multilabel.csv", "ml_fields": "type,class", "model_fields": "-type,-type - W,-type - A,-type - C,-type - S,-type - R,-type - T,-type - P", "objective": "class"}   | ./scenario_mlm_1/models | class | ../data/test_multilabel.csv | ./scenario_mlm_4/predictions.csv | ./check_files/predictions_ml_comma.csv |

    Scenario: Successfully building test predictions from models retrieved by tag
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML multi-label resources with labels "<labels>" and objective "<objective>" using models tagged as "<tag>" to test "<test>" and log predictions in "<output>"
        And I check that the predictions are ready
        Then the local prediction file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  |labels      | objective | tag       | test                  | output                      |predictions_file                    |
        | scenario_mlm_1| {"tag": "my_multilabelm_1", "data": "../data/multilabel_multi.csv", "label_separator": ":", "number_of_labels": 7, "training_separator": ",", "output": "./scenario_mlm_1/predictions.csv", "test": "../data/test_multilabel.csv", "ml_fields": "type,class", "model_fields": "-type,-type - W,-type - A,-type - C,-type - S,-type - R,-type - T,-type - P", "objective": "class"}    | Adult,Student | class | my_multilabelm_1 | ../data/test_multilabel.csv | ./scenario_mlm_5/predictions.csv | ./check_files/predictions_ml_labels.csv |

    Scenario: Successfully extending the multi-label source file:
        Given I create BigML a multi-label source with "<label_separator>" label separator and <number_of_labels> labels from train "<data>" file with "<training_separator>" field separator and "<ml_fields>" as multi-label fields and objective "<objective>" and output in "<output_dir>"
        And I check that the source has been created
        Then I check the extended file "<local_file>" has been created
        And the headers of the local extended file are "<headers>"
        And the first row of the local extended file is "<first_row>"

        Examples:
        |label_separator |number_of_labels | data                   |training_separator | ml_fields | objective | output_dir                        |local_file         | headers | first_row |
        |:|7| ../data/multilabel_multi.csv |,  | type,class | class | ./scenario_mlm_6 | ./scenario_mlm_6/extended_multilabel_multi.csv |color,year,price,first_name,last_name,sex,type,class - Adult,class - Child,class - Pensioner,class - Retired,class - Student,class - Teenager,class - Worker,type - A,type - C,type - P,type - R,type - S,type - T,type - W,class | Blue,1992,"1208,6988040134",John,Higgins,Male,W:A:C:S:T:R:P,True,False,False,False,False,False,True,True,True,True,True,True,True,True,Worker:Adult
        |:|7| ../data/multilabel_multi2.csv |,  | Colors,Movies,Hobbies | Hobbies | ./scenario_mlm_7 | ./scenario_mlm_7/extended_multilabel_multi2.csv |Registration Date,Age Range,Gender,Height,Weight,Points,Colors,Movies,Colors - Black,Colors - Blue,Colors - Green,Colors - Grey,Colors - Orange,Colors - Pink,Colors - Purple,Colors - Red,Colors - White,Colors - Yellow,Movies - Action,Movies - Adventure,Movies - Comedy,Movies - Crime,Movies - Erotica,Movies - Fantasy,Movies - Horror,Movies - Mystery,Movies - Philosophical,Movies - Political,Movies - Romance,Movies - Satire,Movies - Thriller,Hobbies - Barbacue,Hobbies - Books,Hobbies - Chat,Hobbies - Cooking,Hobbies - Dance,Hobbies - Disco,Hobbies - Dolls,Hobbies - Family,Hobbies - Films,Hobbies - Fishing,Hobbies - Friends,Hobbies - Jogging,Hobbies - Music,Hobbies - Soccer,Hobbies - Toys,Hobbies - Travel,Hobbies - Videogames,Hobbies - Walking,Hobbies |2011-02-06,19-30,Female,140,47,11,White:Red,Comedy:Romance,False,False,False,False,False,False,False,True,True,False,False,False,True,False,False,False,False,False,False,False,True,False,False,False,False,False,False,False,False,False,False,False,False,True,False,True,False,False,False,False,False,Friends:Music
