# -*- coding: utf-8 -*-
#
# Copyright 2014-2022 BigML
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


"""Options for BigMLer project processing

"""

def get_project_options(defaults=None):
    """project-related options

    """

    if defaults is None:
        defaults = {}

    options = {
        # The path to a file containing project attributes.
        '--project-attributes': {
            'action': 'store',
            'dest': 'project_attributes',
            'default': defaults.get('project_attributes', None),
            'help': ("Path to a json file describing project"
                     " attributes.")},

        # The organization ID that the project should be assigned to
        '--organization': {
            'action': 'store',
            'dest': 'organization',
            'default': defaults.get('organization', None),
            'help': ("ID of the organization where the project is to"
                     " be created.")}}

    return options
