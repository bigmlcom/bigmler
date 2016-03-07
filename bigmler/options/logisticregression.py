# -*- coding: utf-8 -*-
#
# Copyright 2014-2016 BigML
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


"""Options for BigMLer logistic regression

"""

def get_logistic_regression_options(defaults=None):
    """Adding arguments for the logistic regression subcommand

    """

    if defaults is None:
        defaults = {}

    options = {
        # Input fields to include in the cluster.
        '--logistic-fields': {
            "action": 'store',
            "dest": 'logistic_fields',
            "default": defaults.get('logistic_fields', None),
            "help": ("Comma-separated list of input fields"
                     " (predictors) to create the logistic regression.")},

        # If a BigML logistic regression is provided, the script will
        # use it to generate predictions
        '--logistic-regression': {
            'action': 'store',
            'dest': 'logistic_regression',
            'default': defaults.get('logistic_regression', None),
            'help': "BigML logistic regression Id."},

        # The path to a file containing logistic regression ids.
        '--logistic-regressions': {
            'action': 'store',
            'dest': 'logistic_regressions',
            'default': defaults.get('logistic_regressions', None),
            'help': ("Path to a file containing logisticregression/ids."
                     " One logisticregression"
                     " per line (e.g., "
                     "logisticregression/50a206a8035d0706dc000376"
                     ").")},

        # If a BigML json file containing a logistic regression
        # structure is provided,
        # the script will use it.
        '--logistic-file': {
            'action': 'store',
            'dest': 'logistic_file',
            'default': defaults.get('logistic_file', None),
            'help': "BigML logistic regression JSON structure file."},

        # bias term in the logistic regression.
        '--bias': {
            "action": 'store',
            "dest": 'bias',
            "default": defaults.get('bias', 1),
            "type": float,
            "help": ("Scale of the intercept term. Setting this to 0 will"
                     " exclude the bias term from the solution. Must be"
                     " greater than or equal to 0. ")},

        # The strength of the regularization step. Must be greater than 0.
        '--c': {
            'action': 'store',
            'dest': 'lr_c',
            'default': defaults.get('lr_c', 1),
            'type': float,
            'help': ("The strength of the regularization step. Must be"
                     " greater than 0.")},

        # Stopping criteria for solver.
        '--eps': {
            'action': 'store',
            'dest': 'eps',
            'default': defaults.get('eps', 0.00001),
            'type': float,
            'help': ("Stopping criteria for solver. If the difference between"
                     " the results from the current and last iterations is"
                     " less than eps, then the solver is finished.")},

        # No missing values for numeric predictors
        '--no-missing-numerics': {
            'action': 'store_false',
            'dest': 'missing_numerics',
            'default': defaults.get('missing_numerics', True),
            'help': ("Whether to create an additional binary predictor each"
                     " numeric field which denotes a missing value. If"
                     " true, these predictors are not created, and rows"
                     " containing missing numeric values are dropped. ")},

        # Missing values for numeric predictors
        '--normalize': {
            'action': 'store_true',
            'dest': 'normalize',
            'default': defaults.get('normalize', False),
            'help': ("Whether to normalize feature vectors in training"
                     " and predicting.")},

        # Does not create a logistic regression just a dataset.
        '--no-logistic-regression': {
            'action': 'store_true',
            'dest': 'no_logistic_regression',
            'default': defaults.get('no_logistic_regression', False),
            'help': "Do not create a logistic regression."},

        # The path to a file containing logistic regression attributes.
        '--logistic-regression-attributes': {
            'action': 'store',
            'dest': 'logistic_regression_attributes',
            'default': defaults.get('logistic_regression_attributes', None),
            'help': ("Path to a json file describing logistic regression"
                     " attributes.")},

        # Create a logistic regression, not just a dataset.
        '--no-no-logistic-regression': {
            'action': 'store_false',
            'dest': 'no_logistic_regression',
            'default': defaults.get('no_logistic_regression', False),
            'help': "Create a logistic."}

}
    return options
