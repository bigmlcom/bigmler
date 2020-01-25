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


"""Options for BigMLer linear regression

"""

def get_linear_regression_options(defaults=None):
    """Adding arguments for the linear regression subcommand

    """

    if defaults is None:
        defaults = {}

    options = {
        # Input fields to include in the linear regression.
        '--inear-fields': {
            "action": 'store',
            "dest": 'linear_fields',
            "default": defaults.get('linear_fields', None),
            "help": ("Comma-separated list of input fields"
                     " (predictors) to create the linear regression.")},

        # If a BigML linear regression is provided, the script will
        # use it to generate predictions
        '--linear-regression': {
            'action': 'store',
            'dest': 'linear_regression',
            'default': defaults.get('linear_regression', None),
            'help': "BigML linear regression Id."},

        # The path to a file containing linear regression ids.
        '--linear-regressions': {
            'action': 'store',
            'dest': 'linear_regressions',
            'default': defaults.get('linear_regressions', None),
            'help': ("Path to a file containing linearregression/ids."
                     " One linearregression"
                     " per line (e.g., "
                     "linearregression/50a206a8035d0706dc000376"
                     ").")},

        # If a BigML json file containing a linear regression
        # structure is provided,
        # the script will use it.
        '--linear-file': {
            'action': 'store',
            'dest': 'linear_file',
            'default': defaults.get('linear_file', None),
            'help': "BigML linear regression JSON structure file."},

        # Does not create a linear regression just a dataset.
        '--no-linear-regression': {
            'action': 'store_true',
            'dest': 'no_linear_regression',
            'default': defaults.get('no_linear_regression', False),
            'help': "Do not create a linear regression."},

        # The path to a file containing linear regression attributes.
        '--linear-regression-attributes': {
            'action': 'store',
            'dest': 'linear_regression_attributes',
            'default': defaults.get('linear_regression_attributes', None),
            'help': ("Path to a json file describing linear regression"
                     " attributes.")},

        # Create a linear regression, not just a dataset.
        '--no-no-linear-regression': {
            'action': 'store_false',
            'dest': 'no_linear_regression',
            'default': defaults.get('no_linear_regression', False),
            'help': "Create a linear regression."}}

    return options
