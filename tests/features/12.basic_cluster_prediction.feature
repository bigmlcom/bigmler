Feature: Upload source and produce centroids for test data
    In order produce centroids predictions
    I need to upload a train set
    Then I need to create a dataset and a cluster and a local cluster to predict

    Scenario: Successfully building test centroids from scratch:
        Given I create BigML resources uploading train "<data>" file to create centroids for "<test>" and log predictions in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created 
        And I check that the cluster has been created
        And I check that the centroids are ready
        Then the local centroids file is like "<predictions_file>"

        Examples:
        | data               | test               | output                           |predictions_file           |
        | ../data/grades.csv | ../data/grades.csv | ./scenario_c_1_r/centroids.csv | ./check_files/centroids_grades.csv |
        | ../data/diabetes.csv   | ../data/diabetes.csv   | ./scenario_c_1/centroids.csv   | ./check_files/centroids_diabetes.csv   |



    Scenario: Successfully building test predictions from source
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML resources using source to find centroids for "<test>" and log predictions in "<output>"
        And I check that the dataset has been created 
        And I check that the cluster has been created
        And I check that the centroids are ready
        Then the local centroids file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
        | scenario_c_1| {"data": "../data/diabetes.csv", "output": "./scenario_c_1/centroids.csv", "test": "../data/diabetes.csv"}   | ../data/diabetes.csv   | ./scenario_c_2/centroids.csv   | ./check_files/centroids_diabetes.csv   |

    Scenario: Successfully building test predictions from dataset
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML resources using dataset to find centroids for "<test>" and log predictions in "<output>"
        And I check that the cluster has been created
        And I check that the centroids are ready
        Then the local centroids file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
        | scenario_c_1| {"data": "../data/diabetes.csv", "output": "./scenario_c_1/centroids.csv", "test": "../data/diabetes.csv"}   | ../data/diabetes.csv   | ./scenario_c_3/centroids.csv   | ./check_files/centroids_diabetes.csv   |

    Scenario: Successfully building test predictions from cluster
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>        
        And I create BigML resources using cluster to find centroids for "<test>" and log predictions in "<output>"
        And I check that the centroids are ready
        Then the local centroids file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
        | scenario_c_1| {"data": "../data/diabetes.csv", "output": "./scenario_c_1/centroids.csv", "test": "../data/diabetes.csv"}   | ../data/diabetes.csv   | ./scenario_c_4/centroids.csv   | ./check_files/centroids_diabetes.csv   |

    Scenario: Successfully building test predictions from clusters file
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML resources using clusters in file "<clusters_file>" to find centroids for "<test>" and log predictions in "<output>"
        And I check that the centroids are ready
        Then the local centroids file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | clusters_file        | test                  | output                      |predictions_file                    |
        | scenario_c_1| {"data": "../data/diabetes.csv", "output": "./scenario_c_1/centroids.csv", "test": "../data/diabetes.csv"}   | ./scenario_c_1/clusters | ../data/diabetes.csv | ./scenario_c_5/centroids.csv | ./check_files/centroids_diabetes.csv |

    Scenario: Successfully generating datasets from cluster centroids
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I generate datasets for "<centroid_names>" centroids and log predictions in "<output>"
        Then I check that the <datasets_number> cluster datasets are ready

        Examples:
        |scenario    | kwargs                                                  | centroid_names        | output                      | datasets_number |
        | scenario_c_1| {"data": "../data/diabetes.csv", "output": "./scenario_c_1/centroids.csv", "test": "../data/diabetes.csv"}   || Cluster 1,Cluster 2 | ./scenario_c_6/centroids.csv | 2 |
