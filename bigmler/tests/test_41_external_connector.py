# -*- coding: utf-8 -*-
#!/usr/bin/env python
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#pylint: disable=locally-disabled,invalid-name
#
# Copyright 2020-2024 BigML
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


""" Testing fusion predictions creation

"""


import os

from bigmler.tests.world import (world, common_setup_module,
                                 common_teardown_module, show_method)


import bigmler.tests.external_connector_steps as external_connection
import bigmler.tests.basic_tst_prediction_steps as prediction_create

HOST = os.getenv("BIGML_EXTERNAL_CONN_HOST")
PORT = os.getenv("BIGML_EXTERNAL_CONN_PORT")
DATABASE = os.getenv("BIGML_EXTERNAL_CONN_DB")
USER = os.getenv("BIGML_EXTERNAL_CONN_USER")
PASSWORD = os.getenv("BIGML_EXTERNAL_CONN_PWD")

if HOST is None or PORT is None or DATABASE is None or USER is None or \
        PASSWORD is None:
    raise ValueError("The external connections tests needs defining some"
                     " environment variables: BIGML_EXTERNAL_CONN_HOST,"
                     " BIGML_EXTERNAL_CONN_PORT, BIGML_EXTERNAL_CONN_DB,"
                     " BIGML_EXTERNAL_CONN_USER, BIGML_EXTERNAL_CONN_PWD")


def setup_module():
    """Setup for the module

    """
    common_setup_module()
    TestExternalConnector()


def teardown_module():
    """Teardown for the module

    """
    common_teardown_module()


class TestExternalConnector:
    """Testing external connectors"""

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

    def test_scenario01(self):
        """
        Scenario: Successfully building an external connector
            And I create BigML external connection using  "<name>", "<source>", "<host>", "<port>", "<user>", "<password>" and "<database>" and log files in  "<output_dir>"
            And I check that the external connection is ready
            And I update the external connection to "<new_name>"
            Then the external connection has name "<new_name>"
            And I create a source from the external connector
            And I check that the source is ready

        """
        print(self.test_scenario01.__doc__)
        headers = ["name", "source", "host", "port", "user", "password",
                   "database", "output_dir", "new_name", "connector",
                   "sql_query"]
        examples = [
            ['my connection', 'postgresql', HOST,
            PORT, USER, PASSWORD, DATABASE, 'scenario_41',
            'my new connection', 'scenario_41/my_connector.json',
            'select * from iris']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            external_connection.i_create_external_connector( \
                self, name=example["name"], source=example["source"],
                host=example["host"], port=example["port"],
                user=example["user"], password=example["password"],
                database=example["database"], output_dir=example["output_dir"])
            external_connection.i_check_external_connector(self)
            external_connection.i_update_external_connector( \
                self, name=example["new_name"],
                output_dir=example["output_dir"])
            external_connection.i_check_external_connector(self)
            external_connection.i_check_external_connector_name( \
                self, example["new_name"])
            prediction_create.i_create_source_from_connector(
                self, example["connector"], example["output_dir"],
                example["sql_query"])
            prediction_create.i_check_create_source(self)
