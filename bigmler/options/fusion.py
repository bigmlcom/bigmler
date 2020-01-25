# -*- coding: utf-8 -*-
#
# Copyright 2019-2020 BigML
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


"""Options for BigMLer Fusion

"""

def get_fusion_options(defaults=None):
    """Adding arguments for the fusion subcommand

    """

    if defaults is None:
        defaults = {}

    options = {
        # If a list of BigML models is provided, the script will
        # create a Fusion from them
        '--fusion-models': {
            "action": 'store',
            "dest": 'fusion_models',
            "default": defaults.get('fusion_models', None),
            "help": ("Comma-separated list of models to be included "
                     "in the Fusion resource.")},

        # If a path to the JSON of model maps, the script will
        # create a Fusion from it
        '--fusion-models-file': {
            "action": 'store',
            "dest": 'fusion_models_file',
            "default": defaults.get('fusion_models_file', None),
            "help": ("Path to a JSON file that contains a list "
                     "of model IDs or maps to include in the "
                     "Fusion resource.")},

        # If a BigML Fusion is provided, the script will
        # use it to generate predictions
        '--fusion': {
            'action': 'store',
            'dest': 'fusion',
            'default': defaults.get('fusion', None),
            'help': "BigML Fusion Id."},

        # The path to a file containing fusion ids.
        '--fusions': {
            'action': 'store',
            'dest': 'fusions',
            'default': defaults.get('fusions', None),
            'help': ("Path to a file containing fusion/ids."
                     " One Fusion"
                     " per line (e.g., "
                     "fusion/50a206a8035d0706dc000376"
                     ").")},

        # If a BigML JSON file containing a Fusion
        # structure is provided,
        # the script will use it.
        '--fusion-file': {
            'action': 'store',
            'dest': 'fusion_file',
            'default': defaults.get('fusion_file', None),
            'help': "BigML Fusion JSON structure file."},

        # The path to a file containing Fusion attributes.
        '--fusion-attributes': {
            'action': 'store',
            'dest': 'fusion_attributes',
            'default': defaults.get('fusion_attributes', None),
            'help': ("Path to a json file describing Fusion"
                     " attributes.")}}

    return options
