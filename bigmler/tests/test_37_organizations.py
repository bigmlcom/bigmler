# -*- coding: utf-8 -*-
#!/usr/bin/env python
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#
# Copyright 2017-2024 BigML
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


""" Bigmler retrain

"""
import os

from bigml.api import BigML

from bigmler.tests.world import (world, show_method)


import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.project_creation_steps as test_project


try:
    BIGML_ORGANIZATION = os.environ['BIGML_ORGANIZATION']
except KeyError:
    raise ValueError("You need to set BIGML_ORGANIZATION"
                     " to an organization ID in your "
                     "environment variables to run this test.")


def setup_module():
    """Setup for the module

    """
    world.bck_api = world.api
    world.api = BigML(world.username, world.api_key, debug=world.debug,
                      organization=BIGML_ORGANIZATION)
    print(world.api.connection_info())
    world.bck_project_id = world.project_id
    world.project_id = None
    world.clear()


def teardown_module():
    """Teardown for the module

    """

    if not world.debug:
        world.api = BigML(world.username, world.api_key, debug=world.debug,
                          organization=BIGML_ORGANIZATION)
        world.project_id = world.project["resource"]
        world.api.delete_project(world.project_id)
    world.project_id = world.bck_project_id
    world.api = world.bck_api
    print(world.api.connection_info())


class TestProjectOrg:
    """Testing Projects in Organizations"""

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
        Scenario: Successfully creating a project and associating resources to it:
            Given I create a BigML project in an organization named "<project>" storing results in "<output_dir>"
            And I create a BigML source uploading train "<data>" file and associate it to the organization project storing results in "<output_dir>"
            And I check that the project has been created
            And I check that the source has been created
            Then the source is associated to the project

            Examples:
            | data             | project         | output_dir
            | ../data/iris.csv | My new project  | ./scenario_org_1
        """
        print(self.test_scenario1.__doc__)
        headers = ["data", "project", "output_dir"]
        examples = [
            ['data/iris.csv', 'My new project', 'scenario_org_1']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            test_project.i_create_project_in_org(
                self, name=example["project"],
                output_dir=example["output_dir"],
                organization=BIGML_ORGANIZATION)
            test_project.i_check_create_project(self, organization=True)
            test_project.i_create_source_with_org_project(
                self, data=example["data"], output_dir=example["output_dir"])
            test_pred.i_check_create_source(self)
            test_project.check_source_in_project(self)
