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


"""Options for BigMLer PCA

"""

def get_pca_options(defaults=None):
    """Adding arguments for the pca subcommand

    """

    if defaults is None:
        defaults = {}

    options = {
        # Input fields to include in the PCA.
        '--pca-fields': {
            "action": 'store',
            "dest": 'pca_fields',
            "default": defaults.get('pca_fields', None),
            "help": ("Comma-separated list of input fields"
                     " (predictors) to create the PCA.")},

        # If a BigML PCA is provided, the script will
        # use it to generate projections
        '--pca': {
            'action': 'store',
            'dest': 'pca',
            'default': defaults.get('pca', None),
            'help': "BigML PCA Id."},

        # The path to a file containing PCA ids.
        '--pcas': {
            'action': 'store',
            'dest': 'pcas',
            'default': defaults.get('pcas', None),
            'help': ("Path to a file containing pca/ids."
                     " One PCA"
                     " per line (e.g., "
                     "pca/50a206a8035d0706dc000376"
                     ").")},

        # If a BigML json file containing a PCA
        # structure is provided,
        # the script will use it.
        '--pca-file': {
            'action': 'store',
            'dest': 'pca_file',
            'default': defaults.get('pca_file', None),
            'help': "BigML PCA JSON structure file."},

        # Does not create a PCA just a dataset.
        '--no-pca': {
            'action': 'store_true',
            'dest': 'no_pca',
            'default': defaults.get('no_pca', False),
            'help': "Do not create a PCA."},

        # The path to a file containing PCA attributes.
        '--pca-attributes': {
            'action': 'store',
            'dest': 'pca_attributes',
            'default': defaults.get('pca_attributes', None),
            'help': ("Path to a json file describing PCA"
                     " attributes.")},

        # The maximum number of components used to project
        '--max-components': {
            'action': 'store',
            'dest': 'max_components',
            'type':int,
            'default': defaults.get('max_components', None),
            'help': ("Maximum number of components used as projections.")},

        # The variance used as threshold in to generate the projection
        '--variance-threshold': {
            'action': 'store',
            'dest': 'variance_threshold',
            'type': float,
            'default': defaults.get('variance_threshold', None),
            'help': ("Variance used as threshold to generate projections.")},

        # Excludes the objective field of the dataset from the PCA input fields.
        '--exclude-objective': {
            'action': 'store_true',
            'dest': 'exclude_objective',
            'default': defaults.get('exclude_objective', False),
            'help': "Excludes the objective field from the PCA inputs."},

        # The path to a file containing batch projection attributes.
        '--batch-projection-attributes': {
            'action': 'store',
            'dest': 'batch_projection_attributes',
            'default': defaults.get('batch_projection_attributes', None),
            'help': ("Path to a json file describing batch projection"
                     " attributes.")},

        # The path to a file containing projection attributes.
        '--projection-attributes': {
            'action': 'store',
            'dest': 'projection_attributes',
            'default': defaults.get('projection_attributes', None),
            'help': ("Path to a json file describing projection"
                     " attributes.")},

        # Projection header. If set, headers are added to the projection file.
        '--projection-header': {
            'action': 'store_true',
            'dest': 'projection_header',
            'default': defaults.get('projection_header', False),
            'help': "Headers are added to the projections file."},

        # Projection fields. A comma-separated list of the fields that should
        # be included in the projections file.
        '--projection-fields': {
            'action': 'store',
            'dest': 'projection_fields',
            'default': defaults.get('projection_fields', None),
            'help': "Fields added to the projections file."},

        # Create a PCA, not just a dataset.
        '--no-no-pca': {
            'action': 'store_false',
            'dest': 'no_pca',
            'default': defaults.get('no_pca', False),
            'help': "Create a PCA."}}

    return options
