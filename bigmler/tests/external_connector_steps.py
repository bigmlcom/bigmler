# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
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


import os

from bigml.api import check_resource

from bigmler.tests.common_steps import shell_execute
from bigmler.tests.world import world, ok_, eq_


def i_create_external_connector(step, name=None, source=None, host=None,
                                port=None, database=None, user=None,
                                password=None ,output_dir=None):
    """Step: I create BigML external connection using <name>, <source>, <host>,
    <port>, database, user and password and log files in <output_dir>
    """
    ok_(name is not None and source is not None and host is not None and
        port is not None and database is not None and user is not None and
        password is not None and output_dir is not None)
    command = ("bigmler connector --name \"" + name +
               "\" --host " + host +
               " --port " + port +
               " --database " +  database +
               " --user " + user +
               " --password " + password +
               " --engine " + source +
               " --store --output-dir " + output_dir)
    shell_execute(command, "%s/x" % output_dir)


def i_check_external_connector(step):
    """Step: I check that the external connection is ready"""
    connector_file = os.path.join(world.directory, "external_connector")
    try:
        with open(connector_file) as handler:
            connector = check_resource(handler.readline().strip(),
                                       world.api.get_external_connector)
            world.external_connectors.append(connector['resource'])
            world.external_connector = connector
    except Exception as exc:
        ok_(False, msg=str(exc))


def i_update_external_connector(step, name=None, output_dir=None):
    """Step: I update the external connection to <name> and logs to
    <output_dir>
    """
    ok_(name is not None and output_dir is not None)
    command = ("bigmler connector --external-connector " +
               world.external_connector["resource"] +
               " --name \"" + name + "\"" + " --output-dir " + output_dir)
    shell_execute(command, "%s/x" % output_dir)


def i_check_external_connector_name(step, name=None):
    """Step: I check that the external connection is ready"""
    ec_name = world.external_connector.get( \
        "object", world.external_connector).get("name")
    eq_(ec_name, name)
