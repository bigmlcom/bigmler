# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012, 2013 BigML
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


"""Defaults parser for BigMLer

"""
import ConfigParser

DEFAULTS_FILE = 'bigmler.ini'

FLAGS = {'BigMLer': [{'flag': 'debug', 'type': 'boolean'},
                     {'flag': 'dev', 'type': 'boolean'},
                     {'flag': 'username', 'type': 'string'},
                     {'flag': 'api_key', 'type': 'string'},
                     {'flag': 'train', 'type': 'string'},
                     {'flag': 'test', 'type': 'string'},
                     {'flag': 'output', 'type': 'string'},
                     {'flag': 'objective', 'type': 'string'},
                     {'flag': 'category', 'type': 'int'},
                     {'flag': 'description', 'type': 'string'},
                     {'flag': 'field_names', 'type': 'string'},
                     {'flag': 'field_attributes', 'type': 'string'},
                     {'flag': 'types', 'type': 'string'},
                     {'flag': 'dataset_fields', 'type': 'string'},
                     {'flag': 'json_filter', 'type': 'string'},
                     {'flag': 'lisp_filter', 'type': 'string'},
                     {'flag': 'model_fields', 'type': 'string'},
                     {'flag': 'train_header', 'type': 'boolean'},
                     {'flag': 'test_header', 'type': 'boolean'},
                     {'flag': 'name', 'type': 'string'},
                     {'flag': 'source', 'type': 'string'},
                     {'flag': 'dataset', 'type': 'string'},
                     {'flag': 'model', 'type': 'string'},
                     {'flag': 'remote', 'type': 'boolean'},
                     {'flag': 'models', 'type': 'string'},
                     {'flag': 'datasets', 'type': 'string'},
                     {'flag': 'pruning', 'type': 'string'},
                     {'flag': 'datasets', 'type': 'string'},
                     {'flag': 'number_of_models', 'type': 'int'},
                     {'flag': 'sample_rate', 'type': 'float'},
                     {'flag': 'replacement', 'type': 'boolean'},
                     {'flag': 'max_parallel_models', 'type': 'int'},
                     {'flag': 'max_batch_models', 'type': 'int'},
                     {'flag': 'randomize', 'type': 'boolean'},
                     {'flag': 'no_tag', 'type': 'boolean'},
                     {'flag': 'tag', 'type': 'string'},
                     {'flag': 'model_tag', 'type': 'string'},
                     {'flag': 'public_dataset', 'type': 'boolean'},
                     {'flag': 'black_box', 'type': 'boolean'},
                     {'flag': 'white_box', 'type': 'boolean'},
                     {'flag': 'model_price', 'type': 'float'},
                     {'flag': 'dataset_price', 'type': 'float'},
                     {'flag': 'cpp', 'type': 'float'},
                     {'flag': 'progress_bar', 'type': 'boolean'},
                     {'flag': 'resources_log', 'type': 'string'},
                     {'flag': 'from_file', 'type': 'string'},
                     {'flag': 'source_tag', 'type': 'string'},
                     {'flag': 'dataset_tag', 'type': 'string'},
                     {'flag': 'prediction_tag', 'type': 'string'},
                     {'flag': 'evaluation_tag', 'type': 'string'},
                     {'flag': 'ensemble_tag', 'type': 'string'},
                     {'flag': 'all_tag', 'type': 'string'},
                     {'flag': 'locale', 'type': 'string'},
                     {'flag': 'combine_votes', 'type': 'string'},
                     {'flag': 'plurality', 'type': 'string'},
                     {'flag': 'verbosity', 'type': 'int'},
                     {'flag': 'fields_map', 'type': 'string'},
                     {'flag': 'clear_logs', 'type': 'boolean'},
                     {'flag': 'cross_validation_rate', 'type': 'float'},
                     {'flag': 'number_of_evaluations', 'type': 'int'},
                     {'flag': 'store', 'type': 'boolean'},
                     {'flag': 'test_split', 'type': 'float'},
                     {'flag': 'ensemble', 'type': 'string'},
                     {'flag': 'tlp', 'type': 'int'},
                     {'flag': 'prediction_info', 'type': 'string'},
                     {'flag': 'max_parallel_evaluations', 'type': 'int'},
                     {'flag': 'test_separator', 'type': 'string'},
                     {'flag': 'multi_label', 'type': 'boolean'},
                     {'flag': 'labels', 'type': 'string'},
                     {'flag': 'label_separator', 'type': 'string'},
                     {'flag': 'training_separator', 'type': 'string'},
                     {'flag': 'prediction_header', 'type': 'boolean'},
                     {'flag': 'prediction_fields', 'type': 'string'},
                     {'flag': 'seed', 'type': 'string'},
                     {'flag': 'max_parallel_ensembles', 'type': 'int'},
                     {'flag': 'ensembles', 'type': 'string'}]}


def get_user_defaults(defaults_file=DEFAULTS_FILE):
    """Looks for a defaults file and returns its contents

    """
    try:
        open(defaults_file).close()
        config = ConfigParser.ConfigParser()
        config.read(defaults_file)
        defaults = parse_user_defaults(config)
    except IOError:
        defaults = {}

    return defaults


def parse_user_defaults(config):
    """Reads default values from file

    """
    config_get = {'boolean': config.getboolean,
                  'float': config.getfloat,
                  'int': config.getint,
                  'string': config.get}
    defaults = {}
    for section in FLAGS:
        for argument in FLAGS[section]:
            try:
                value = config_get[argument['type']](section,
                                                     argument['flag'])
                defaults.update({argument['flag']: value})
            except ConfigParser.Error:
                pass
    return defaults
