Feature: Delete resources filtered by user criteria
    In order to delete resources
    I need create resources first
    Then I need to use the delete subcommand


    Scenario: Sucessfully deleting resources from a directory:
        Given I create BigML resources uploading train "<data>" storing results in "<output_dir>"
        And I check that the number of resources has changed
        And I delete the resources from the output directory
        Then the number of resources has not changed

        Examples:
        | data               | output_dir        
        | ../data/iris.csv   | ./scenario_del_10 
