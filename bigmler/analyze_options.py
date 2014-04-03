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

def subparser_options(subparsers, defaults={}):
    """Adding arguments for the analyze subcommand

    """

    parser_analysis = subparsers.add_parser('analyze')
    parser_analysis.add_argument('--k-fold-cross-validation',
                                 action='store',
                                 dest='k_fold_cv',
                                 default=defaults.get('k_fold_cv', None),
                                 help="K-fold cross-validation index.")
    # Name of the directory where session files will be stored. If --output
    # is set, this setting will be overriden by it.
    parser_analysis.add_argument('--output-dir',
                                 action='store',
                                 dest='output_dir',
                                 default=defaults.get('output_dir', None),
                                 help=("Directory where session files will be stored."
                                       " --output file path will override it if both"
                                       " are set."))
    # If a BigML dataset is provided, the script won't create a new one
    parser_analysis.add_argument('--dataset',
                                 action='store',
                                 dest='dataset',
                                 default=defaults.get('dataset', None),
                                 help="BigML dataset Id.")
