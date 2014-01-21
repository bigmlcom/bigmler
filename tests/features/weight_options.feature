Feature: Create a model using weight options
    In order to create a weighted model
    I need to create a dataset
    Then I need to generate a model from it using different weights

    Scenario: Successfully building a balanced model
        Given I create a BigML balanced model from "<data>" and store logs in "<output_dir>"
        And I check that the source has been created
        And I check that the dataset has been created
        And I check that the model has been created
        Then I check that the model is balanced

        Examples:
        |data |output_dir  |
        |../data/iris.csv | ./scenario_w_1 |

    Scenario: Successfully building a field weighted model
        Given I create a BigML field weighted model from "<data>" using field "<field>" as weight and store logs in "<output_dir>"
        And I check that the source has been created
        And I check that the dataset has been created
        And I check that the model has been created
        Then I check that the model uses as weight "<field_id>"

        Examples:
        |data |field | output_dir  | field_id
        |../data/iris_w.csv | weight |./scenario_w_2 | 000005
