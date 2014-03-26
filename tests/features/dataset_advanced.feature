Feature: Create a new dataset from an old one by combining its fields or from a datasets list
    In order to create a new dataset
    I need to create one/many origin datasets
    Then I need to generate the new dataset from a new fields file or a datasets list

    Scenario: Successfully building a new dataset from an existing one
        Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
        And I check that the source has been created
        And I check that the dataset has been created
        And I create a new BigML dataset using the specs in JSON file "<new_fields>"
        And I check that the new dataset has been created
        Then I check that the new dataset has field "<field>"

        Examples:
        |data |output_dir  |new_fields | field |
        |../data/iris.csv | ./scenario_d_1 |../data/new_fields.json| outlier? |

    Scenario: Successfully updating a dataset with attributes in a JSON file
        Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
        And I check that the source has been created
        And I check that the dataset has been created
        And I update the dataset using the specs in JSON file "<new_fields>"
        Then I check that property "<property>" for field id "<field_id>" is "<value>" of type "<type>"

        Examples:
        |data |output_dir  |new_fields | property | field_id | value | type
        |../data/iris.csv | ./scenario_d_2 |../data/attributes.json| preferred | 000001 | false | boolean

    Scenario: Successfully building a multi-dataset
        Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
        And I check that the source has been created
        And I check that the dataset has been created
        And I create a BigML dataset from "<data>" and store logs in "<output_dir>"
        And I check that the source has been created
        And I check that the dataset has been created
        And I create a multi-dataset from the datasets file and store logs in "<output_dir2>"
        And I check that the multi-dataset has been created
        Then I check that the multi-dataset's origin are the datasets in "<output_dir>"

        Examples:
        |data |output_dir  |output_dir2 |
        |../data/iris.csv | ./scenario_d_3 | ./scenario_d_4|
