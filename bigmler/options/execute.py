# -*- coding: utf-8 -*-
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


"""Options for BigMLer execute option

"""

def get_execute_options(defaults=None):
    """Execute-related options

    """

    if defaults is None:
        defaults = {}
    options = {

        # A BigML script is provided
        '--script': {
            "action": 'store',
            "dest": 'script',
            "default": defaults.get('script', None),
            "help": "BigML script Id."},

        # A BigML json file containing a script structure
        '--script-file': {
            'action': 'store',
            'dest': 'script_file',
            'default': defaults.get('script_file', None),
            'help': "BigML script JSON structure file."},

        # The path to a file containing script ids.
        '--scripts': {
            'action': 'store',
            'dest': 'scripts',
            'default': defaults.get('scripts', None),
            'help': ("Path to a file containing script/ids. Just"
                     " one script per line"
                     " (e.g., script/50a20697035d0706da0004a4).")},

        # A BigML library is provided
        '--library': {
            "action": 'store',
            "dest": 'library',
            "default": defaults.get('library', None),
            "help": "BigML library Id."},

        # A BigML json file containing a library structure
        '--library-file': {
            'action': 'store',
            'dest': 'library_file',
            'default': defaults.get('library_file', None),
            'help': "BigML library JSON structure file."},

        # The path to a file containing library ids.
        '--libraries': {
            'action': 'store',
            'dest': 'libraries',
            'default': defaults.get('libraries', None),
            'help': ("Path to a file containing libraries/ids. Just"
                     " one library per line"
                     " (e.g., library/50a20697035d0706da0004a4).")},

        # A BigML execution is provided
        '--execution': {
            "action": 'store',
            "dest": 'execution',
            "default": defaults.get('execution', None),
            "help": "BigML execution Id."},

        # A BigML json file containing a execution structure
        '--execution-file': {
            'action': 'store',
            'dest': 'execution_file',
            'default': defaults.get('execution_file', None),
            'help': "BigML execution JSON structure file."},

        # The path to a file containing execution ids.
        '--executions': {
            'action': 'store',
            'dest': 'executions',
            'default': defaults.get('executions', None),
            'help': ("Path to a file containing execution/ids. Just"
                     " one execution per line"
                     " (e.g., execution/50a20697035d0706da0004a4).")},

        # Path to the file that contains Whizzml source code
        '--code-file': {
            "action": 'store',
            'dest': 'code_file',
            'default': defaults.get('code_file', None),
            'help': ("Path to the file that contains Whizzml source code.")},

        # Path to the file that contains Whizzml source code
        '--code': {
            "action": 'store',
            'dest': 'code',
            'default': defaults.get('code', None),
            'help': ("String of Whizzml source code.")},

        # Name of the file to output the code.
        "--output": {
            'action': 'store',
            'dest': 'output',
            'default': defaults.get('output', None),
            'help': "Path to the file to output the execution results."},

        # Comma-separated list of libraries IDs to be included as imports
        # in scripts or other libraries.
        "--imports": {
            'action': 'store',
            'dest': 'imports',
            'default': defaults.get('imports', None),
            'help': ("Comma-separated list of libraries IDs to be"
                     " included as imports in scripts or other libraries.")},

        # Path to the JSON file with the description of the script parameters.
        "--parameters": {
            'action': 'store',
            'dest': 'parameters',
            'default': defaults.get('parameters', None),
            'help': ("Path to the JSON file with the description of "
                     "the script parameters")},

        # Path to the JSON file with the creation defaults for
        # the script parameters.
        "--creation-defaults": {
            'action': 'store',
            'dest': 'creation_defaults',
            'default': defaults.get('creation_defaults', None),
            'help': ("Path to the JSON file with the creation defaults for "
                     "the script parameters")},

        # Arguments for the script execution.
        "--arguments": {
            'action': 'store',
            'dest': 'arguments',
            'default': defaults.get('arguments', None),
            'help': "Arguments for the script execution."}
    }

    return options
