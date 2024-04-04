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

""" Testing delete subcommand, --from-dir option

"""
from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)

import bigmler.tests.delete_subcommand_steps as test_delete


def setup_module():
    """Setup for the module

    """
    common_setup_module()

def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()

class TestDeleteDir:
    """Testing delete from directory"""

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
        Scenario: Sucessfully deleting resources from a directory:
            Given I store the number of existing resources
            And I create BigML resources uploading train "<data>" storing results in "<output_dir>"
            And I check that the number of resources has changed
            And I delete the resources from the output directory
            Then the number of resources has not changed

            Examples:
            | data               | output_dir
            | ../data/iris.csv   | ./scenario_del_10
        """
        print(self.test_scenario1.__doc__)
        headers = ["data", "output_dir"]
        examples = [
            ['data/iris.csv', 'scenario_del_10']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_delete.i_store_the_number_of_resources(self)
            test_delete.i_create_source_from_file(
                self, data=example["data"], output_dir=example["output_dir"])
            test_delete.i_check_changed_number_of_resources(self)
            test_delete.i_delete_resources_from_dir(self)
            test_delete.i_check_equal_number_of_resources(self)
