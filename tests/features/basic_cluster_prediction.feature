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
        | ../data/iris.csv   | ../data/iris.csv   | ./scenario_c_1/centroids.csv   | ./check_files/centroids_iris.csv   |



    Scenario: Successfully building test predictions from source
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML resources using source to find centroids for "<test>" and log predictions in "<output>"
        And I check that the dataset has been created 
        And I check that the cluster has been created
        And I check that the centroids are ready
        Then the local centroids file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
        | scenario_c_1| {"data": "../data/iris.csv", "output": "./scenario_c_1/predictions.csv", "test": "../data/iris.csv"}   | ../data/iris.csv   | ./scenario_c_2/centroids.csv   | ./check_files/centroids_iris.csv   |

    Scenario: Successfully building test predictions from dataset
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML resources using dataset to find centroids for "<test>" and log predictions in "<output>"
        And I check that the cluster has been created
        And I check that the centroids are ready
        Then the local centroids file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
        | scenario_c_1| {"data": "../data/iris.csv", "output": "./scenario1/predictions.csv", "test": "../data/iris.csv"}   | ../data/iris.csv   | ./scenario_c_3/centroids.csv   | ./check_files/centroids_iris.csv   |

    Scenario: Successfully building test predictions from cluster
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>        
        And I create BigML resources using cluster to find centroids for "<test>" and log predictions in "<output>"
        And I check that the centroids are ready
        Then the local centroids file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | test                    | output                        |predictions_file           |
        | scenario_c_1| {"data": "../data/iris.csv", "output": "./scenario1/centroids.csv", "test": "../data/iris.csv"}   | ../data/iris.csv   | ./scenario_c_4/centroids.csv   | ./check_files/centroids_iris.csv   |

    Scenario: Successfully building test predictions from clusters file
        Given I have previously executed "<scenario>" or reproduce it with arguments <kwargs>
        And I create BigML resources using clusters in file "<clusters_file>" to find centroids for "<test>" and log predictions in "<output>"
        And I check that the centroids are ready
        Then the local centroids file is like "<predictions_file>"

        Examples:
        |scenario    | kwargs                                                  | clusters_file        | test                  | output                      |predictions_file                    |
        | scenario_c_1| {"data": "../data/iris.csv", "output": "./scenario_c_1/predictions.csv", "test": "../data/iris.csv"}   | ./scenario_c_1/clusters | ../data/iris.csv | ./scenario_c_5/centroids.csv | ./check_files/centroids_iris.csv |
