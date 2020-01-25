# -*- coding: utf-8 -*-
#
# Copyright 2017-2020 BigML
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


"""Options for BigMLer code export functions

"""

def get_export_options(defaults=None):
    """code export related options

    """

    if defaults is None:
        defaults = {}

    options = {
        # ID of the model to generate a local model
        '--model': {
            'action': 'store',
            'dest': 'model',
            'default': defaults.get('model', None),
            'help': ("ID of the model to generate a local model.")},
        # ID of the ensemble to generate the local models in the ensemble
        '--ensemble': {
            'action': 'store',
            'dest': 'ensemble',
            'default': defaults.get('ensemble', None),
            'help': ("ID of the ensemble to generate the local models in"
                     " the ensemble.")},
        '--language': {
            'action': 'store',
            'dest': 'language',
            'choices': ['python', 'javascript', 'tableau', 'mysql', 'r'],
            'default': defaults.get('language', 'javascript'),
            'help': ("Language to be used in code generation.")}}

        # If a BigML logistic regression is provided, the script will
        # use it to generate predictions
#        '--logistic-regression': {
#           'action': 'store',
#           'dest': 'logistic_regression',
#           'default': defaults.get('logistic_regression', None),
#           'help': "BigML logistic regression Id."}

    return options
