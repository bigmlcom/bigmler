# -*- coding: utf-8 -*-
#
# Copyright 2015-2020 BigML
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


COMMON_DEFAULTS = {
    'create': {
        'category': [0],
        'description': [None, ""],
        'tags': [[]]
    },
    'update': {
        'category': [0],
        'description': [None, ""],
        'tags': [[]]
    }
}

DEFAULTS = {
    "source": {
        "create": {
            'name': ["Unnamed inline source"],
            'data': [None, ""],
            'disable_datetime': [False],
            'project': [None],
            'source_parser': [ \
                {"header": True, "locale": "en-US",
                 "missing_tokens": [ \
                    "", "NaN", "NULL", "N/A", "null", "-", "#REF!", "#VALUE!",
                    "?", "#NULL!", "#NUM!", "#DIV/0", "n/a", "#NAME?", "NIL",
                    "nil", "na", "#N/A", "NA"],
                 "quote": "\"",
                 "separator": ","},
                {"header": True,
                 "locale": "en_US",
                 "missing_tokens": [ \
                     "", "NaN", "NULL", "N/A", "null", "-", "#REF!", "#VALUE!",
                     "?", "#NULL!", "#NUM!", "#DIV/0", "n/a", "#NAME?", "NIL",
                     "nil", "na", "#N/A", "NA"],
                 "quote": "\"",
                 "separator": ","}]
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
            'selective_pruning': [None],
            'stat_pruning': [None],
            'balance_objective': [False],
            'weight_field': [None, ''],
            'objective_weights': [None, []],
            'missing_splits': [False],
            'node_threshold': [512]
        }
    },
    "ensemble": {
        "create": {
            'number_of_models': [10],
            'replacement': [False],
            'selective_pruning': [None],
            'stat_pruning': [None],
            'seed': [None],
            'ensemble_seed': [None],
            'boosting': [False, {}]
        }
    },
    "prediction": {
        "create": {
            'combiner': [0, None],
            'ordering': [0],
            'missing_strategy': [0],
            'private': [True],
            'threshold': [None, {}]
        }
    },
    "evaluation": {
        "create": {
            'confidence_threshold': [None],
            'combiner': [0, None],
            'missing_strategy': [0],
            'ordering': [0],
            'out_of_bag': [False],
            'negative_class': [None],
            'positive_class': [None],
            'replacement': [False],
            'sample_rate': [1.0],
            'seed': [None],
            'threshold': [None]
        },
        "update": {
            'private': [True]
        }
    },
    "anomaly": {
        "create": {
            'anomaly_seed': [None],
            'constraints': [False],
            'excluded_fields': [[]],
            'id_fields': [[]],
            'forest_size': [128],
            'out_of_bag': [False],
            'replacement': [False],
            'sample_rate': [1.0],
            'seed': [None],
            'top_n': [10]
        }
    },
    "cluster": {
        "create": {
            'balance_fields': [True],
            'cluster_seed': [None],
            'critical_value': [None, 5],
            'default_numeric_value': [None],
            'excluded_fields': [[]],
            'field_scales': [{}],
            'model_clusters': [False],
            'out_of_bag': [False],
            'replacement': [False],
            'sample_rate': [1.0],
            'seed': [None],
            'summary_fields': [[]],
            'weight_field': [""]
        }
    },
    "centroid": {
        "create": {
            'missing_strategy': [0]
        },
        "update": {
            'private': [True]
        },
    },
    "batchanomalyscore": {
        "create":{
            'all_fields': [False],
            'header': [True],
            'output_dataset': [False],
            'separator': [','],
            'score_name': ['score', None, '']
        }
    },
    "batchcentroid": {
        "create":{
            'all_fields': [False],
            'header': [True],
            'output_dataset': [False],
            'separator': [','],
            'distance': [False]
        }
    },
    "batchprediction": {
        "create": {
            'all_fields': [False],
            'confidence_threshold': [None],
            'combiner': [0, None],
            'confidence': [False],
            'confidence_name': [None, ''],
            'header': [True],
            'missing_strategy': [0],
            'negative_class': [None],
            'negative_class_confidence': [None],
            'output_dataset': [False],
            'output_fields': [None, []],
            'positive_class': [None],
            'separator': [','],
            'threshold': [None]
        }
    }
}
