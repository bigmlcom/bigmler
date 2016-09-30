# -*- coding: utf-8 -*-
#
# Copyright 2012-2016 BigML
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

FLAGS = {
    'BigMLer': [
        {'flag': 'debug', 'type': 'boolean'},
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
        {'flag': 'model_file', 'type': 'string'},
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
        {'flag': 'ensemble_file', 'type': 'string'},
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
        {'flag': 'ensembles', 'type': 'string'},
        {'flag': 'threshold', 'type': 'int'},
        {'flag': 'threshold_class', 'type': 'string'},
        {'flag': 'max_categories', 'type': 'int'},
        {'flag': 'test_field_attributes', 'type': 'string'},
        {'flag': 'test_types', 'type': 'string'},
        {'flag': 'test_source', 'type': 'string'},
        {'flag': 'test_dataset', 'type': 'string'},
        {'flag': 'no_batch', 'type': 'boolean'},
        {'flag': 'dataset_attributes', 'type': 'string'},
        {'flag': 'output', 'type': 'string'},
        {'flag': 'new_fields', 'type': 'string'},
        {'flag': 'model_attributes', 'type': 'string'},
        {'flag': 'node_threshold', 'type': 'int'},
        {'flag': 'multi_label_fields', 'type': 'string'},
        {'flag': 'ensemble_attributes', 'type': 'string'},
        {'flag': 'source_attributes', 'type': 'string'},
        {'flag': 'evaluation_attributes', 'type': 'string'},
        {'flag': 'batch_prediction_attributes', 'type': 'string'},
        {'flag': 'batch_prediction_tag', 'type': 'string'},
        {'flag': 'balance', 'type': 'boolean'},
        {'flag': 'weight_field', 'type': 'string'},
        {'flag': 'objective_weights', 'type': 'string'},
        {'flag': 'label_aggregates', 'type': 'string'},
        {'flag': 'missing_strategy', 'type': 'string'},
        {'flag': 'other_than', 'type': 'string'},
        {'flag': 'newer_than', 'type': 'string'},
        {'flag': 'multi_dataset', 'type': 'boolean'},
        {'flag': 'multi_dataset_attributes', 'type': 'string'},
        {'flag': 'shared', 'type': 'boolean'},
        {'flag': 'reports', 'type': 'string'},
        {'flag': 'upload', 'type': 'boolean'},
        {'flag': 'test_dataset', 'type': 'string'},
        {'flag': 'dataset_off', 'type': 'boolean'},
        {'flag': 'args_separator', 'type': 'string'},
        {'flag': 'cluster_tag', 'type': 'string'},
        {'flag': 'centroid_tag', 'type': 'string'},
        {'flag': 'batch_centroid_tag', 'type': 'string'},
        {'flag': 'to_csv', 'type': 'string'},
        {'flag': 'resource_types', 'type': 'string'},
        {'flag': 'dry_run', 'type': 'boolean'},
        {'flag': 'anomaly_tag', 'type': 'string'},
        {'flag': 'anomaly_score_tag', 'type': 'string'},
        {'flag': 'project_tag', 'type': 'string'},
        {'flag': 'fast', 'type': 'boolean'},
        {'flag': 'project', 'type': 'string'},
        {'flag': 'project_id', 'type': 'string'},
        {'flag': 'no_csv', 'type': 'boolean'},
        {'flag': 'to_dataset', 'type': 'boolean'},
        {'flag': 'median', 'type': 'boolean'},
        {'flag': 'random_candidates', 'type': 'int'},
        {'flag': 'status', 'type': 'string'},
        {'flag': 'export_fields', 'type': 'string'},
        {'flag': 'import_fields', 'type': 'string'},
        {'flag': 'only_execution', 'type': 'boolean'},
        {'flag': 'ensemble_sample_seed', 'type': 'string'},
        {'flag': 'ensemble_sample_rate', 'type': 'float'},
        {'flag': 'ensemble_sample_replacement', 'type': 'boolean'}],
    'BigMLer analyze': [
        {'flag': 'k-fold', 'type': 'int'},
        {'flag': 'cv', 'type': 'boolean'},
        {'flag': 'features', 'type': 'boolean'},
        {'flag': 'maximize', 'type': 'string'},
        {'flag': 'optimize', 'type': 'string'},
        {'flag': 'nodes', 'type': 'boolean'},
        {'flag': 'max_nodes', 'type': 'int'},
        {'flag': 'min_nodes', 'type': 'int'},
        {'flag': 'nodes_step', 'type': 'int'},
        {'flag': 'random_fields', 'type': 'boolean'},
        {'flag': 'exclude_features', 'type': 'string'},
        {'flag': 'optimize_category', 'type': 'string'},
        {'flag': 'predictions_csv', 'type': 'boolean'}],
    'BigMLer cluster': [
        {'flag': 'cluster_fields', 'type': 'string'},
        {'flag': 'cluster', 'type': 'string'},
        {'flag': 'cluster_file', 'type': 'string'},
        {'flag': 'clusters', 'type': 'string'},
        {'flag': 'k', 'type': 'int'},
        {'flag': 'no_cluster', 'type': 'boolean'},
        {'flag': 'cluster_attributes', 'type': 'string'},
        {'flag': 'centroid_attributes', 'type': 'string'},
        {'flag': 'batch_centroid_attributes', 'type': 'string'},
        {'flag': 'cluster_datasets', 'type': 'string'},
        {'flag': 'cluster_models', 'type': 'string'},
        {'flag': 'summary_fields', 'type': 'string'}],
    'BigMLer anomaly': [
        {'flag': 'anomaly_fields', 'type': 'string'},
        {'flag': 'anomaly', 'type': 'string'},
        {'flag': 'anomaly_file', 'type': 'string'},
        {'flag': 'anomalies', 'type': 'string'},
        {'flag': 'no_anomaly', 'type': 'boolean'},
        {'flag': 'anomaly_attributes', 'type': 'string'},
        {'flag': 'anomaly_score_attributes', 'type': 'string'},
        {'flag': 'batch_anomaly_score_attributes', 'type': 'string'},
        {'flag': 'score', 'type': 'boolean'},
        {'flag': 'anomalies-dataset', 'type': 'string'},
        {'flag': 'top_n', 'type': 'int'},
        {'flag': 'forest_size', 'type': 'int'}],
    'BigMLer sample': [
        {'flag': 'anomaly_fields', 'type': 'string'},
        {'flag': 'sample', 'type': 'string'},
        {'flag': 'sample_file', 'type': 'string'},
        {'flag': 'samples', 'type': 'string'},
        {'flag': 'no_sample', 'type': 'boolean'},
        {'flag': 'sample_attributes', 'type': 'string'},
        {'flag': 'sample_header', 'type': 'boolean'},
        {'flag': 'fields_filter', 'type': 'string'},
        {'flag': 'row_index', 'type': 'int'},
        {'flag': 'mode', 'type': 'string'},
        {'flag': 'occurrence', 'type': 'int'},
        {'flag': 'precision', 'type': 'int'},
        {'flag': 'rows', 'type': 'int'},
        {'flag': 'row_offset', 'type': 'int'},
        {'flag': 'row_order_by', 'type': 'string'},
        {'flag': 'row_fields', 'type': 'string'},
        {'flag': 'stat_fields', 'type': 'string'},
        {'flag': 'stat_field', 'type': 'string'},
        {'flag': 'unique', 'type': 'boolean'}],
    'BigMLer report': [
        {'flag': 'from_dir', 'type': 'string'},
        {'flag': 'port', 'type': 'int'},
        {'flag': 'no_server', 'type': 'boolean'}],
    'BigMLer reify': [
        {'flag': 'language', 'type': 'string'},
        {'flag': 'add_fields', 'type': 'boolean'}],
    'BigMLer project': [
        {'flag': 'project_attributes', 'type': 'string'}],
    'BigMLer association': [
        {'flag': 'association_fields', 'type': 'string'},
        {'flag': 'association', 'type': 'string'},
        {'flag': 'association_file', 'type': 'string'},
        {'flag': 'associations', 'type': 'string'},
        {'flag': 'association_k', 'type': 'int'},
        {'flag': 'no_association', 'type': 'boolean'},
        {'flag': 'association_attributes', 'type': 'string'}],
    'BigMLer logistic regression': [
        {'flag': 'logistic_fields', 'type': 'string'},
        {'flag': 'logistic_regression', 'type': 'string'},
        {'flag': 'logistic_regression_file', 'type': 'string'},
        {'flag': 'logistic_regressions', 'type': 'string'},
        {'flag': 'no_logistic_regression', 'type': 'boolean'},
        {'flag': 'logistic_regression_attributes', 'type': 'string'},
        {'flag': 'bias', 'type': 'boolean'},
        {'flag': 'balance_fields', 'type': 'boolean'},
        {'flag': 'lr_c', 'type': 'float'},
        {'flag': 'eps', 'type': 'float'},
        {'flag': 'field_codings', 'type': 'string'},
        {'flag': 'missing_numerics', 'type': 'boolean'},
        {'flag': 'normalize', 'type': 'boolean'}],
    'BigMLer execute': [
        {'flag': 'script', 'type': 'string'},
        {'flag': 'library', 'type': 'string'},
        {'flag': 'execution', 'type': 'string'},
        {'flag': 'code_file', 'type': 'string'},
        {'flag': 'output', 'type': 'string'},
        {'flag': 'imports', 'type': 'string'},
        {'flag': 'inputs', 'type': 'string'},
        {'flag': 'declare_inputs', 'type': 'string'},
        {'flag': 'declare_outputs', 'type': 'string'},
        {'flag': 'input_maps', 'type': 'string'},
        {'flag': 'outputs', 'type': 'string'},
        {'flag': 'creation_defaults', 'type': 'string'},
        {'flag': 'no_execute', 'type': 'boolean'}],
    'BigMLer whizzml': [
        {'flag': 'package_dir', 'type': 'string'}]}


def get_user_defaults(defaults_file=DEFAULTS_FILE):
    """Looks for a defaults file and returns its contents

    """
    if defaults_file is None:
        defaults_file = DEFAULTS_FILE
    try:
        open(defaults_file).close()
        config = ConfigParser.ConfigParser()
        config.read(defaults_file)
        defaults = parse_user_defaults(config)
    except IOError:
        defaults = {}
        for section in FLAGS:
            defaults[section] = {}
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
        defaults[section] = {}
        for argument in FLAGS[section]:
            try:
                value = config_get[argument['type']](section,
                                                     argument['flag'])
                defaults[section].update({argument['flag']: value})
            except ConfigParser.Error:
                pass
    return defaults
