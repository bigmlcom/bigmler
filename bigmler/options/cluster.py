# -*- coding: utf-8 -*-
#
# Copyright 2014-2016 BigML
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


"""Options for BigMLer cluster

"""

def get_cluster_options(defaults=None):
    """Adding arguments for the cluster subcommand

    """

    if defaults is None:
        defaults = {}

    options = {
        # Input fields to include in the cluster.
        '--cluster-fields': {
            "action": 'store',
            "dest": 'cluster_fields',
            "default": defaults.get('cluster_fields', None),
            "help": ("Comma-separated list of input fields"
                     " (predictors) to create the cluster.")},

        # If a BigML cluster is provided, the script will use it to generate
        # centroid predictions.
        '--cluster': {
            'action': 'store',
            'dest': 'cluster',
            'default': defaults.get('cluster', None),
            'help': "BigML cluster Id."},

        # The path to a file containing cluster ids.
        '--clusters': {
            'action': 'store',
            'dest': 'clusters',
            'default': defaults.get('clusters', None),
            'help': ("Path to a file containing cluster/ids. One cluster"
                     " per line (e.g., cluster/50a206a8035d0706dc000376"
                     ").")},

        # If a BigML json file containing a cluster structure is provided,
        # the script will use it.
        '--cluster-file': {
            'action': 'store',
            'dest': 'cluster_file',
            'default': defaults.get('cluster_file', None),
            'help': "BigML cluster JSON structure file."},

        # Number of centroids to be generated in the cluster
        '--k': {
            'action': 'store',
            'type': int,
            'dest': 'cluster_k',
            'default': defaults.get('cluster_k', None),
            'help': "Number of centroids to be generated in the cluster."},

        # Does not create a cluster just a dataset.
        '--no-cluster': {
            'action': 'store_true',
            'dest': 'no_cluster',
            'default': defaults.get('no_cluster', False),
            'help': "Do not create a cluster."},

        # The path to a file containing cluster attributes.
        '--cluster-attributes': {
            'action': 'store',
            'dest': 'cluster_attributes',
            'default': defaults.get('cluster_attributes', None),
            'help': ("Path to a json file describing cluster"
                     " attributes.")},

        # Create a cluster, not just a dataset.
        '--no-no-cluster': {
            'action': 'store_false',
            'dest': 'no_cluster',
            'default': defaults.get('no_cluster', False),
            'help': "Create a cluster."},

        # Comma separated list of datasets to be generated from the cluster.
        '--cluster-datasets': {
            'action': 'store',
            'dest': 'cluster_datasets',
            'nargs': '?',
            'const': '',
            'default': defaults.get('cluster_datasets', None),
            'help': ("Comma-separated list of centroid names. The"
                     " related datasets will be generated. All datasets "
                     "will be generated if empty.")},

        # The seed to be used in cluster building.
        '--cluster-seed': {
            'action': 'store',
            'dest': 'cluster_seed',
            'default': defaults.get('cluster_seed', None),
            'help': "The seed to be used in cluster building."},

        # The path to a file containing batch prediction attributes.
        '--batch-centroid-attributes': {
            'action': 'store',
            'dest': 'batch_centroid_attributes',
            'default': defaults.get('batch_centroid_attributes', None),
            'help': ("Path to a json file describing batch centroid"
                     " attributes.")},

        # The path to a file containing centroid attributes.
        '--centroid-attributes': {
            'action': 'store',
            'dest': 'centroid_attributes',
            'default': defaults.get('centroid_attributes', None),
            'help': ("Path to a json file describing centroid"
                     " attributes.")},

        # Comma separated list of models to be generated from the cluster.
        '--cluster-models': {
            'action': 'store',
            'dest': 'cluster_models',
            'nargs': '?',
            'const': '',
            'default': defaults.get('cluster_models', None),
            'help': ("Comma-separated list of centroid names. The"
                     " related models will be generated. All models "
                     "will be generated if empty.")},

        # Comma separated list of summary fields
        '--summary-fields': {
            'action': 'store',
            'dest': 'summary_fields',
            'default': defaults.get('summary_fields', None),
            'help': ("Comma-separated list of summary fields, that will be"
                     " included in the generated datasets but not used in"
                     " clustering.")}}

    return options
