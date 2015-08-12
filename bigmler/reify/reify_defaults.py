# -*- coding: utf-8 -*-
#
# Copyright 2015 BigML
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

"""BigMLer - defaults for reify subcommand

"""
import json


COMMON_DEFAULTS = {
    'create': {
        'category': [0],
        'description': [None, ""]
    },
    'update': {
        'tags': [[]],
    }
}

DEFAULTS = {
    "source": {
        "create": {
            'name': ["Unnamed inline source"],
            'data': [None, ""],
            'disable_datetime': [False],
            'file': [None, ""],
            'project': [None],
            'remote': [None, ""],
            'source_parser': [{
                 "header": True, "locale": "en-US", "missing_tokens": [ "", "NaN", "NULL", "N/A", "null", "-", "#REF!", "#VALUE!", "?", "#NULL!", "#NUM!", "#DIV/0", "n/a", "#NAME?", "NIL", "nil", "na", "#N/A", "NA" ], "quote": "\"", "separator": "," }, { "header": True, "locale": "en_US", "missing_tokens": [ "", "NaN", "NULL", "N/A", "null", "-", "#REF!", "#VALUE!", "?", "#NULL!", "#NUM!", "#DIV/0", "n/a", "#NAME?", "NIL", "nil", "na", "#N/A", "NA" ], "quote": "\"", "separator": "," }]
        },
        "update": {
            "term_analysis": [{"enabled": True}]
        }
    },
    "dataset": {
        "create": {
            'excluded_fields': [[]],
            'all_but': [[]],
            'all_fields': [True],
            'json_filter': [''],
            'lisp_filter': [''],
            'sample_rate': [1.0],
            'out_of_bag': [False],
            'seed': [None],
            'price': [0],
            'replacement': [False],
            'tags': [[]],
            'term_limit': [1000]
        },
        "update": {
            'private': [True],
            'shared': [False]
        }
    },
    "model": {
        "create": {
            'excluded_fields': [[]],
            'ordering': [0],
            'out_of_bag': [False],
            'randomize': [False],
            'replacement': [False],
            'sample_rate': [1.0],
            'seed': [None],
            'stat_pruning': [True],
            'balance_objective': [False],
            'weight_field': [None, ''],
            'objective_weights': [None, []],
            'missing_splits': [False],
            'node_threshold': 512
        }
    }
}
