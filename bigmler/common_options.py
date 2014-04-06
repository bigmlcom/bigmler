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
"""Common options for the BigMLer parser

"""

def common_options(parser, defaults={}, constants={}):
    """Adds common options to the given parser

    """
    # Shows log info for each https request.
    parser.add_argument('--debug',
                        action='store_true',
                        default=defaults.get('debug', False),
                        help="Activate debug level")

    # Uses BigML dev environment. Sizes must be under 16MB though.
    parser.add_argument('--dev',
                        action='store_true',
                        dest='dev_mode',
                        default=defaults.get('dev', False),
                        help=("Compute a test output using BigML FREE"
                             " development environment."))

    # BigML's username.
    parser.add_argument('--username',
                        action='store',
                        default=defaults.get('username', None),
                        help="BigML's username.")

    # BigML's API key.
    parser.add_argument('--api-key',
                        action='store',
                        dest='api_key',
                        default=defaults.get('api-key', None),
                        help="BigML's API key.")

    # Log file to store resources ids.
    parser.add_argument('--resources-log',
                        action='store',
                        dest='log_file',
                        default=defaults.get('resources_log', None),
                        help=("Path to a file to store new resources ids."
                              " One resource per line"
                              " (e.g., model/50a206a8035d0706dc000376)."))

    # Stores the retrieved resources in the output directory
    parser.add_argument('--store',
                        action='store_true',
                        dest='store',
                        default=defaults.get('store', False),
                        help=("Store the retrieved resources in the"
                              " output directory."))

    # Clear global bigmler log files
    parser.add_argument('--clear-logs',
                        action='store_true',
                        dest='clear_logs',
                        default=defaults.get('clear_logs', False),
                        help="Clear global bigmler log files.")

    # Max number of models to create in parallel.
    parser.add_argument('--max-parallel-models',
                        action='store',
                        dest='max_parallel_models',
                        default=defaults.get('max_parallel_models', 1),
                        type=int,
                        help="Max number of models to create in parallel.")

    # Max number of evaluations to create in parallel.
    parser.add_argument('--max-parallel-evaluations',
                        action='store',
                        dest='max_parallel_evaluations',
                        default=defaults.get('max_parallel_evaluations', 1),
                        type=int,
                        help=("Max number of evaluations to create in"
                              " parallel."))

    # The name of the field that represents the objective field (i.e., class or
    # label) or its column number.
    parser.add_argument('--objective',
                        action='store',
                        dest='objective_field',
                        default=defaults.get('objective', None),
                        help=("The column number of the Objective Field"
                              " or its name, if headers are given."))

    # The following options are only useful to deactivate the corresponding
    # oposed default values
    #
    # Hides log info for each https request.
    parser.add_argument('--no-debug',
                        action='store_false',
                        dest='debug',
                        default=defaults.get('debug', False),
                        help="Deactivate debug level.")

    # Uses BigML standard environment.
    parser.add_argument('--no-dev',
                        action='store_false',
                        dest='dev_mode',
                        default=defaults.get('dev', False),
                        help=("Compute a test output using BigML "
                             "standard development environment."))
