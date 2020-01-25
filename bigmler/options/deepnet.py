# -*- coding: utf-8 -*-
#
# Copyright 2017-2020 BigML
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


"""Options for BigMLer deepnet

"""

def get_deepnet_options(defaults=None):
    """Adding arguments for the deepnet subcommand

    """

    if defaults is None:
        defaults = {}

    options = {
        # Input fields to include in the deepnet.
        '--deepnet-fields': {
            "action": 'store',
            "dest": 'deepnet_fields',
            "default": defaults.get('deepnet_fields', None),
            "help": ("Comma-separated list of input fields"
                     " (predictors) to create the deepnet.")},

        # If a BigML deepnet is provided, the script will
        # use it to generate predictions
        '--deepnet': {
            'action': 'store',
            'dest': 'deepnet',
            'default': defaults.get('deepnet', None),
            'help': "BigML deepnet Id."},

        # The path to a file containing deepnet ids.
        '--deepnets': {
            'action': 'store',
            'dest': 'deepnets',
            'default': defaults.get('deepnets', None),
            'help': ("Path to a file containing deepnets/ids."
                     " One deepnet"
                     " per line (e.g., "
                     "deepnet/50a206a8035d0706dc000376"
                     ").")},

        # If a BigML json file containing a deepnet
        # structure is provided,
        # the script will use it.
        '--deepnet-file': {
            'action': 'store',
            'dest': 'deepnet_file',
            'default': defaults.get('deepnet_file', None),
            'help': "BigML deepnet JSON structure file."},

        # The batch_normalization. Specifies whether to normalize the outputs
        # of a network before being passed to the activation function or not.
        '--batch-normalization': {
            'action': 'store_true',
            'dest': 'batch_normalization',
            'default': defaults.get('batch_normalization', None),
            'help': ("Specifies whether to normalize the outputs of"
                     " a network before being passed to the activation"
                     " function or not.")},

        # Stopping criteria for solver.
        '--default-numeric-value': {
            'action': 'store',
            'dest': 'default_numeric_value',
            'default': defaults.get('default_numeric_value', None),
            'choices': ["mean", "median", "minimum", "maximum", "zero"],
            'help': ("It accepts any of the following strings to substitute"
                     " missing numeric values across all the numeric fields"
                     " in the dataset: 'mean', 'median', 'minimum',"
                     " 'maximum', 'zero'.")},

        # dropout to control overfitting
        '--dropout-rate': {
            'action': 'store',
            'dest': 'dropout_rate',
            'type': float,
            'default': defaults.get('dropout_rate', None),
            'help': ("A number between 0 and 1 specifying the rate at "
                     "which to drop weights during training to control"
                     " overfitting")},

        # Hidden layers description
        '--hidden-layers': {
            'action': 'store',
            'dest': 'hidden_layers',
            'default': defaults.get('hidden_layers', None),
            'help': ("A JSON file that contains a list of maps describing"
                     " the number and type of layers in the network "
                     "(other than the output layer, which is determined by "
                     "the type of learning problem).")},

        # Use alternate layers for residuals
        '--learn-residuals': {
            'action': 'store_true',
            'dest': 'learn_residuals',
            'default': defaults.get('learn_residuals', None),
            'help': ("Specifies whether alternate layers should learn a"
                     " representation of the residuals for a given layer"
                     " rather than the layer itself or not.")},

        # Learning rate
        '--learning-rate': {
            'action': 'store',
            'dest': 'learning_rate',
            'type': float,
            'default': defaults.get('learning_rate', None),
            'help': ("A number between 0 and 1 specifying the"
                     " learning rate.")},

        # Max iterations
        '--max-iterations': {
            'action': 'store',
            'dest': 'max_iterations',
            'type': int,
            'default': defaults.get('max_iterations', None),
            'help': ("A number between 100 and 100000 for the maximum "
                     "number of gradient steps to take during the"
                     " optimization.")},

        # Max training time
        '--max-training-time': {
            'action': 'store',
            'dest': 'max_training_time',
            'type': int,
            'default': defaults.get('max_training_time', None),
            'help': ("The maximum wall-clock training time, in seconds, "
                     "for which to train the network. ")},

        # Number of hidden layers
        '--number-of-hidden-layers': {
            'action': 'store',
            'dest': 'number_of_hidden_layers',
            'type': int,
            'default': defaults.get('number_of_hidden_layers', None),
            'help': ("The number of hidden layers to use in the network. "
                     "If the number is greater than the length of the list"
                     " of hidden_layers, the list is cycled until the"
                     " desired number is reached. If the number is smaller"
                     " than the length of the list of hidden_layers, the"
                     " list is shortened. ")},

        # Number of model candidates
        '--number-of-model-candidates': {
            'action': 'store',
            'dest': 'number_of_model_candidates',
            'type': int,
            'default': defaults.get('number_of_model_candidates', None),
            'help': ("An  integer specifying the number of models to try "
                     "during the model search. ")},

        # use search
        '--search': {
            'action': 'store',
            'dest': 'search',
            'default': defaults.get('search', None),
            'help': ("During the deepnet creation, BigML trains and"
                     " evaluates over all possible network configurations,"
                     " returning the best networks found for the problem. "
                     "The final deepnet returned by the search is a "
                     "compromise between the top n networks found in the"
                     " search. Since this option builds several networks,"
                     " it may be significantly slower than the"
                     " suggest_structure technique.")},

        # Suggest structure
        '--suggest-structure': {
            'action': 'store_true',
            'dest': 'suggest_structure',
            'default': defaults.get('suggest_structure', None),
            'help': ("An alternative to the search technique that is "
                     "usually a more efficient way to quickly train "
                     "and iterate deepnets and it can reach similar"
                     " results. BigML has learned some general rules "
                     "about what makes one network structure better"
                     " than another for a given dataset. Given your"
                     " dataset, BigML will automatically suggest a"
                     " structure and a set of parameter values that"
                     " are likely to perform well for your dataset."
                     " This option only builds one network.")},

        # Missing numeric values are  used
        '--missing-numerics': {
            'action': 'store_true',
            'dest': 'missing_numerics',
            'default': defaults.get('missing_numerics', True),
            'help': ("Whether to create an additional binary predictor each"
                     " numeric field which denotes a missing value. If"
                     " false, these predictors are not created, and rows"
                     " containing missing numeric values are dropped. ")},

        # Missing numeric values are not used
        '--no-missing-numerics': {
            'action': 'store_false',
            'dest': 'missing_numerics',
            'default': defaults.get('missing_numerics', True),
            'help': ("Whether to create an additional binary predictor each"
                     " numeric field which denotes a missing value. If"
                     " true, these predictors are not created, and rows"
                     " containing missing numeric values are dropped. ")},

        # Suggest structure
        '--tree-embedding': {
            'action': 'store_true',
            'dest': 'tree_embedding',
            'default': defaults.get('tree_embedding', None),
            'help': ("Specify whether to learn a tree-based representation"
                     " of the data as engineered features along with the"
                     " raw features, essentially by learning trees over "
                     "slices of the input space and a small amount of "
                     "the training data. The theory is that these engineered"
                     " features will linearize obvious non-linear "
                     "dependencies before training begins, and so make "
                     "learning proceed more quickly. ")},

        # Does not balance fields
        '--no-balance-fields': {
            'action': 'store_false',
            'dest': 'balance_fields',
            'default': defaults.get('balance_fields', True),
            'help': "Do not balance fields."},

        # Does not create a deepnet just a dataset.
        '--no-deepnet': {
            'action': 'store_true',
            'dest': 'no_deepnet',
            'default': defaults.get('no_deepnet', False),
            'help': "Do not create a deepnet."},

        # The path to a file containing deepnet attributes.
        '--deepnet-attributes': {
            'action': 'store',
            'dest': 'deepnet_attributes',
            'default': defaults.get('deepnet_attributes', None),
            'help': ("Path to a json file describing deepnet"
                     " attributes.")},

        # Create a deepnet, not just a dataset.
        '--no-no-depnet': {
            'action': 'store_false',
            'dest': 'no_deepnet',
            'default': defaults.get('no_deepnet', False),
            'help': "Create a deepnet."}}

    return options
