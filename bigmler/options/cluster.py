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


"""Options for BigMLer cluster

"""

def get_cluster_options(defaults=None):
    """Adding arguments for the analyze subcommand

    """

    if defaults is None:
        defaults = {}

    options = {
        # Make cluster public.
        '--public-cluster': {
            'action': 'store_true',
            'dest': 'public_dataset',
            'default': defaults.get('public_dataset', False),
            'help': "Make generated dataset public."},

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

        # Set a price tag to your public cluster.
        '--cluster-price': {
            'action': 'store',
            'dest': 'cluster_price',
            'type': float,
            'default': defaults.get('cluster_price', 0.0),
            'help': ("The price other users must pay to clone your"
                     " cluster.")},

        # Does not create a cluster just a dataset.
        '--no-cluster': {
            'action': 'store_true',
            'dest': 'no_cluster',
            'default': defaults.get('no_cluster', False),
            'help': "Do not create a cluster."},

        # Max number of clusters to create in parallel.
        '--max-parallel-clusters': {
            "action": 'store',
            "dest": 'max_parallel_clusters',
            "default": defaults.get('max_parallel_clusters', 1),
            "type": int,
            "help": "Max number of clusters to create in parallel."},

        # The path to a file containing cluster attributes.
        '--cluster-attributes': {
            'action': 'store',
            'dest': 'cluster_attributes',
            'default': defaults.get('cluster_attributes', None),
            'help': ("Path to a json file describing cluster"
                     " attributes.")},

        # Doesn't make model a public cluster.
        '--no-public-cluster': {
            'action': 'store_false',
            'dest': 'public_cluster',
            'default': defaults.get('public_cluster', False),
            'help': "Doesn't make generated cluster public."},

        # Create a cluster, not just a dataset.
        '--no-no-cluster': {
            'action': 'store_false',
            'dest': 'no_cluster',
            'default': defaults.get('no_cluster', False),
            'help': "Create a cluster."}}

    return options
