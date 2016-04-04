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


"""Options for BigMLer analyze

"""
from __future__ import absolute_import


import os


ACCURACY = "accuracy"
BIGML_MAX_NODES = os.environ.get("BIGML_MAX_NODES", 2000)
MINIMIZE_OPTIONS = ["mean_squared_error", "mean_absolute_error"]
MAXIMIZE_OPTIONS = [ACCURACY, "precision", "recall", "phi", "f_measure",
                    "r_squared", "phi_coefficient"]
OPTIMIZE_OPTIONS = [ACCURACY, "precision", "recall", "phi", "f_measure",
                    "mean_squared_error", "mean_absolute_error", "r_squared",
                    "phi_coefficient"]

def get_analyze_options(defaults=None):
    """Adding arguments for the analyze subcommand

    """


    if defaults is None:
        defaults = {}

    options = {
        # K-fold cross-validation flag
        '--cross-validation': {
            "action": 'store_true',
            "dest": 'cv',
            "default": defaults.get('cv', False),
            "help": "K-fold cross-validation flag."},

        # K-fold cross-validation index
        '--k-folds': {
            "action": 'store',
            "dest": 'k_folds',
            "default": defaults.get('k_folds', None),
            "type": int,
            "help": "K-fold cross-validation index."},

        # Name of the directory where session files will be stored. If --output
        # is set, this setting will be overriden by it.
        '--output-dir': {
            "action": 'store',
            "dest": 'output_dir',
            "default": defaults.get('output_dir', None),
            "help": ("Directory where session files will be"
                     " stored. --output file path will "
                     " override it if both"
                     " are set.")},

        # Staleness to stop --features analysis
        '--staleness': {
            "action": 'store',
            "dest": 'staleness',
            "type": float,
            "default": defaults.get('staleness', None),
            "help": ("Limit staleness when using --features"
                     " analysis.")},

        # Penalty per feature in --features analysis
        '--penalty': {
            "action": 'store',
            "dest": 'penalty',
            "type": float,
            "default": defaults.get('penalty', None),
            "help": ("Penalty for each feature in --features"
                     " analysis.")},

        # Features: Set on the feature exclusion analysis
        '--features': {
            "action": 'store_true',
            "dest": 'features',
            "default": defaults.get('features', False),
            "help": "Features analysis."},

        # Mazimize: evaluation measure to be maximized
        '--maximize': {
            "action": 'store',
            "dest": 'maximize',
            "choices": MAXIMIZE_OPTIONS,
            "default": defaults.get('maximize', ACCURACY),
            "help": ("Evaluation measure to be maximized. This flag will be"
                     " deprecated. Please, use --optimize.")},

        # Optimize: evaluation measure to be optimized
        '--optimize': {
            "action": 'store',
            "dest": 'optimize',
            "choices": OPTIMIZE_OPTIONS,
            "default": defaults.get('optimize', ACCURACY),
            "help": "Evaluation measure to be optimized."},

        # Optimize-category: in categorical models, name of the category
        # whose evaluation measure is to be optimized
        '--optimize-category': {
            "action": 'store',
            "dest": 'optimize_category',
            "default": defaults.get('optimize-category', None),
            "help": ("Name of the category whose evaluation measure"
                     " is to be optimized.")},

        # Min_nodes: Minimum number of nodes to start the node threshold
        # analysis
        '--min-nodes': {
            "action": 'store',
            "dest": 'min_nodes',
            "type": int,
            "default": defaults.get('min_nodes', None),
            "help": ("Minimum number of nodes to start the"
                     " node threshold analysis.")},

        # Max_nodes: Maximum number of nodes to end the node threshold analysis
        '--max-nodes': {
            "action": 'store',
            "dest": 'max_nodes',
            "type": int,
            "default": defaults.get('max_nodes',
                                    BIGML_MAX_NODES),
            "help": ("Maximum number of nodes to end the"
                     " node threshold analysis.")},

        # Nodes: Set on node threshold analysis.
        '--nodes': {
            "action": 'store_true',
            "dest": 'nodes',
            "default": defaults.get('nodes', False),
            "help": "Node threshold analysis."},

        # Nodes step: Step to increase the nodes threshold number
        '--nodes-step': {
            "action": 'store',
            "dest": 'nodes_step',
            "type": int,
            "default": defaults.get('nodes_step', None),
            "help": ("Step to increase the nodes"
                     " threshold number in nodes "
                     " threshold analysis. If not set,"
                     " an increase of 100 is used")},

        # Exclude some features from the features analyze
        '--exclude-features': {
            "action": 'store',
            "dest": 'exclude_features',
            "default": defaults.get('exclude_features',
                                    None),
            "help": ("List of comma-separated field names to"
                     " be excluded from the features"
                     " analysis.")},

        # random candidates: Set on random candidates analysis.
        '--random-fields': {
            "action": 'store_true',
            "dest": 'random_fields',
            "default": defaults.get('random_fields', False),
            "help": "Random candidates analysis for ensembles."},

        # predictions-csv: Creates a batch prediction file with the kfold
        # predictions.
        '--predictions-csv': {
            "action": 'store_true',
            "dest": 'predictions_csv',
            "default": defaults.get('predictions_csv', False),
            "help": ("Creates a CSV file with the predictions of the"
                     " optimized model.")}}

    return options
