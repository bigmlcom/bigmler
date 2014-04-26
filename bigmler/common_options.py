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


def common_options(parser, defaults={}):
    """Adds common options to the given parser

    """
    options = []
    # Shows log info for each https request.
    parser.add_argument('--debug',
                        action='store_true',
                        default=defaults.get('debug', False),
                        help="Activate debug level")
    options.append('--debug')

    # Uses BigML dev environment. Sizes must be under 16MB though.
    parser.add_argument('--dev',
                        action='store_true',
                        dest='dev_mode',
                        default=defaults.get('dev', False),
                        help=("Compute a test output using BigML FREE"
                             " development environment."))
    options.append('--dev')

    # BigML's username.
    parser.add_argument('--username',
                        action='store',
                        default=defaults.get('username', None),
                        help="BigML's username.")
    options.append('--username')

    # BigML's API key.
    parser.add_argument('--api-key',
                        action='store',
                        dest='api_key',
                        default=defaults.get('api-key', None),
                        help="BigML's API key.")
    options.append('--api-key')

    # Log file to store resources ids.
    parser.add_argument('--resources-log',
                        action='store',
                        dest='log_file',
                        default=defaults.get('resources_log', None),
                        help=("Path to a file to store new resources ids."
                              " One resource per line"
                              " (e.g., model/50a206a8035d0706dc000376)."))
    options.append('--resources-log')

    # Stores the retrieved resources in the output directory
    parser.add_argument('--store',
                        action='store_true',
                        dest='store',
                        default=defaults.get('store', False),
                        help=("Store the retrieved resources in the"
                              " output directory."))
    options.append('--store')

    # Clear global bigmler log files
    parser.add_argument('--clear-logs',
                        action='store_true',
                        dest='clear_logs',
                        default=defaults.get('clear_logs', False),
                        help="Clear global bigmler log files.")
    options.append('--clear-logs')

    # Max number of models to create in parallel.
    parser.add_argument('--max-parallel-models',
                        action='store',
                        dest='max_parallel_models',
                        default=defaults.get('max_parallel_models', 1),
                        type=int,
                        help="Max number of models to create in parallel.")
    options.append('--max-parallel-models')

    # Max number of evaluations to create in parallel.
    parser.add_argument('--max-parallel-evaluations',
                        action='store',
                        dest='max_parallel_evaluations',
                        default=defaults.get('max_parallel_evaluations', 1),
                        type=int,
                        help=("Max number of evaluations to create in"
                              " parallel."))
    options.append('--max-parallel-evaluations')

    # The name of the field that represents the objective field (i.e., class or
    # label) or its column number.
    parser.add_argument('--objective',
                        action='store',
                        dest='objective_field',
                        default=defaults.get('objective', None),
                        help=("The column number of the Objective Field"
                              " or its name, if headers are given."))
    options.append('--objective')

    # Use it to add a tag to the new resources created.
    defaults_tag = defaults.get('tag')
    defaults_tag = [] if defaults_tag is None else defaults_tag.split(",")
    parser.add_argument('--tag',
                        action='append',
                        default=defaults_tag,
                        help="Tag to later retrieve new resources.")
    options.append('--tag')

    # Avoid default tagging of resources.
    parser.add_argument('--no-tag',
                        action='store_false',
                        dest='no_tag',
                        default=defaults.get('no_tag', True),
                        help="No tag resources with default BigMLer tags.")
    options.append('--no-tag')

    # The following options are only useful to deactivate the corresponding
    # oposed default values
    #
    # Hides log info for each https request.
    parser.add_argument('--no-debug',
                        action='store_false',
                        dest='debug',
                        default=defaults.get('debug', False),
                        help="Deactivate debug level.")
    options.append('--no-debug')

    # Uses BigML standard environment.
    parser.add_argument('--no-dev',
                        action='store_false',
                        dest='dev_mode',
                        default=defaults.get('dev', False),
                        help=("Compute a test output using BigML "
                             "standard development environment."))
    options.append('--no-dev')

    # Input fields to include in the model.
    parser.add_argument('--model-fields',
                        action='store',
                        dest='model_fields',
                        default=defaults.get('model_fields', None),
                        help=("Comma-separated list of input fields"
                              " (predictors) to create the model."))
    options.append('--model-fields')

    # Turn on/off verbosity
    parser.add_argument('--verbosity',
                        action='store',
                        dest='verbosity',
                        default=defaults.get('verbosity', 1),
                        type=int,
                        choices=[0, 1],
                        help="Set verbosity: 0 to turn off, 1 to turn on.")
    options.append('--verbosity')

    # Resume a partial execution
    parser.add_argument('--resume',
                        action='store_true',
                        help="Resume command.")
    options.append('--resume')

    # Resume a partial execution
    parser.add_argument('--stack-level',
                        action='store',
                        dest='stack_level',
                        default=0,
                        type=int,
                        help="Resume command.")
    options.append('--stack_level')

    # If a BigML source is provided, the script won't create a new one
    parser.add_argument('--source',
                        action='store',
                        dest='source',
                        default=defaults.get('source', None),
                        help="BigML source Id.")
    options.append('--source')

    # Path to the training set.
    parser.add_argument('--train',
                        action='store',
                        dest='training_set',
                        nargs='?',
                        default=defaults.get('train', None),
                        help="Training set path.")
    options.append('--train')

    return options
