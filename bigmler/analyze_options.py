# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012-2014 BigML
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


"""Parser for BigMLer analyze

"""
from __future__ import absolute_import


import os


from bigmler.common_options import common_options

ACCURACY = "accuracy"
BIGML_MAX_NODES = os.environ.get("BIGML_MAX_NODES", 2000)
MAXIMIZE_OPTIONS = [ACCURACY, "precision", "recall", "phi", "f_measure",
                    "mean_squared_error", "mean_absolute_error", "r_squared"]

def subparser_options(subparsers, defaults={}, constants={}):
    """Adding arguments for the analyze subcommand

    """

    parser_analysis = subparsers.add_parser('analyze')

    common_options(parser_analysis, defaults=defaults)

    # K-fold cross-validation flag
    parser_analysis.add_argument('--cross-validation',
                                 action='store_true',
                                 dest='cv',
                                 default=defaults.get('cv', False),
                                 help="K-fold cross-validation flag.")

    # K-fold cross-validation index
    parser_analysis.add_argument('--k-folds',
                                 action='store',
                                 dest='k_folds',
                                 default=defaults.get('k_folds', None),
                                 type=int,
                                 help="K-fold cross-validation index.")

    # Name of the directory where session files will be stored. If --output
    # is set, this setting will be overriden by it.
    parser_analysis.add_argument('--output-dir',
                                 action='store',
                                 dest='output_dir',
                                 default=defaults.get('output_dir', None),
                                 help=("Directory where session files will be"
                                       " stored. --output file path will "
                                       " override it if both"
                                       " are set."))

    # If a BigML dataset is provided, the script won't create a new one
    parser_analysis.add_argument('--dataset',
                                 action='store',
                                 dest='dataset',
                                 default=defaults.get('dataset', None),
                                 help="BigML dataset Id.")

    # Staleness to stop --features analysis
    parser_analysis.add_argument('--staleness',
                                 action='store',
                                 dest='staleness',
                                 type=float,
                                 default=defaults.get('staleness', None),
                                 help=("Limit staleness when using --features"
                                       " analysis."))

    # Penalty per feature in --features analysis
    parser_analysis.add_argument('--penalty',
                                 action='store',
                                 dest='penalty',
                                 type=float,
                                 default=defaults.get('penalty', None),
                                 help=("Penalty for each feature in --features"
                                       " analysis."))

    # Features: Set on the feature exclusion analysis
    parser_analysis.add_argument('--features',
                                 action='store_true',
                                 dest='features',
                                 default=defaults.get('features', False),
                                 help="Features analysis.")

    # Mazimize: evaluation measure to be maximized
    parser_analysis.add_argument('--maximize',
                                 action='store',
                                 dest='maximize',
                                 choices=MAXIMIZE_OPTIONS,
                                 default=defaults.get('maximize', ACCURACY),
                                 help="Evaluation measure to be maximized.")

    # Min_nodes: Minimum number of nodes to start the node threshold analysis
    parser_analysis.add_argument('--min-nodes',
                                 action='store',
                                 dest='min_nodes',
                                 type=int,
                                 default=defaults.get('min_nodes', None),
                                 help=("Minimum number of nodes to start the"
                                       "node threshold analysis."))

    # Max_nodes: Maximum number of nodes to end the node threshold analysis
    parser_analysis.add_argument('--max-nodes',
                                 action='store',
                                 dest='max_nodes',
                                 type=int,
                                 default=defaults.get('max_nodes',
                                                      BIGML_MAX_NODES),
                                 help=("Maximum number of nodes to end the"
                                       "node threshold analysis."))

    # Nodes: Set on node threshold analysis.
    parser_analysis.add_argument('--nodes',
                                 action='store_true',
                                 dest='nodes',
                                 default=defaults.get('nodes', False),
                                 help="Node threshold analysis.")

    # Nodes step: Step to increase the nodes threshold number
    parser_analysis.add_argument('--nodes-step',
                                 action='store',
                                 dest='nodes_step',
                                 type=int,
                                 default=defaults.get('nodes_step', None),
                                 help=("Step to increase the nodes"
                                       " threshold number in nodes "
                                       " threshold analysis. If not set,"
                                       " an increase of 100 is used"))
