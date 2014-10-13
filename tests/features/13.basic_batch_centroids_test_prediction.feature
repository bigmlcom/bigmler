Feature: Upload source and produce remote batch centroids test predictions
    In order to produce test predictions
    I need to upload a train set and a test set
    Then I need to create a dataset and a cluster and a batch centroid prediction to predict


    Scenario: Successfully building test centroid predictions from scratch:
        Given I create BigML resources uploading train "<data>" file to find centroids for "<test>" remotely with mapping file "<fields_map>" and log predictions in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created 
        And I check that the cluster has been created
        And I check that the source has been created from the test file
        And I check that the dataset has been created from the test file
        And I check that the batch centroid prediction has been created
        And I check that the centroids are ready
        Then the local centroids file is like "<predictions_file>"

        Examples:
        | data               | test                    | fields_map | output                        |predictions_file           |
        | ../data/grades.csv | ../data/grades_perm.csv | ../data/grades_fields_map_perm.csv | ./scenario_cb_1_r/centroids.csv | ./check_files/centroids_grades.csv |
