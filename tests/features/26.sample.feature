Feature: Create a sample resource from a dataset
    In order to create a new sample
    I need to create one origin datasets
    Then I need to generate the new sample from a dataset

    Scenario: Successfully building a new sample from a dataset
        Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
        And I check that the source has been created
        And I check that the dataset has been created
        Then I create a new sample from the dataset and get the sample using options "<sample_options>" storing logs in "<output_dir>"
        And I check that the sample has been created
        And the sample file is like "<sample_CSV>"

        Examples:
        |data |output_dir  |sample_options | sample_CSV
        |../data/iris.csv | ./scenario_smp_1 | --occurrence --sample-header --row-index | ./check_files/sample_iris.csv
        |../data/iris.csv | ./scenario_smp_2 | --precision 0 --rows 10 --row-offset 10 --unique | ./check_files/sample_iris2.csv
        |../data/iris.csv | ./scenario_smp_3 | --row-order-by="-petal length" --row-fields "petal length,petal width" --mode linear | ./check_files/sample_iris3.csv

    Scenario: Successfully building a new sample from a dataset
        Given I create a BigML dataset from "<data>" and store logs in "<output_dir>"
        And I check that the source has been created
        And I check that the dataset has been created
        Then I create a new sample from the dataset and get the sample using options "<sample_options>" storing logs in "<output_dir>"
        And I check that the sample has been created
        And the sample contains stat-info like in "<sample_JSON>"

        Examples:
        |data |output_dir  |sample_options | sample_JSON
        |../data/iris.csv | ./scenario_smp_4 | --stat-field "petal length"| ./check_files/stat_info.json
