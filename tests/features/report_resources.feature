Feature: Create reports for generated resources in Gazibit, reveal, and impress
    In order to create reports in Gazibit
    I need to upload a train set
    Then I need to create a dataset and a model and an evaluation

    Scenario: Successfully generating reports in Gazibit, reveal, and impress:
        Given I create BigML resources and share them uploading train "<data>" file to evaluate and log evaluation and reports in "<output>"
        And I check that the source has been created
        And I check that the dataset has been created and shared
        And I check that the model has been created and shared
        Then I check that the evaluation has been created and shared
        And I check that the Gazibit private report has been created
        And I check that the Gazibit shared report has been created
        And I check that the reveal private report has been created
        And I check that the reveal shared report has been created
        And I check that the impress private report has been created
        And I check that the impress shared report has been created

        Examples:
        | data               | output                      |
        | ../data/iris.csv   | ./scenario_rpt_1/evaluation |
