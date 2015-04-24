# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015 BigML
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
from world import world, setup_module, teardown_module, teardown_class

import delete_subcommand_steps as test_delete


class TestDeleteDir(object):

    def teardown(self):
        """Calling generic teardown for every method

        """
        teardown_class()

    def setup(self):
        """No setup operations for every method at present

        """
        pass

    def test_scenario1(self):
        """
            Scenario: Sucessfully deleting resources from a directory:
                Given I create BigML resources uploading train "<data>" storing results in "<output_dir>"
                And I check that the number of resources has changed
                And I delete the resources from the output directory
                Then the number of resources has not changed

                Examples:
                | data               | output_dir
                | ../data/iris.csv   | ./scenario_del_10
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', 'scenario_del_10']]
        for example in examples:
            print "\nTesting with:\n", example
            test_delete.i_create_source_from_file(self, data=example[0], output_dir=example[1])
            test_delete.i_check_changed_number_of_resources(self)
            test_delete.i_delete_resources_from_dir(self)
            test_delete.i_check_equal_number_of_resources(self)