Feature: Delete resources filtered by user criteria
    In order to delete resources
    I need create resources first
    Then I need to use the delete subcommand

    Scenario: Successfully deleting a source by id:
        Given I create a BigML source from file "<data>" storing results in "<output_dir>"
        And I check that the source exists
        And I delete the source by id using --ids storing results in "<output_dir>"
        Then I check that the source doesn't exist

        Examples:
        | data               | output_dir       |
        | ../data/iris.csv   | ./scenario_del_1 |

    Scenario: Failing deleting a source by id when --dry-run is used:
        Given I create a BigML source from file "<data>" storing results in "<output_dir>"
        And I check that the source has been created
        And I delete the source by id using --ids and --dry-run storing results in "<output_dir>"
        Then I check that the source exists

        Examples:
        | data               | output_dir       |
        | ../data/iris.csv   | ./scenario_del_2 |

    Scenario: Failing deleting a source by id when a different resource_types is used:
        Given I create a BigML source from file "<data>" storing results in "<output_dir>"
        And I check that the source has been created
        And I delete the source by id using --ids and --resource-types "<resource_types>" storing results in "<output_dir>"
        Then I check that the source exists

        Examples:
        | data               | output_dir       | resource_types
        | ../data/iris.csv   | ./scenario_del_3 | dataset,model

    Scenario: Successfully deleting a source from a file:
        Given I create a BigML source from file "<data>" storing results in "<output_dir>"
        And I check that the source exists
        And I delete the source by id using --from-file and the source file storing results in "<output_dir>"
        Then I check that the source doesn't exist

        Examples:
        | data               | output_dir       |
        | ../data/iris.csv   | ./scenario_del_4 |

    Scenario: Failing deleting a source from a file when a different resource_types is used:
        Given I create a BigML source from file "<data>" storing results in "<output_dir>"
        And I check that the source has been created
        And I delete the source by id using --from-file, the source file and --resource-types "<resource_types>" storing results in "<output_dir>"
        Then I check that the source exists

        Examples:
        | data               | output_dir       | resource_types
        | ../data/iris.csv   | ./scenario_del_5 | dataset,model


    Scenario: Sucessfully deleting a source in a time range:
        Given I create a BigML source from file "<data>" storing results in "<output_dir>"
        And I check that the source has been created
        And I store the source id as lower
        And I create a BigML source from file "<data>" storing results in "<output_dir>"
        And I check that the source exists
        And I store the source id as reference
        And I create a BigML source from file "<data>" storing results in "<output_dir>"
        And I check that the source has been created
        And I store the source id as upper
        And I delete the source using --older-than and --newer-than storing results in "<output_dir>"
        Then I check that the reference source doesn't exist

        Examples:
        | data               | output_dir       
        | ../data/iris.csv   | ./scenario_del_6 


    Scenario: Failing deleting a source in a time range when a different resource_types is used:
        Given I create a BigML source from file "<data>" storing results in "<output_dir>"
        And I check that the source has been created
        And I store the source id as lower
        And I create a BigML source from file "<data>" storing results in "<output_dir>"
        And I check that the source has been created
        And I store the source id as reference
        And I create a BigML source from file "<data>" storing results in "<output_dir>"
        And I check that the source has been created
        And I store the source id as upper
        And I delete the source using --older-than and --newer-than with resource_types "<resource_types>" storing results in "<output_dir>"
        Then I check that the reference source exists

        Examples:
        | data               | output_dir       | resource_types
        | ../data/iris.csv   | ./scenario_del_7 | dataset,model 


    Scenario: Sucessfully deleting a source in a time range and with a tag:
        Given I create a BigML source from file "<data>" storing results in "<output_dir>"
        And I check that the source has been created
        And I store the source id as lower
        And I create a BigML source from file "<data>" with tag "<tag1>" storing results in "<output_dir>"
        And I check that the source exists
        And I store the source id as reference
        And I create a BigML source from file "<data>" with tag "<tag2>" storing results in "<output_dir>"
        And I check that the source has been created
        And I store the source id as upper
        And I delete the source using --newer-than and --source-tag "<tag1>" storing results in "<output_dir>"
        Then I check that the reference source doesn't exist
        And I check that the upper source exists

        Examples:
        | data               | output_dir       | tag1    | tag2
        | ../data/iris.csv   | ./scenario_del_8 | my_tag1 | my_tag2


    Scenario: Sucessfully deleting resources in a time range and with a tag:
        Given I create a BigML source from file "<data>" storing results in "<output_dir>"
        And I check that the source has been created
        And I store the source id as lower
        And I create a BigML source from file "<data>" with tag "<tag1>" storing results in "<output_dir>"
        And I check that the source exists
        And I create a BigML dataset from the source with tag "<tag1>" storing results in "<output_dir>"
        And I check that the dataset exists
        And I delete the resources using --newer-than and --all-tag "<tag1>" storing results in "<output_dir>"
        Then I check that the source doesn't exist
        And I check that the dataset doesn't exist

        Examples:
        | data               | output_dir       | tag1    
        | ../data/iris.csv   | ./scenario_del_9 | my_tag1
