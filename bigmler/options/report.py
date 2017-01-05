# -*- coding: utf-8 -*-
#
# Copyright 2015-2017 BigML
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


"""Options for BigMLer report option

"""
DEFAULT_PORT = 8085

def get_report_options(defaults=None):
    """Report-related options

    """

    if defaults is None:
        defaults = {}
    options = {

        # Retrieves the information from the resources in the directory.
        '--from-dir': {
            'dest': 'from_dir',
            'default': defaults.get('from_dir', None),
            'help': ("Retrieves the information from the"
                     " resources in the directory.")},

        # Uses the user-given port to start a local HTTP server
        '--port': {
            'dest': 'port',
            'type': int,
            'default': defaults.get('port', DEFAULT_PORT),
            'help': ("Port where the local HTTP server is bound.")},

        # Not starting the local HTTP server. Only generates the report files.
        '--no-server': {
            'dest': 'no_server',
            'action': 'store_true',
            'default': defaults.get('no_server', False),
            'help': ("Not starting the HTTP server. Only generates"
                     " the report files.")},

        # Starting the local HTTP server, as opposed to --no-server
        '--server': {
            'dest': 'no_server',
            'action': 'store_false',
            'default': defaults.get('no_server', False),
            'help': ("Sarting the HTTP server to view the report files.")}
        }

    return options
