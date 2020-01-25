# -*- coding: utf-8 -*-
#
# Copyright 2014-2020 BigML
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


"""Options for BigMLer dataset transformations processing

"""

def get_dataset_trans_options(defaults=None):
    """Dataset transformations-related options

    """

    if defaults is None:
        defaults = {}

    options = {

        # String describing the datasets to be used as origin and their attrs.
        '--datasets-json': {
            'action': 'store',
            'dest': 'datasets_json',
            'default': defaults.get('datasets_json', None),
            'help': ("JSON string describing the datasets used as origin to"
                     " merge or join "
                     " (e.g., [\"{\\\"id\\\": "
                     "\\\"dataset/50a20697035d0706da0004a4\\\"}\", "
                     " {\\\"id\\\": "
                     "\\\"dataset/50a20697035d0706da0004b5\\\"}]\""
                     "]).")},

        # File. The path to the data file
        '--file': {
            'action': 'store',
            'dest': 'training_set',
            'default': defaults.get('training_set', None),
            'help': ("Path to the file containing the data.")},

        # Merge. Alias for multi-dataset
        '--merge': {
            'action': 'store_true',
            'dest': 'multi_dataset',
            'default': defaults.get('multi_dataset', False),
            'help': ("Generate a new dataset by adding existing"
                     " datasets (alias for --multi-dataset).")},

        # Juxtapose: join the rows in each dataset according to row index
        '--juxtapose': {
            'action': 'store_true',
            'dest': 'juxtapose',
            'default': defaults.get('juxtapose', False),
            'help': ("Generate a new dataset by joining the rows"
                     "in several datasets according to row index.")},

        # String describing the sql query to be executed.
        '--sql-query': {
            'action': 'store',
            'dest': 'sql_query',
            'default': defaults.get('sql_query', None),
            'help': ("SQL query to be executed"
                     " (e.g., \"select A.`000000` as x, A.`00000a` as z, "
                     "A.`00000c` from A, B where A.id = B.id\").")},

        # Path to the JSON file describing the SQL output fields and types
        '--sql-output-fields': {
            'action': 'store',
            'dest': 'sql_output_fields',
            'default': defaults.get('sql_output_fields', None),
            'help': ("Path to a JSON file describing the structure and "
                     "types of the output fields.")},

        # Path to the JSON file describing the query to be executed
        '--json-query': {
            'action': 'store',
            'dest': 'json_query',
            'default': defaults.get('json_query', None),
            'help': ("Path to the JSON file describing the SQL query to "
                     "be executed.")}}

    return options
