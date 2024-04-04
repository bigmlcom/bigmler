# -*- coding: utf-8 -*-
#!/usr/bin/env python
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#
# Copyright 2015-2024 BigML
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


""" Testing delete subcommand

"""
from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)


import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.delete_subcommand_steps as test_delete


def setup_module():
    """Setup for the module

    """
    common_setup_module()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestDelete:
    """Testing delete command """

    def setup_method(self, method):
        """
            Debug information
        """
        self.bigml = {}
        self.bigml["method"] = method.__name__
        print("\n-------------------\nTests in: %s\n" % __name__)

    def teardown_method(self):
        """Calling generic teardown for every method

        """
        world.clear_paths()
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)
        self.bigml = {}

    def test_scenario1(self):
        """
        Scenario: Successfully deleting a source by id:
            Given I create a BigML source from file "<data>" storing results in "<output_dir>"
            And I check that the source exists
            And I delete the source by id using --ids storing results in "<output_dir>"
            Then I check that the source doesn't exist
        """
        print(self.test_scenario1.__doc__)
        headers = ["data", "output_dir"]
        examples = [
            ['data/iris.csv', 'scenario_del_1']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_delete.i_create_source_from_file(
                self, data=example["data"], output_dir=example["output_dir"])
            test_delete.i_check_source_exists(self)
            test_delete.i_delete_source_by_ids(
                self, output_dir=example["output_dir"])
            test_delete.i_check_source_does_not_exist(
                self, source_id=None)

    def test_scenario2(self):
        """
        Scenario: Failing deleting a source by id when --dry-run is used:
            Given I create a BigML source from file "<data>" storing results in "<output_dir>"
            And I check that the source has been created
            And I delete the source by id using --ids and --dry-run storing results in "<output_dir>"
            Then I check that the source exists
        """
        print(self.test_scenario2.__doc__)
        headers = ["data", "output_dir"]
        examples = [
            ['data/iris.csv', 'scenario_del_2']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_delete.i_create_source_from_file(
                self, data=example["data"], output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_delete.i_delete_source_by_ids_dry(
                self, output_dir=example["output_dir"])
            test_delete.i_check_source_exists(self)

    def test_scenario3(self):
        """
        Scenario: Failing deleting a source by id when a different resource_types is used:
            Given I create a BigML source from file "<data>" storing results in "<output_dir>"
            And I check that the source has been created
            And I delete the source by id using --ids and --resource-types "<resource_types>" storing results in "<output_dir>"
            Then I check that the source exists
        """
        print(self.test_scenario3.__doc__)
        headers = ["data", "output_dir", "resource_types"]
        examples = [
            ['data/iris.csv', 'scenario_del_3', 'dataset,model']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_delete.i_create_source_from_file(
                self, data=example["data"], output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_delete.i_delete_source_by_ids_filtered(
                self, resource_types=example["resource_types"],
                output_dir=example["output_dir"])
            test_delete.i_check_source_exists(self)

    def test_scenario4(self):
        """
        Scenario: Successfully deleting a source from a file:
            Given I create a BigML source from file "<data>" storing results in "<output_dir>"
            And I check that the source exists
            And I delete the source by id using --from-file and the source file storing results in "<output_dir>"
            Then I check that the source doesn't exist
        """
        print(self.test_scenario4.__doc__)
        headers = ["data", "output_dir"]
        examples = [
            ['data/iris.csv', 'scenario_del_4']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_delete.i_create_source_from_file(
                self, data=example["data"], output_dir=example["output_dir"])
            test_delete.i_check_source_exists(self)
            test_delete.i_delete_source_by_file(
                self, output_dir=example["output_dir"])
            test_delete.i_check_source_does_not_exist(self, source_id=None)

    def test_scenario5(self):
        """
            Scenario: Failing deleting a source from a file when a different resource_types is used:
                Given I create a BigML source from file "<data>" storing results in "<output_dir>"
                And I check that the source has been created
                And I delete the source by id using --from-file, the source file and --resource-types "<resource_types>" storing results in "<output_dir>"
                Then I check that the source exists
        """
        print(self.test_scenario5.__doc__)
        headers = ["data", "output_dir", "resource_types"]
        examples = [
            ['data/iris.csv', 'scenario_del_5', 'dataset,model']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_delete.i_create_source_from_file(
                self, data=example["data"], output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_delete.i_delete_source_by_file_filtered(
                self, resource_types=example["resource_types"],
                output_dir=example["output_dir"])
            test_delete.i_check_source_exists(self)

    def test_scenario6(self):
        """
            Scenario: Sucessfully deleting a source in a time range:
                Given I create a BigML source from file "<data>" storing results in "<output_dir>"
                And I check that the source has been created
                And I store the source id as lower
                And I create a BigML source from file "<data>" storing results in "<output_dir2>"
                And I check that the source exists
                And I store the source id as reference
                And I create a BigML source from file "<data>" storing results in "<output_dir3>"
                And I check that the source has been created
                And I store the source id as upper
                And I delete the source using --older-than and --newer-than storing results in "<output_dir>"
                Then I check that the reference source doesn't exist
        """
        print(self.test_scenario6.__doc__)
        headers = ["data", "output_dir", "output_dir2", "output_dir3"]
        examples = [
            ['data/iris.csv', 'scenario_del_6', 'scenario_del_6_2',
             'scenario_del_6_3']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_delete.i_create_source_from_file(
                self, data=example["data"], output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            self.bigml["source_lower"] = world.source["resource"]
            test_delete.i_create_source_from_file(
                self, data=example["data"], output_dir=example["output_dir2"])
            test_delete.i_check_source_exists(self)
            self.bigml["source_reference"] = world.source["resource"]
            test_delete.i_create_source_from_file(
                self, data=example["data"], output_dir=example["output_dir3"])
            test_pred.i_check_create_source(self)
            self.bigml["source_upper"] = world.source["resource"]
            test_delete.i_delete_source_older_newer(
                self, output_dir=example["output_dir3"])
            test_delete.i_check_source_does_not_exist(
                self, source_id=self.bigml["source_reference"])

    def test_scenario7(self):
        """
        Scenario: Failing deleting a source in a time range when a different resource_types is used:
            Given I create a BigML source from file "<data>" storing results in "<output_dir>"
            And I check that the source has been created
            And I store the source id as lower
            And I create a BigML source from file "<data>" storing results in "<output_dir2>"
            And I check that the source has been created
            And I store the source id as reference
            And I create a BigML source from file "<data>" storing results in "<output_dir3>"
            And I check that the source has been created
            And I store the source id as upper
            And I delete the source using --older-than and --newer-than with resource_types "<resource_types>" storing results in "<output_dir>"
            Then I check that the reference source exists
        """
        print(self.test_scenario7.__doc__)
        headers = ["data", "output_dir", "resource_types", "output_dir2",
                   "output_dir3"]
        examples = [
            ['data/iris.csv', 'scenario_del_7', 'dataset,model',
             'scenario_del_7_2', 'scenario_del_7_3']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_delete.i_create_source_from_file(
                self, data=example["data"], output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            self.bigml["source_lower"] = world.source["resource"]
            test_delete.i_create_source_from_file(
                self, data=example["data"], output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            self.bigml["source_reference"] = world.source["resource"]
            test_delete.i_create_source_from_file(
                self, data=example["data"], output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            self.bigml["source_upper"] = world.source["resource"]
            test_delete.i_delete_source_older_newer_with_resource_types(
                self, resource_types=example["resource_types"],
                output_dir=example["output_dir"])
            test_delete.i_check_source_exists_by_id(
                self, source_id=self.bigml["source_reference"])

    def test_scenario8(self):
        """
        Scenario: Sucessfully deleting a source in a time range and with a tag:
            Given I create a BigML source from file "<data>" storing results in "<output_dir>"
            And I check that the source has been created
            And I store the source id as lower
            And I create a BigML source from file "<data>" with tag "<tag1>" storing results in "<output_dir>"
            And I check that the source exists
            And I store the source id as reference
            And I create a BigML source from file "<data>" with tag "<tag2>" storing results in "<output_dir2>"
            And I check that the source has been created
            And I store the source id as upper
            And I delete the source using --newer-than and --source-tag "<tag1>" storing results in "<output_dir3>"
            Then I check that the reference source doesn't exist
            And I check that the upper source exists
        """
        print(self.test_scenario8.__doc__)
        headers = ["data", "output_dir", "tag1", "tag2", "output_dir2",
                   "output_dir3"]
        examples = [
            ['data/iris.csv', 'scenario_del_8', 'my_tag1', 'my_tag2',
             'scenario_del_8_2', 'scenario_del_8_3']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_delete.i_create_source_from_file(
                self, data=example["data"], output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            self.bigml["source_lower"] = world.source["resource"]
            test_delete.i_create_source_from_file_with_tag(
                self, data=example["data"], tag=example["tag1"],
                output_dir=example["output_dir"])
            test_delete.i_check_source_exists(self)
            self.bigml["source_reference"] = world.source["resource"]
            test_delete.i_create_source_from_file_with_tag(
                self, data=example["data"], tag=example["tag2"],
                output_dir=example["output_dir"])
            test_delete.i_check_source_exists(self)
            self.bigml["source_upper"] = world.source["resource"]
            test_delete.i_delete_source_newer_and_tag(
                self, tag=example["tag1"], output_dir=example["output_dir"])
            test_delete.i_check_source_does_not_exist(
                self, source_id=self.bigml["source_reference"])
            test_delete.i_check_source_exists_by_id(
                self, source_id=self.bigml["source_upper"])

    def test_scenario9(self):
        """
        Scenario: Sucessfully deleting resources in a time range and with a tag:
            Given I create a BigML source from file "<data>" storing results in "<output_dir>"
            And I check that the source has been created
            And I store the source id as lower
            And I create a BigML source from file "<data>" with tag "<tag>" storing results in "<output_dir>"
            And I check that the source exists
            And I create a BigML dataset from the source with tag "<tag>" storing results in "<output_dir2>"
            And I check that the dataset exists
            And I delete the resources using --newer-than and --all-tag "<tag>" storing results in "<output_dir3>"
            Then I check that the source doesn't exist
            And I check that the dataset doesn't exist
        """
        print(self.test_scenario9.__doc__)
        headers = ["data", "output_dir", "tag", "output_dir2", "output_dir3"]
        examples = [
            ['data/iris.csv', 'scenario_del_9', 'my_tag1', 'scenario_del_9_2',
             'scenario_del_9_3']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_delete.i_create_source_from_file(
                self, data=example["data"], output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            self.bigml["source_lower"] = world.source["resource"]
            test_delete.i_create_source_from_file_with_tag(
                self, data=example["data"], tag=example["tag"],
                output_dir=example["output_dir"])
            test_delete.i_check_source_exists(self)
            self.bigml["source_reference"] = world.source["resource"]
            test_delete.i_create_dataset_from_source_with_tag(
                self, tag=example["tag"], output_dir=example["output_dir"])
            test_delete.i_check_dataset_exists(self)
            test_delete.i_delete_resources_newer_and_tag(
                self, tag=example["tag"], output_dir=example["output_dir"])
            test_delete.i_check_source_does_not_exist(
                self, source_id=self.bigml["source_reference"])
            test_delete.i_check_dataset_does_not_exist(
                self, dataset_id=world.dataset)
            test_delete.i_check_source_exists_by_id(
                self, source_id=self.bigml["source_lower"])

    def test_scenario10(self):
        """
        Scenario: Sucessfully deleting a source in a time range and with a tag and status faulty:
            Given I create a BigML source from file "<data>" storing results in "<output_dir>"
            And I check that the source has been created
            And I store the source id as lower
            And I create a BigML source from file "<data>" storing results in "<output_dir>"
            And I check that the source exists
            And I store the source id as reference
            And I create a BigML source from file "<data2>" with tag "<tag2>" storing results in "<output_dir2>"
            And I check that the failed source exists
            And I delete the source using --newer-than and --source-tag "<tag2>" and --status faulty storing results in "<output_dir3>"
            Then I check that the reference source doesn't exist
            And I check that the upper source exists
        """
        print(self.test_scenario10.__doc__)
        headers = ["data", "output_dir", "tag2",
                   "output_dir2", "output_dir3", "data2"]
        examples = [
            ['data/iris.csv', 'scenario_del_10', 'my_tag2',
             'scenario_del_10_2', 'scenario_del_10_3', 'data/faulty.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_delete.i_create_source_from_file(
                self, data=example["data"], output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            self.bigml["source_lower"] = world.source["resource"]
            test_delete.i_create_faulty_source_from_file_with_tag(
                self, data=example["data2"], tag=example["tag2"],
                output_dir=example["output_dir2"])
            test_delete.i_check_faulty_source_exists(self)
            self.bigml["source_reference"] = world.source["resource"]
            test_delete.i_delete_source_newer_faulty_and_tag(
                self, tag=example["tag2"], output_dir=example["output_dir3"])
            test_delete.i_check_source_does_not_exist(
                self, source_id=self.bigml["source_reference"])
            test_delete.i_check_source_exists_by_id(
                self, source_id=self.bigml["source_lower"])

    def test_scenario11(self):
        """
        Scenario: Successfully deleting a project:
            Given I create a BigML project with name "<name>" storing results in "<output_dir>"
            And I check that the project exists
            And I delete the project by name storing results in "<output_dir>"
            Then I check that the project doesn't exist

            Examples:
            | name               | output_dir       |
            | my_trash_project   | ./scenario_del_11 |
        """
        print(self.test_scenario11.__doc__)
        headers = ["name", "output_dir"]
        examples = [
            ['my_trash_project', 'scenario_del_11']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_delete.i_create_project(
                self, name=example["name"], output_dir=example["output_dir"])
            test_delete.i_check_project_exists(self)
            test_delete.i_delete_project_by_name(self, name=example["name"],
                output_dir=example["output_dir"])
            test_delete.i_check_project_does_not_exist(self)
