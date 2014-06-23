# -*- coding: utf-8 -*-
#
# Copyright 2014 BigML
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


"""Options for BigMLer delete option

"""

def get_delete_options(defaults={}, constants={}):
    """Delete-related options

    """

    options = {
        # Changes to delete mode.
        '--delete': {
            'action': 'store_true',
            'help': "Delete command."},

        # Resources to be deleted.
        '--ids': {
            'action': 'store',
            'dest': 'delete_list',
            'help': ("Select comma-separated list of"
                     " resources to be deleted.")},

        # Resources to be deleted are taken from file.
        '--from-file': {
            'action': 'store',
            'dest': 'delete_file',
            'default': defaults.get('from_file', None),
            'help': ("Path to a file containing resources ids."
                     " One resource per line"
                     " (e.g., model/50a206a8035d0706dc000376).")},

        # Sources selected by tag to be deleted.
        '--source-tag': {
            'dest': 'source_tag',
            'default': defaults.get('source_tag', None),
            'help': ("Select sources tagged with tag to"
                     " be deleted")},

        # Datasets selected by tag to be deleted.
        '--dataset-tag': {
            'dest': 'dataset_tag',
            'default': defaults.get('dataset_tag', None),
            'help': ("Select datasets tagged with tag to"
                     " be deleted")},
        # Use it to retrieve models that were tagged with tag.
        '--model-tag': {
            'dest': 'model_tag',
            'default': defaults.get('model_tag', None),
            'help': "Retrieve models that were tagged with tag."},

        # Predictions selected by tag to be deleted.
        '--prediction-tag': {
            'dest': 'prediction_tag',
            'default': defaults.get('prediction_tag', None),
            'help': ("Select prediction tagged with tag to"
                     " be deleted.")},

        # Evaluations selected by tag to be deleted.
        '--evaluation-tag': {
            'dest': 'evaluation_tag',
            'default': defaults.get('evaluation_tag', None),
            'help': ("Select evaluation tagged with tag to"
                  " be deleted.")},

        # Ensembles selected by tag to be deleted.
        '--ensemble-tag': {
            'dest': 'ensemble_tag',
            'default': defaults.get('ensemble_tag', None),
            'help': ("Select ensemble tagged with tag to"
                     " be deleted.")},

        # Batch predictions selected by tag to be deleted.
        '--batch-prediction-tag': {
            'dest': 'batch_prediction_tag',
            'default': defaults.get('batch_prediction_tag', None),
            'help': ("Select batch prediction tagged with tag to"
                     " be deleted.")},

        # Resources selected by tag to be deleted.
        '--all-tag': {
            'dest': 'all_tag',
            'default': defaults.get('all_tag', None),
            'help': ("Select resources tagged with tag to"
                     " be deleted.")},
        # Condition to select resources for deletion: olther than.
        '--older-than': {
            'action': 'store',
            'dest': 'older_than',
            'default': defaults.get('older_than', None),
            'help': ("Upper limit to select the resources older than"
                     " the given number of days, date, or resource.")},

        # Condition to select resources for deletion: newer than.
        '--newer-than': {
            'action': 'store',
            'dest': 'newer_than',
            'default': defaults.get('newer_than', None),
            'help': ("Lower limit to select the resources newer than"
                     " the given number of days, date, or resource.")}}

    return options
