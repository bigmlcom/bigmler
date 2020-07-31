# -*- coding: utf-8 -*-
#
# Copyright 2014-2020 BigML
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
"""Common options for the BigMLer parser

"""


import datetime

def get_common_options(defaults=None, constants=None):
    """Common options used in all subcommands

    """

    if defaults is None:
        defaults = {}
    if constants is None:
        constants = {}
    now = constants.get('NOW',
                        datetime.datetime.now().strftime("%a%b%d%y_%H%M%S"))
    version_text = constants['version_text']
    defaults_tag = defaults.get('tag')
    defaults_tag = [] if defaults_tag is None else defaults_tag.split(",")
    options = {
        # Shows log info for each https request.
        '--debug': {
            "action": 'store_true',
            "default": defaults.get('debug', False),
            "help": "Activate debug level"},

        # BigML's username.
        '--username': {
            "action": 'store',
            "default": defaults.get('username', None),
            "help": "BigML's username."},

        # BigML's API key.
        '--api-key': {
            "action": 'store',
            "dest": 'api_key',
            "default": defaults.get('api_key', None),
            "help": "BigML's API key."},

        # Id of the project in an organization to be used in resource creation
        '--org-project': {
            'action': 'store',
            'dest': 'org_project',
            'default': defaults.get('org_project', None),
            'help': ("Id of the project in an organization to be used in"
                     "resource creation.")},

        # Log file to store resources ids.
        '--resources-log': {
            "action": 'store',
            "dest": 'log_file',
            "default": defaults.get('resources_log', None),
            "help": ("Path to a file to store new resources"
                     " ids. One resource per line"
                     " (e.g., model/50a206a8035d0706dc000376"
                     ").")},

        # Stores the retrieved resources in the output directory
        '--store': {
            "action": 'store_true',
            "dest": 'store',
            "default": defaults.get('store', False),
            "help": ("Store the retrieved resources in the"
                     " output directory.")},

        # Clear global bigmler log files
        '--clear-logs': {
            "action": 'store_true',
            "dest": 'clear_logs',
            "default": defaults.get('clear_logs', False),
            "help": "Clear global bigmler log files."},

        # Use it to add a tag to the new resources created.
        '--tag': {
            "action": 'append',
            "default": defaults_tag,
            "help": "Tag to later retrieve new resources."},

        # Avoid default tagging of resources.
        '--no-tag': {
            "action": 'store_false',
            "dest": 'no_tag',
            "default": defaults.get('no_tag', True),
            "help": "No tag resources with default BigMLer tags."},

        # Hides log info for each https request.
        '--no-debug': {
            "action": 'store_false',
            "dest": 'debug',
            "default": defaults.get('debug', False),
            "help": "Deactivate debug level."},

        # Turn on/off verbosity
        '--verbosity': {
            "action": 'store',
            "dest": 'verbosity',
            "default": defaults.get('verbosity', 1),
            "type": int,
            "choices": [0, 1],
            "help": "Set verbosity: 0 to turn off, 1 to turn on."},

        # Resume a partial execution
        '--resume': {
            "action": 'store_true',
            "help": "Resume command."},

        # Resume a partial execution
        '--stack-level': {
            "action": 'store',
            "dest": 'stack_level',
            "default": 0,
            "type": int,
            "help": "Resume command."},

        # Separator for multiple arguments
        '--args-separator': {
            "action": 'store',
            "dest": 'args_separator',
            "default": defaults.get('args_separator', ","),
            "help": ("Separator used in arguments with "
                     " multiple values.")},

        # Name to be used with the source and then with datasets, models and
        # predictions.
        '--name': {
            "action": 'store',
            "dest": 'name',
            "default": defaults.get('name', 'BigMLer_%s' % now),
            "help": "Name for the resources in BigML."},

        # Name of the directory where session files will be stored. If --output
        # is set, this setting will be overriden by it.
        '--output-dir': {
            'action': 'store',
            'dest': 'output_dir',
            'default': defaults.get('output_dir', None),
            'help': ("Directory where session files will be stored."
                     " --output file path will override it if both"
                     " are set.")},

        # Shared. Shares all shareable resources and uses its shared links in
        # reports
        '--shared': {
            'action': 'store_true',
            'dest': 'shared',
            'default': defaults.get('shared', False),
            'help': ("Share resources and use its shared urls "
                     " in reports.")},

        # Category code.
        '--category': {
            'action': 'store',
            'dest': 'category',
            'default': defaults.get('category', 12),
            'type': int,
            'help': "Category code."},

        # A file including a markdown description
        '--description': {
            'action': 'store',
            'dest': 'description',
            'default': defaults.get('description', None),
            'help': ("Path to a file with a description in plain"
                     " text or markdown.")},

        # Set default tagging of resources. (opposed to --no-tag)
        '--no-no-tag': {
            'action': 'store_true',
            'dest': 'no_tag',
            'default': defaults.get('no_tag', True),
            'help': "Tag resources with default BigMLer tags."},

        # Evaluations flag: excluding one dataset from the datasets list to test
        '--version': {
            'action': 'version',
            'version': version_text}}

    return options
