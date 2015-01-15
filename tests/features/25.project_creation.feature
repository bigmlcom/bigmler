Feature: Create projects and associate resources with them
    In order to produce a resource in a project
    I need to create the project
    Then I need to create the original source for the resource and associate it with the project


    Scenario: Successfully creating a project and associating resources to it:
        Given I create a BigML source uploading train "<data>" file and associate it to a new project named "<project>" storing results in "<output_dir>"
        And I check that the project has been created
        And I check that the source has been created
        Then the source is associated to the project

        Examples:
        | data             | project         | output_dir
        | ../data/iris.csv | My new project  | ./scenario_p_1

    Scenario: Successfully associating resources to an existing project:
        Given I create a BigML source uploading train "<data>" file and associate it to a new project named "<project>" storing results in "<output_dir>"
        And I check that the project has been created
        And I check that the source has been created
        And I create a BigML source uploading train "<data>" file and associate it to the last created project id storing results in "<output_dir2>"
        Then the source is associated to the project

        Examples:
        | data             | project         | output_dir     | output_dir2
        | ../data/iris.csv | My new project  | ./scenario_p_2 | ./scenario_p_2_1

    Scenario: Successfully creating resources with no project association:
        Given I create a BigML source from file "<data>" storing results in "<output_dir>"
        And I check that the source has been created
        Then the source has no project association

        Examples:
        | data             | output_dir
        | ../data/iris.csv | ./scenario_p_3
