# -*- coding: utf-8 -*-
#
# Copyright 2016-2017 BigML
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


"""Options for BigMLer topic model

"""

def get_topic_model_options(defaults=None):
    """Adding arguments for the topic model subcommand

    """

    if defaults is None:
        defaults = {}

    options = {
        # Input fields to include in the topic model.
        '--topic-fields': {
            "action": 'store',
            "dest": 'topic_fields',
            "default": defaults.get('topic_fields', None),
            "help": ("Comma-separated list of input fields"
                     " (predictors) to create the topic model.")},

        # If a BigML topic model is provided, the script will
        # use it to generate predictions
        '--topic-model': {
            'action': 'store',
            'dest': 'topic_model',
            'default': defaults.get('topic_model', None),
            'help': "BigML topic model Id."},

        # The path to a file containing topic model ids.
        '--topic-models': {
            'action': 'store',
            'dest': 'topic_models',
            'default': defaults.get('topic_models', None),
            'help': ("Path to a file containing topicmodel/ids."
                     " One topicmodel"
                     " per line (e.g., "
                     "topicmodel/50a206a8035d0706dc000376"
                     ").")},

        # If a BigML json file containing a topic model
        # structure is provided,
        # the script will use it.
        '--topic-model-file': {
            'action': 'store',
            'dest': 'topic_model_file',
            'default': defaults.get('topic_model_file', None),
            'help': "BigML topic model JSON structure file."},

        # Whether to include a contiguous sequence of two items from a given
        # sequence of text
        '--bigrams': {
            "action": 'store_true',
            "dest": 'bigrams',
            "default": defaults.get('bigrams', False),
            "help": ("Whether to include a contiguous sequence of two items"
                     " from a given sequence of text.")},

        # Whether the analysis is case-sensitive or not.
        '--case-sensitive': {
            "action": 'store_true',
            "dest": 'case_sensitive',
            "default": defaults.get('case_sensitive', False),
            "help": "Whether the analysis is case-sensitive or not."},

        # Comma separated list of tems to be excluded from term analysis.
        '--excluded-terms': {
            'action': 'store',
            'dest': 'excluded_terms',
            'default': defaults.get('excluded_terms', None),
            'help': ("Comma-separated list of terms to be excluded from "
                     "text analysis.")},

        # Number of topics to be generated
        '--number-of-topics': {
            'action': 'store',
            'dest': 'number_of_topics',
            'type': int,
            'default': defaults.get('number_of_topics', None),
            'help': ("Number of topics to be generated for the model.")},

        # The maximum number of terms used for the topic model vocabulary
        '--term-limit': {
            'action': 'store',
            'dest': 'term_limit',
            'type': int,
            'default': defaults.get('term_limit', 4096),
            'help': ("The maximum number of terms used for the topic"
                     " model vocabulary.")},

        # The size of the most influential terms recorded.
        '--top-n-terms': {
            'action': 'store',
            'dest': 'top_n_terms',
            'type': int,
            'default': defaults.get('top_n_terms', 10),
            'help': "The size of the most influential terms recorded."},

        # Whether to use stop words.
        '--use-stopwords': {
            "action": 'store_true',
            "dest": 'use_stopwords',
            "default": defaults.get('use_stopwords', False),
            "help": "Whether to use stop words."},

        # Does not create a topic model just a dataset.
        '--no-topic-model': {
            'action': 'store_true',
            'dest': 'no_topic_model',
            'default': defaults.get('no_topic_model', False),
            'help': "Do not create a topic model."},

        # Create a topic model, not just a dataset.
        '--no-no-topic-model': {
            'action': 'store_false',
            'dest': 'no_topic_model',
            'default': defaults.get('no_topic_model', False),
            'help': "Create a topic model."},

        # The path to a file containing topic model attributes.
        '--topic-model-attributes': {
            'action': 'store',
            'dest': 'topic_model_attributes',
            'default': defaults.get('topic_model_attributes', None),
            'help': ("Path to a json file describing topic model"
                     " attributes.")}}

    return options
