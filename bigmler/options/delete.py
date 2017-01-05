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


"""Options for BigMLer delete option

"""

def get_delete_options(defaults=None):
    """Delete-related options

    """

    if defaults is None:
        defaults = {}
    options = {

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

        # Anomaly detectors selected by tag to be deleted.
        '--anomaly-tag': {
            'dest': 'anomaly_tag',
            'default': defaults.get('anomaly_tag', None),
            'help': ("Select anomaly tagged with tag to"
                     " be deleted.")},

        # Anomaly scores selected by tag to be deleted.
        '--anomaly-score-tag': {
            'dest': 'anomaly_score_tag',
            'default': defaults.get('anomaly_score_tag', None),
            'help': ("Select anomaly score tagged with tag to"
                     " be deleted.")},

        # Batch anomaly scores selected by tag to be deleted.
        '--batch-anomaly-score-tag': {
            'dest': 'batch_anomaly_score_tag',
            'default': defaults.get('batch_anomaly_score_tag', None),
            'help': ("Select batch anomaly score tagged with tag to"
                     " be deleted.")},

        # Scripts selected by tag to be deleted.
        '--script-tag': {
            'dest': 'script_tag',
            'default': defaults.get('script_tag', None),
            'help': ("Select script tagged with tag to"
                     " be deleted.")},

        # Libraries selected by tag to be deleted.
        '--library-tag': {
            'dest': 'library_tag',
            'default': defaults.get('library_tag', None),
            'help': ("Select libraries tagged with tag to"
                     " be deleted.")},

        # Execution selected by tag to be deleted.
        '--execution-tag': {
            'dest': 'execution_tag',
            'default': defaults.get('execution_tag', None),
            'help': ("Select execution tagged with tag to"
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
                     " the given number of days, date, or resource.")},

        # Use it to retrieve clusters that were tagged with tag.
        '--cluster-tag': {
            'dest': 'cluster_tag',
            'default': defaults.get('cluster_tag', None),
            'help': "Retrieve clusters that were tagged with tag."},

        # Use it to retrieve centroids that were tagged with tag.
        '--centroid-tag': {
            'dest': 'centroid_tag',
            'default': defaults.get('centroid_tag', None),
            'help': "Retrieve centroids that were tagged with tag."},

        # Use it to retrieve batch centroids that were tagged with tag.
        '--batch-centroid-tag': {
            'dest': 'batch_centroid_tag',
            'default': defaults.get('batch_centroid_tag', None),
            'help': "Retrieve batch centroids that were tagged with tag."},

        # Use it to retrieve topic models that were tagged with tag.
        '--topic-model-tag': {
            'dest': 'topic_model_tag',
            'default': defaults.get('topic_model_tag', None),
            'help': "Retrieve topic models that were tagged with tag."},

        # Use it to retrieve topic distributions that were tagged with tag.
        '--topic-distribution-tag': {
            'dest': 'topic_distribution_tag',
            'default': defaults.get('topic_distribution_tag', None),
            'help': "Retrieve topic distributions that were tagged with tag."},

        # Use it to retrieve batch topic distributions
        # that were tagged with tag.
        '--batch-topic-distribution-tag': {
            'dest': 'batch_topic_distribution_tag',
            'default': defaults.get('batch_topic_distribution_tag', None),
            'help': ("Retrieve batch topic distributions that were"
                     " tagged with tag.")},

        # Use it to retrieve batch centroids that were tagged with tag.
        '--sample-tag': {
            'dest': 'sample_tag',
            'default': defaults.get('sample_tag', None),
            'help': "Retrieve samples that were tagged with tag."},

        # Use it to limit the resources to be deleted.
        '--resource-types': {
            'dest': 'resource_types',
            'default': defaults.get('resource_types', None),
            'help': "Limits the type of resources to be deleted."},

        # Simulate the delete, storing the ids to be deleted.
        '--dry-run': {
            'action': 'store_true',
            'dest': 'dry_run',
            'default': defaults.get('dry_run', False),
            'help': "Lists the ids to be deleted, but does not delete."},

        # Don't simulate the delete.
        '--no-dry-run': {
            'action': 'store_false',
            'dest': 'dry_run',
            'default': defaults.get('dry_run', False),
            'help': "Deletes the ids retrieved to be deleted."},

        # Delete only executions but not the generated output resources
        '--execution-only': {
            'action': 'store_true',
            'dest': 'execution_only',
            'default': defaults.get('execution_only', False),
            'help': ("Deletes only executions, if present,"
                     " not generated output resources.")},

        # Retrieves the ids of the resources that have been logged in the
        # directory to add them to the delete list.
        '--from-dir': {
            'dest': 'from_dir',
            'default': defaults.get('from_dir', None),
            'help': ("Retrieves the ids of the resources logged in the "
                     "directory to add them to the delete list.")},

        # Use it to retrieve projects that were tagged with tag.
        '--project-tag': {
            'dest': 'project_tag',
            'default': defaults.get('project_tag', None),
            'help': "Retrieve projects that were tagged with tag."},

        # Use it to retrieve associations that were tagged with tag.
        '--association-tag': {
            'dest': 'association_tag',
            'default': defaults.get('association_tag', None),
            'help': "Retrieve associations that were tagged with tag."},

        # Use it to retrieve logistic regression that were tagged with tag.
        '--logistic-regression-tag': {
            'dest': 'logistic_regression_tag',
            'default': defaults.get('logistic_regression_tag', None),
            'help': "Retrieve logistic regression that were tagged with tag."},

        # Filter the resources to be deleted by its status (finished if
        # not set)
        '--status': {
            'action': 'store',
            'default': defaults.get('status', "finished"),
            'choices': ["finished", "faulty", "waiting", "queued", "started",
                        "in progress", "summarized", "uploading", "unknown",
                        "runnable"],
            'help': ("Filter the resources to be deleted by its status "
                     "(finished if not set).")}
        }

    return options
