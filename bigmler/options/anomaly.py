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


"""Options for BigMLer anomaly

"""

ANOMALIES_IN = 'in'
ANOMALIES_OUT = 'out'

def get_anomaly_options(defaults=None):
    """Adding arguments for the anomaly subcommand

    """

    if defaults is None:
        defaults = {}

    options = {
        # Input fields to include in the cluster.
        '--anomaly-fields': {
            "action": 'store',
            "dest": 'anomaly_fields',
            "default": defaults.get('anomaly_fields', None),
            "help": ("Comma-separated list of input fields"
                     " (predictors) to create the anomaly.")},

        # If a BigML anomaly id is provided, the script will use it to generate
        # anomaly score predictions.
        '--anomaly': {
            'action': 'store',
            'dest': 'anomaly',
            'default': defaults.get('anomaly', None),
            'help': "BigML anomaly Id."},

        # The path to a file containing anomaly detector ids.
        '--anomalies': {
            'action': 'store',
            'dest': 'anomalies',
            'default': defaults.get('anomalies', None),
            'help': ("Path to a file containing anomalies/ids. One anomaly"
                     " detector id per line (e.g.,"
                     " anomaly/50a206a8035d0706dc000376"
                     ").")},

        # If a BigML json file containing an anomaly structure is provided,
        # the script will use it to generate
        # anomaly score predictions.
        '--anomaly-file': {
            'action': 'store',
            'dest': 'anomaly_file',
            'default': defaults.get('anomaly_file', None),
            'help': "BigML anomaly detector JSON structure file."},

        # Does not create an anomaly detector, just a dataset.
        '--no-anomaly': {
            'action': 'store_true',
            'dest': 'no_anomaly',
            'default': defaults.get('no_anomaly', False),
            'help': "Do not create an anomaly detector."},

        # The path to a file containing anomaly attributes.
        '--anomaly-attributes': {
            'action': 'store',
            'dest': 'anomaly_attributes',
            'default': defaults.get('anomaly_attributes', None),
            'help': ("Path to a json file describing anomaly detector"
                     " attributes.")},

        # Create an anomaly detector, not just a dataset.
        '--no-no-anomaly': {
            'action': 'store_false',
            'dest': 'no_anomaly',
            'default': defaults.get('no_anomaly', False),
            'help': "Create an anomaly detector."},

        # The seed to be used in anomaly detector building.
        '--anomaly-seed': {
            'action': 'store',
            'dest': 'anomaly_seed',
            'default': defaults.get('anomaly_seed', None),
            'help': "The seed to be used in anomaly building."},

        # The path to a file containing anomaly score attributes.
        '--anomaly-score-attributes': {
            'action': 'store',
            'dest': 'anomaly_score_attributes',
            'default': defaults.get('anomaly_score_attributes', None),
            'help': ("Path to a json file describing anomaly score"
                     " attributes.")},

        # The path to a file containing batch anomaly score attributes.
        '--batch-anomaly-score-attributes': {
            'action': 'store',
            'dest': 'batch_anomaly_score_attributes',
            'default': defaults.get('batch_anomaly_score_attributes', None),
            'help': ("Path to a json file describing batch anomaly score"
                     " attributes.")},

        # Creates scores using the training dataset for the anomaly detector
        '--score': {
            'action': 'store_true',
            'dest': 'score',
            'default': defaults.get('score', False),
            'help': "Creates scores for the training dataset."},

        # Doesn't create scores (as opposed to --score)
        '--no-score': {
            'action': 'store_false',
            'dest': 'score',
            'default': defaults.get('score', False),
            'help': "Doesn't create scores for the training dataset."},

        # Generates a new dataset from the dataset used to create the anomaly
        # detector, including only the top anomalies or excluding
        # them.
        '--anomalies-dataset': {
            'action': 'store',
            'dest': 'anomalies_dataset',
            'default': defaults.get('anomalies_dataset', None),
            'choices': [ANOMALIES_IN, ANOMALIES_OUT],
            'help': ("Generates a new dataset from the dataset used to create"
                     " the anomaly detector, including only the top anomalies"
                     " or excluding them.")},

        # Number of selected top anomalies
        '--top-n': {
            'action': 'store',
            'dest': 'top_n',
            'default': defaults.get('top_n', 0),
            'type': int,
            'help': ("Number of selected top anomalies.")},

        # Number of trees in the anomaly detector
        '--forest-size': {
            'action': 'store',
            'dest': 'forest_size',
            'default': defaults.get('forest_size', 0),
            'type': int,
            'help': ("Number of trees in the anomaly detector.")}}

    return options
