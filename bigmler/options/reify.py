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


"""Options for BigMLer reify option

"""

def get_reify_options(defaults=None):
    """Reify-related options

    """

    if defaults is None:
        defaults = {}
    options = {

        # Resource ID
        '--id': {
            'dest': 'resource_id',
            'default': defaults.get('resource_id', None),
            'help': ("ID for the resource to be reified.")},

        # Language for the output (currently only python available)
        '--language': {
            'dest': 'language',
            'default': defaults.get('language', 'python'),
            'choices': ["python", "whizzml"],
            'help': ("Language for the resource to be reified in.")},

        # Name of the file to output the code.
        "--output": {
            'action': 'store',
            'dest': 'output',
            'default': defaults.get('output', None),
            'help': "Path to the file to output the reify code."},

        # Add updatable field structure information to the source update call
        '--add-fields': {
            'action': 'store_true',
            'dest': 'add_fields',
            'default': defaults.get('add_fields', False),
            'help': ("Add the updatable fields structure information"
                     " to the source update call.")},

        # Don't add the updatable field structure information to the
        # source update call. As opposed to --add-fields
        '--no-add-fields': {
            'action': 'store_false',
            'dest': 'add_fields',
            'default': defaults.get('add_fields', False),
            'help': ("Don't add the updatable fields structure information"
                     " to the source update call.")},
    }

    return options
