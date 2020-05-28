# -*- coding: utf-8 -*-
#
# Copyright 2020 BigML
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


"""Options for BigMLer external connector processing

"""

def get_external_connector_options(defaults=None):
    """external connector-related options

    """

    if defaults is None:
        defaults = {}

    options = {
        # The path to a file containing external connector attributes.
        '--connector-attributes': {
            'action': 'store',
            'dest': 'connector_attributes',
            'default': defaults.get('connector_attributes', None),
            'help': ("Path to a json file describing connector"
                     " attributes.")},

        # The ID of an existing connector.
        '--external-connector-id': {
            'action': 'store',
            'dest': 'external_connector_id',
            'default': defaults.get('external_connector_id', None),
            'help': ("ID of an existing external connector.")},

        # The kind of database manager
        '--engine': {
            'action': 'store',
            'dest': 'source',
            'default': defaults.get('source', None),
            'choices': ["mysql", "postgresql", "elasticsearch", "sqlserver"],
            'help': ("Database manager engine.")},

        # The host where the database manager is
        '--host': {
            'action': 'store',
            'dest': 'host',
            'default': defaults.get('host', None),
            'help': ("Name of the database manager host.")},

        # The list of hosts for Elasticsearch
        '--hosts': {
            'action': 'store',
            'dest': 'hosts',
            'default': defaults.get('hosts', None),
            'help': ("Comma-separated list of hosts (elasticsearch only).")},

        # The port that the database listens to
        '--port': {
            'action': 'store',
            'dest': 'port',
            'default': defaults.get('port', None),
            'help': ("Port number to connect to.")},

        # The database name
        '--database': {
            'action': 'store',
            'dest': 'database',
            'default': defaults.get('database', None),
            'help': ("Name of the database.")},

        # The username
        '--user': {
            'action': 'store',
            'dest': 'user',
            'default': defaults.get('user', None),
            'help': ("Database user name.")},

        # The password
        '--password': {
            'action': 'store',
            'dest': 'password',
            'default': defaults.get('password', None),
            'help': ("Database user password.")},

        # JSON file containing the connection info
        '--connection-json': {
            'action': 'store',
            'dest': 'connection_json',
            'default': defaults.get('connection_json', None),
            'help': ("JSON file describing the connection arguments.")}

    }

    return options
