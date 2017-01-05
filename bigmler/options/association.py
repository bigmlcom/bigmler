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


"""Options for BigMLer association

"""

def get_association_options(defaults=None):
    """Adding arguments for the association subcommand

    """

    if defaults is None:
        defaults = {}

    options = {
        # Input fields to include in the cluster.
        '--association-fields': {
            "action": 'store',
            "dest": 'association_fields',
            "default": defaults.get('association_fields', None),
            "help": ("Comma-separated list of input fields"
                     " (predictors) to create the association.")},

        # If a BigML association id is provided, the script will use it to
        # generate association set predictions.
        '--association': {
            'action': 'store',
            'dest': 'association',
            'default': defaults.get('association', None),
            'help': "BigML association Id."},

        # The path to a file containing association ids.
        '--associations': {
            'action': 'store',
            'dest': 'associations',
            'default': defaults.get('associations', None),
            'help': ("Path to a file containing association/ids. One"
                     " association per line (e.g., "
                     "association/50a206a8035d0706dc000376).")},

        # If a BigML json file containing an association structure is provided,
        # the script will use it.
        '--association-file': {
            'action': 'store',
            'dest': 'association_file',
            'default': defaults.get('association_file', None),
            'help': "BigML association JSON structure file."},

        # Maximum Number of rules to be included in the association
        '--max-k': {
            'action': 'store',
            'type': int,
            'dest': 'association_k',
            'default': defaults.get('association_k', None),
            'help': ("Maximum number of rules to be included in the "
                     " association.")},

        # Search strategy
        '--search-strategy': {
            'action': 'store',
            'dest': 'search_strategy',
            'choices': ["confidence", "coverage", "leverage",
                        "lift", "support"],
            'default': defaults.get('search_strategy', None),
            'help': ("The strategy for prioritizing the rules"
                     " in the search.")},

        # Does not create an association just a dataset.
        '--no-association': {
            'action': 'store_true',
            'dest': 'no_association',
            'default': defaults.get('no_association', False),
            'help': "Do not create an association."},

        # The path to a file containing cluster attributes.
        '--association-attributes': {
            'action': 'store',
            'dest': 'association_attributes',
            'default': defaults.get('association_attributes', None),
            'help': ("Path to a json file describing association"
                     " attributes.")},

        # Create an association, not just a dataset.
        '--no-no-association': {
            'action': 'store_false',
            'dest': 'no_association',
            'default': defaults.get('no_association', False),
            'help': "Create an association."}}

    return options
