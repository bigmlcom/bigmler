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


from bigmler.common_options import common_options


def subparser_options(subparsers, defaults={}, constants={}):
    """Adding arguments for the analyze subcommand

    """

    parser_analysis = subparsers.add_parser('analyze')

    common_options(parser_analysis, defaults=defaults, constants=constants)

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
                                 help="Features analysis")
