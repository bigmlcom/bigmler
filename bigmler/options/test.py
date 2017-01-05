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


"""Options for BigMLer test files processing

"""

def get_test_options(defaults=None):
    """Test files-related options

    """

    if defaults is None:
        defaults = {}
    options = {
        # Path to the test set.
        "--test": {
            'action': 'store',
            'dest': 'test_set',
            'nargs': '?',
            'default': defaults.get('test', None),
            'help': "Test set path."},
        # Name of the file to output predictions.
        "--output": {
            'action': 'store',
            'dest': 'predictions',
            'default': defaults.get('output', None),
            'help': "Path to the file to output predictions."},

        # Set when the test set file doesn't include a header on the first
        # line.
        '--no-test-header': {
            'action': 'store_false',
            'dest': 'test_header',
            'default': defaults.get('test_header', True),
            'help': "The test set file hasn't a header."},

        # Test set field separator. Defaults to the locale csv
        # separator.
        '--test-separator': {
            'action': 'store',
            'dest': 'test_separator',
            'default': defaults.get('test_separator', None),
            'help': "Test set field separator."},

        # The path to a file containing attributes if you want to alter BigML's
        # default field attributes or the ones provided by the test file
        # header.
        '--test-field-attributes': {
            'action': 'store',
            'dest': 'test_field_attributes',
            'default': defaults.get('test_field_attributes', None),
            'help': ("Path to a csv file describing field attributes."
                     " One definition per line"
                     " (e.g., 0,'Last Name').")},

        # The path to a file containing types if you want to alter BigML's
        # type auto-detect.
        '--test-types': {
            'action': 'store',
            'dest': 'test_types',
            'default': defaults.get('test_types', None),
            'help': ("Path to a file describing field types. One"
                     " definition per line (e.g., 0, 'numeric').")},

        # If a BigML test source is provided, the script won't create a new one
        '--test-source': {
            'action': 'store',
            'dest': 'test_source',
            'default': defaults.get('test_source', None),
            'help': "BigML test source Id."},

        # If a BigML test dataset is provided, the script won't create a new
        # one
        '--test-dataset': {
            'action': 'store',
            'dest': 'test_dataset',
            'default': defaults.get('test_dataset', None),
            'help': "BigML test dataset Id."},

        # The path to a file containing dataset ids.
        '--test-datasets': {
            'action': 'store',
            'dest': 'test_datasets',
            'default': defaults.get('test_datasets', None),
            'help': ("Path to a file containing dataset/ids. Just"
                     " one dataset per line"
                     " (e.g., dataset/50a20697035d0706da0004a4).")},

        # Set when the test set file does include a header on the first
        # line. (opposed to --no-test-header)
        '--test-header': {
            'action': 'store_true',
            'dest': 'test_header',
            'default': defaults.get('test_header', True),
            'help': "The test set file has a header."}}

    return options
