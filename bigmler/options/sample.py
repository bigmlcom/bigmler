# -*- coding: utf-8 -*-
#
# Copyright 2015-2016 BigML
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


"""Options for BigMLer sample

"""

def get_sample_options(defaults=None):
    """Adding arguments for the sample subcommand

    """

    if defaults is None:
        defaults = {}

    options = {
        # Input fields to include in the sample.
        '--sample-fields': {
            "action": 'store',
            "dest": 'sample_fields',
            "default": defaults.get('sample_fields', None),
            "help": ("Comma-separated list of input fields"
                     " (predictors) to create the sample.")},

        # If a BigML sample is provided, the script will use it to get
        # sample info.
        '--sample': {
            'action': 'store',
            'dest': 'sample',
            'default': defaults.get('sample', None),
            'help': "BigML sample Id."},

        # The path to a file containing sample ids.
        '--samples': {
            'action': 'store',
            'dest': 'samples',
            'default': defaults.get('samples', None),
            'help': ("Path to a file containing sample/ids. One sample"
                     " per line (e.g., sample/50a206a8035d0706dc000376"
                     ").")},

        # If a BigML json file containing a smaple structure is provided,
        # the script will use it.
        '--sample-file': {
            'action': 'store',
            'dest': 'sample_file',
            'default': defaults.get('sample_file', None),
            'help': "BigML sample JSON structure file."},

        # Does not create a sample just a dataset.
        '--no-sample': {
            'action': 'store_true',
            'dest': 'no_sample',
            'default': defaults.get('no_sample', False),
            'help': "Do not create a sample."},

        # The path to a file containing sample attributes.
        '--sample-attributes': {
            'action': 'store',
            'dest': 'sample_attributes',
            'default': defaults.get('sample_attributes', None),
            'help': ("Path to a json file describing sample"
                     " attributes.")},

        # Create a sample, not just a dataset.
        '--no-no-sample': {
            'action': 'store_false',
            'dest': 'no_sample',
            'default': defaults.get('no_sample', False),
            'help': "Create a sample."},

        # Prediction-header.
        '--sample-header': {
            'action': 'store_true',
            'dest': 'sample_header',
            'default': defaults.get('sample_header', False),
            'help': "Headers are added to the sample file."},

        # Prediction-header.
        '--no-sample-header': {
            'action': 'store_false',
            'dest': 'sample_header',
            'default': defaults.get('sample_header', False),
            'help': "No headers are added to the sample file."},

        # Field query string.
        '--fields-filter': {
            "action": 'store',
            "dest": 'fields_filter',
            "default": defaults.get('fields_filter', None),
            "help": ("Query string to filter the rows according to the"
                     " values of its fields.")},

        # Index as id for the selected rows.
        '--row-index': {
            'action': 'store_true',
            'dest': 'row_index',
            'default': defaults.get('row_index', False),
            'help': "An absolute row number is added to the selected rows."},

        # Don't add an index as id for the selected rows.
        '--no-row-index': {
            'action': 'store_false',
            'dest': 'row_index',
            'default': defaults.get('row_index', False),
            'help': "An absolute row number is added to the selected rows."},

        # Sampling mode.
        '--mode': {
            'action': 'store',
            'dest': 'mode',
            'default': defaults.get('mode', None),
            'choices': ["deterministic", "linear", "random"],
            'help': "Sampling mode."},

        # Number of times a row is present in the sample.
        '--occurrence': {
            'action': 'store_true',
            'dest': 'occurrence',
            'default': defaults.get('occurrence', False),
            'help': "Number of times a row is present in the sample."},

        # Don't add the number of times a row is present in the sample.
        '--no-occurrence': {
            'action': 'store_false',
            'dest': 'occurrence',
            'default': defaults.get('occurrence', False),
            'help': ("Don't add the number of times a row is present in"
                     " the sample.")},

        # precision
        '--precision': {
            "action": 'store',
            "dest": 'precision',
            "type": int,
            "default": defaults.get('precision', None),
            "help": ("Number of decimals in the returned values.")},

        # Number of rows returned by the sample.
        '--rows': {
            "action": 'store',
            "dest": 'rows',
            "type": int,
            "default": defaults.get('rows', None),
            "help": ("Number of rows returned by the sample.")},

        # Offset before the row sample.
        '--row-offset': {
            "action": 'store',
            "dest": 'row_offset',
            "type": int,
            "default": defaults.get('row_offset', 0),
            "help": ("Offset before the row sample.")},

        # Field used for sorting.
        '--row-order-by': {
            "action": 'store',
            "dest": 'row_order_by',
            "default": defaults.get('row_order_by', None),
            "help": ("Field ids used for sorting.")},

        # Sorted comma-separated list of fields to be used as columns
        # for sample rows.
        '--row-fields': {
            "action": 'store',
            "dest": 'row_fields',
            "default": defaults.get('row_fields', None),
            "help": ("Sorted comma-separated list of fields to be used"
                     "as columns for sample rows.")},

        # Comma-separated couple of field names to compute the Pearsons'
        # and Spearman's correlations and linear regression terms between them.
        '--stat-fields': {
            "action": 'store',
            "dest": 'stat_fields',
            "default": defaults.get('stat_fields', None),
            "help": ("Comma-separated couple of field ids to compute the"
                     " Pearsons' and Spearman's correlations and"
                     " linear regression terms between them.")},


        # Field name to compute the Pearsons'
        # and Spearman's correlations and linear regression terms between them
        # and the rest of numeric fields.
        '--stat-field': {
            "action": 'store',
            "dest": 'stat_field',
            "default": defaults.get('stat_field', None),
            "help": ("Numeric field to compute the"
                     " Pearsons' and Spearman's correlations and"
                     " linear regression terms between them"
                     " and the rest of numeric fields.")},

        # Unique, when set to true, repeated rows are removed.
        '--unique': {
            'action': 'store_true',
            'dest': 'unique',
            'default': defaults.get('unique', False),
            'help': "If True, repeated rows are removed."},

        # Don't remove repeated rows.
        '--no-unique': {
            'action': 'store_false',
            'dest': 'unique',
            'default': defaults.get('unique', False),
            'help': ("Don't remove repeated rows.")}}

    return options
