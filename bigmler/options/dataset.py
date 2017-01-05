# -*- coding: utf-8 -*-
#
# Copyright 2014-2017 BigML
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


"""Options for BigMLer dataset processing

"""

def get_dataset_options(defaults=None):
    """Dataset-related options

    """

    if defaults is None:
        defaults = {}

    options = {
        # If a BigML dataset is provided, the script won't create a new one
        '--dataset': {
            'action': 'store',
            'dest': 'dataset',
            'default': defaults.get('dataset', None),
            'help': "BigML dataset Id."},

        # The path to a file containing dataset ids.
        '--datasets': {
            'action': 'store',
            'dest': 'datasets',
            'default': defaults.get('datasets', None),
            'help': ("Path to a file containing dataset/ids. Just"
                     " one dataset per line"
                     " (e.g., dataset/50a20697035d0706da0004a4).")},

        # If a BigML json file containing a dataset structure is provided,
        # the script will use it.
        '--dataset-file': {
            'action': 'store',
            'dest': 'dataset_file',
            'default': defaults.get('dataset_file', None),
            'help': "BigML dataset JSON structure file."},

        # Sampling to use when using bagging.
        '--sample-rate': {
            'action': 'store',
            'dest': 'sample_rate',
            'default': defaults.get('sample_rate', 1.0),
            'type': float,
            'help': "Sample rate to split datasets."},

        # Fields to include in the dataset.
        '--dataset-fields': {
            'action': 'store',
            'dest': 'dataset_fields',
            'default': defaults.get('dataset_fields', None),
            'help': ("Comma-separated list of field column numbers"
                     " to include in the dataset.")},

        # Path to a file that includes a JSON filter.
        '--json-filter': {
            'action': 'store',
            'dest': 'json_filter',
            'default': defaults.get('json_filter', None),
            'help': "File including a JSON filter."},

        # Path to a file that includes a lisp filter.
        '--lisp-filter': {
            'action': 'store',
            'dest': 'lisp_filter',
            'default': defaults.get('lisp_filter', None),
            'help': "File including a Lisp filter."},

        # Make dataset public.
        '--public-dataset': {
            'action': 'store_true',
            'dest': 'public_dataset',
            'default': defaults.get('public_dataset', False),
            'help': "Make generated dataset public."},

        # Set a price tag to your dataset.
        '--dataset-price': {
            'action': 'store',
            'dest': 'dataset_price',
            'type': float,
            'default': defaults.get('dataset_price', 0.0),
            'help': "Price for the dataset."},

        # Doesn't make dataset public.
        '--no-public-dataset': {
            'action': 'store_false',
            'dest': 'public_dataset',
            'default': defaults.get('public_dataset', False),
            'help': "Doesn't make generated dataset public."},

        # Does not create a dataset.
        '--no-dataset': {
            'action': 'store_true',
            'dest': 'no_dataset',
            'default': defaults.get('no_dataset', False),
            'help': "Do not create a dataset."},

        # Seed. The value used in dataset's splits and sampling as seed
        '--seed': {
            'action': 'store',
            'dest': 'seed',
            'default': defaults.get('seed', None),
            'help': "Value used as seed in dataset splits and sampling."},

        # The path to a file containing dataset attributes.
        '--dataset-attributes': {
            'action': 'store',
            'dest': 'dataset_attributes',
            'default': defaults.get('dataset_attributes', None),
            'help': ("Path to a json file describing dataset"
                     " attributes.")},
        # Multi-dataset. Generate new dataset from a list of existing datasets.
        '--multi-dataset': {
            'action': 'store_true',
            'dest': 'multi_dataset',
            'default': defaults.get('multi_dataset', False),
            'help': ("Generate a new dataset by adding existing"
                     " datasets.")},

        # The path to a file containing multi-dataset attributes.
        '--multi-dataset-attributes': {
            'action': 'store',
            'dest': 'multi_dataset_attributes',
            'default': defaults.get('multi_dataset_attributes', None),
            'help': ("Path to a json file describing multi-dataset"
                     " attributes.")},

        # Create a dataset.
        '--no-no-dataset': {
            'action': 'store_false',
            'dest': 'no_dataset',
            'default': defaults.get('no_dataset', False),
            'help': "Create a dataset."},

        # Set the part of training data to be held out for testing
        '--test-split': {
            'action': 'store',
            'dest': 'test_split',
            'type': float,
            'default': defaults.get('test_split', 0.0),
            'help': ("Part of training data to be held out for "
                     "testing (e.g. --test-split 0.2).")},

        # Path to the file containing fields generators for the new dataset.
        # Used when generating a dataset from another by adding new fields
        # combining or setting its contents.
        '--new-fields': {
            'action': 'store',
            'dest': 'new_fields',
            'default': defaults.get('new_fields', None),
            'help': ("Path to the file containing fields generators."
                     " Used to create a new dataset from an existing"
                     " one by adding new fields combining or"
                     " setting its contents.")},

        # Exports the dataset to a CSV file
        '--to-csv': {
            'action': 'store',
            'dest': 'to_csv',
            'nargs': '?',
            'const': '',
            'default': defaults.get('to_csv', None),
            'help': "Path to the exported dataset file."}}

    return options
