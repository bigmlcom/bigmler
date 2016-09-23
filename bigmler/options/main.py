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


"""Options for BigMLer main subcommand processing

"""

def get_main_options(defaults=None, constants=None):
    """Main subcommand-related options

    """

    if defaults is None:
        defaults = {}
    if constants is None:
        constants = {}
    max_models = constants.get('MAX_MODELS')
    plurality = constants.get('PLURALITY')
    last = constants.get('LAST_PREDICTION')

    options = {
        # If a BigML model is provided, the script will use it to generate
        # predictions.
        '--model': {
            'action': 'store',
            'dest': 'model',
            'default': defaults.get('model', None),
            'help': "BigML model Id."},

        # Use it to compute predictions remotely.
        '--remote': {
            'action': 'store_true',
            'dest': 'remote',
            'default': defaults.get('remote', False),
            'help': "Compute predictions remotely."},

        # The path to a file containing model ids.
        '--models': {
            'action': 'store',
            'dest': 'models',
            'default': defaults.get('models', None),
            'help': ("Path to a file containing model/ids. One model"
                     " per line (e.g., model/50a206a8035d0706dc000376"
                     ").")},

        # If a BigML json file containing a model structure is provided,
        # the script will use it.
        '--model-file': {
            'action': 'store',
            'dest': 'model_file',
            'default': defaults.get('model_file', None),
            'help': "BigML model JSON structure file."},

        # Sets pruning.
        '--pruning': {
            'action': 'store',
            'default': defaults.get('pruning', "smart"),
            'choices': ["smart", "statistical", "no-pruning"],
            'help': ("Set pruning type: smart, statistical,"
                     " no-pruning.")},

        # Number of models to create when using ensembles.
        '--number-of-models': {
            'action': 'store',
            'dest': 'number_of_models',
            'default': defaults.get('number_of_models', 1),
            'type': int,
            'help': ("Number of models to create when using"
                     " ensembles.")},

        # Replacement to use when sampling.
        '--replacement': {
            'action': 'store_true',
            'default': defaults.get('replacement', False),
            'help': "Use replacement when sampling."},

        # Max number of models to predict from in parallel.
        '--max-batch-models': {
            'action': 'store',
            'dest': 'max_batch_models',
            'default': defaults.get('max_batch_models', max_models),
            'type': int,
            'help': ("Max number of models to predict from"
                     " in parallel.")},

        # Randomize feature selection at each split.
        '--randomize': {
            'action': 'store_true',
            'dest': 'randomize',
            'default': defaults.get('randomize', False),
            'help': "Randomize feature selection at each split."},

        # Make model a public black-box model.
        '--black-box': {
            'action': 'store_true',
            'dest': 'black_box',
            'default': defaults.get('black_box', False),
            'help': "Make generated model black-box."},

        # Make model a public white-box model.
        '--white-box': {
            'action': 'store_true',
            'dest': 'white_box',
            'default': defaults.get('white_box', False),
            'help': "Make generated model white-box."},

        # Set a price tag to your white-box model.
        '--model-price': {
            'action': 'store',
            'dest': 'model_price',
            'type': float,
            'default': defaults.get('model_price', 0.0),
            'help': ("The price other users must pay to clone your"
                     " model.")},

        # Set credits per prediction to your white box or black box models.
        '--cpp': {
            'action': 'store',
            'type': float,
            'default': defaults.get('cpp', 0.0),
            'help': ("The number of credits that other users will"
                     " consume to make a prediction with your"
                     " model.")},

        # Does not create a model just a dataset.
        '--no-model': {
            'action': 'store_true',
            'dest': 'no_model',
            'default': defaults.get('no_model', False),
            'help': "Do not create a model."},

        # Prediction directories to be combined.
        '--combine-votes': {
            'action': 'store',
            'dest': 'votes_dirs',
            'default': defaults.get('combine_votes', None),
            'help': ("Comma separated list of"
                     " directories that contain models' votes"
                     " for the same test set.")},

        # Method to combine votes in multiple models predictions
        '--method': {
            'action': 'store',
            'dest': 'method',
            'default': defaults.get('method', plurality),
            'choices': ["plurality", "confidence weighted",
                        "probability weighted", "threshold",
                        "combined"],
            'help': ("Method to combine votes from ensemble"
                     " predictions. Allowed methods: plurality"
                     ", \"confidence weighted\", "
                     " \"probability weighted\", threshold. Also"
                     " \"combined\" for datasets with subsets of"
                     " categories")},

        # Evaluate a model
        '--evaluate': {
            'action': 'store_true',
            'help': "Evaluate command."},

        # Max number of models to create in parallel.
        '--max-parallel-models': {
            "action": 'store',
            "dest": 'max_parallel_models',
            "default": defaults.get('max_parallel_models', 1),
            "type": int,
            "help": "Max number of models to create in parallel."},

        # Max number of evaluations to create in parallel.
        '--max-parallel-evaluations': {
            "action": 'store',
            "dest": 'max_parallel_evaluations',
            "default": defaults.get('max_parallel_evaluations', 1),
            "type": int,
            "help": ("Max number of evaluations to create in"
                     " parallel.")},

        # The name of the field that represents the objective field (i.e.,
        # class or label) or its column number.
        '--objective': {
            "action": 'store',
            "dest": 'objective_field',
            "default": defaults.get('objective', None),
            "help": ("The column number of the Objective Field"
                     " or its name, if headers are given.")},

        # The path to a file containing the mapping of fields' ids from
        # the test dataset fields to the model fields.
        '--fields-map': {
            'action': 'store',
            'dest': 'fields_map',
            'default': defaults.get('fields_map', None),
            'help': ("Path to a csv file describing fields mapping. "
                     "One definition per line (e.g., 00000,"
                     "00000a).")},

        # Set the part of training data to be held out for cross-validation
        '--cross-validation-rate': {
            'action': 'store',
            'dest': 'cross_validation_rate',
            'type': float,
            'default': defaults.get('cross_validation_rate', 0.0),
            'help': ("Part of training data to be held out for "
                     "cross-validation.")},

        # Number of evaluations used in cross-validation
        '--number-of-evaluations': {
            'action': 'store',
            'dest': 'number_of_evaluations',
            'type': int,
            'default': defaults.get('number_of_evaluations', 0),
            'help': ("Number of evaluations used for"
                     " cross-validation.")},

        # If a BigML ensemble is provided, the script will use it to generate
        # predictions.
        '--ensemble': {
            'action': 'store',
            'dest': 'ensemble',
            'default': defaults.get('ensemble', None),
            'help': "BigML ensemble Id."},

        # If a BigML ensemble is created, creation will use this task-level
        # parallelism
        '--tlp': {
            'action': 'store',
            'dest': 'tlp',
            'default': defaults.get('tlp', 1),
            'type': int,
            'help': ("BigML ensemble's creation task-level"
                     " parallelism.")},

        # Prediction log format: `short` will only log predictions, `long` will
        # log also confidence information
        '--prediction-info': {
            'action': 'store',
            'dest': 'prediction_info',
            'default': defaults.get('prediction_info', 'normal'),
            'choices': ["brief", "normal", "full", "full data"],
            'help': ("Prediction log format: 'brief' will only "
                     "log predictions, 'normal' will write confidence"
                     " too, 'full' will write in a row the"
                     " input data that generates the prediction"
                     " followed by the latter.")},

        # Multi-label. The objective field has multiple labels.
        '--multi-label': {
            'action': 'store_true',
            'dest': 'multi_label',
            'default': defaults.get('multi_label', False),
            'help': ("The objective field has multiple labels that"
                     " should be treated independently.")},

        # Prediction header. If set, headers are added to the prediction file.
        '--prediction-header': {
            'action': 'store_true',
            'dest': 'prediction_header',
            'default': defaults.get('prediction_header', False),
            'help': "Headers are added to the prediction file."},

        # Prediction fields. A comma-separated list of the fields that should
        # be included in the prediction file.
        '--prediction-fields': {
            'action': 'store',
            'dest': 'prediction_fields',
            'default': defaults.get('prediction_fields', None),
            'help': "Fields added to the prediction file."},

        # Max number of ensembles to create in parallel.
        '--max-parallel-ensembles': {
            'action': 'store',
            'dest': 'max_parallel_ensembles',
            'default': defaults.get('max_parallel_ensembles', 1),
            'type': int,
            'help': "Max number of ensembles to create in parallel."},

        # The path to a file containing ensemble ids.
        '--ensembles': {
            'action': 'store',
            'dest': 'ensembles',
            'default': defaults.get('ensembles', None),
            'help': ("Path to a file containing ensemble/ids. One "
                     "ensemble per line (e.g., "
                     "ensemble/50a206a8035d0706dc000376).")},

        # If a BigML json file containing a model structure is provided,
        # the script will use it.
        '--ensemble-file': {
            'action': 'store',
            'dest': 'ensemble_file',
            'default': defaults.get('ensemble_file', None),
            'help': "BigML ensemble JSON structure file."},

        # Threshold. Minimum necessary number of votes to issue a prediction.
        '--threshold': {
            'action': 'store',
            'dest': 'threshold',
            'default': defaults.get('threshold', 1),
            'type': int,
            'help': ("Minimum number of votes to issue a prediction"
                     " for the threshold combiner.")},

        # Class. Label for the category used in threshold voting predictions.
        '--class': {
            'action': 'store',
            'dest': 'threshold_class',
            'default': defaults.get('threshold_class', None),
            'help': "Category used in threshold combiner method."},

        # Max number of categories to be included in a model
        '--max-categories': {
            'action': 'store',
            'dest': 'max_categories',
            'default': defaults.get('max_categories', 0),
            'type': int,
            'help': ("Max number of categories to be included in"
                     " a model.")},

        # No batch predictions. Remote predictions are created individually.
        '--no-batch': {
            'action': 'store_true',
            'dest': 'no_batch',
            'default': defaults.get('no_batch', False),
            'help': "Create remote predictions individually."},

        # Evaluations flag: excluding one dataset from the datasets list to
        # test
        '--dataset-off': {
            'action': 'store_true',
            'dest': 'dataset_off',
            'default': defaults.get('dataset_off', False),
            'help': ("Excluding one dataset at a time from the"
                     " datasets list to test.")},

        # The path to a file containing model attributes.
        '--model-attributes': {
            'action': 'store',
            'dest': 'model_attributes',
            'default': defaults.get('model_attributes', None),
            'help': ("Path to a json file describing model"
                     " attributes.")},

        # Input fields to include in the model.
        '--model-fields': {
            "action": 'store',
            "dest": 'model_fields',
            "default": defaults.get('model_fields', None),
            "help": ("Comma-separated list of input fields"
                     " (predictors) to create the model.")},

        # Balance. Automatically balance all the classes evenly.
        '--balance': {
            "action": 'store_true',
            "dest": 'balance',
            "default": defaults.get('balance', False),
            "help": ("Automatically balance all objective classes"
                     " evenly.")},

        # Balance. Do not automatically balance all the classes evenly.
        # (opposed to balance)
        '--no-balance': {
            "action": 'store_false',
            "dest": 'balance',
            "default": defaults.get('balance', False),
            "help": ("Do not automatically balance all objective"
                     " classes evenly.")},

        # Node threshold. Maximum number of nodes in the tree.
        '--node-threshold': {
            'action': 'store',
            'dest': 'node_threshold',
            'default': defaults.get('node_threshold', 0),
            'type': int,
            'help': "Maximum number of nodes in the model."},

        # The path to a file containing ensemble attributes.
        '--ensemble-attributes': {
            'action': 'store',
            'dest': 'ensemble_attributes',
            'default': defaults.get('ensemble_attributes', None),
            'help': ("Path to a json file describing ensemble"
                     " attributes.")},

        # The path to a file containing evaluation attributes.
        '--evaluation-attributes': {
            'action': 'store',
            'dest': 'evaluation_attributes',
            'default': defaults.get('evaluation_attributes', None),
            'help': ("Path to a json file describing evaluation"
                     " attributes.")},

        # The path to a file containing batch prediction attributes.
        '--batch-prediction-attributes': {
            'action': 'store',
            'dest': 'batch_prediction_attributes',
            'default': defaults.get('batch_prediction_attributes', None),
            'help': ("Path to a json file describing batch prediction"
                     " attributes.")},

        # Weight-field. Use the contents of the given field as weights.
        '--weight-field': {
            'action': 'store',
            'dest': 'weight_field',
            'default': defaults.get('weight_field', None),
            'help': ("Sets the name (or column) of the field"
                     " that contains the weights for the instances.")},

        # Objective-weights. Path a to a CSV file of class, weight pairs.
        '--objective-weights': {
            'action': 'store',
            'dest': 'objective_weights',
            'default': defaults.get('objective_weights', None),
            'help': "Path to a CSV file of class, weight pairs."},

        # Strategy used in predictions when a missing value is found for the
        # field used to split the node.
        '--missing-strategy': {
            'action': 'store',
            'dest': 'missing_strategy',
            'default': defaults.get('missing_strategy', last),
            'choices': ["last", "proportional"],
            'help': ("Strategy used when the field used in the split"
                     " to next nodes is missing in the input data."
                     " Allowed values: last or proportional")},

        # Report. Additional output report formats
        '--reports': {
            'action': 'store',
            'dest': 'reports',
            'nargs': '*',
            'default': defaults.get('reports', []),
            'choices': ["gazibit"],
            'help': "Output report formats."},

        # Set it to use the missing splits operators: including missing values
        # in tree branches.
        '--missing-splits': {
            'action': 'store_true',
            'dest': 'missing_splits',
            'default': defaults.get('missing_splits', False),
            'help': ("Accept missing values as valid in some branches of the"
                     "tree.")},

        # Random candidates: Number of fields to be selected at random in
        # ensembles construction
        '--random-candidates': {
            'action': 'store',
            'dest': 'random_candidates',
            'default': defaults.get('random_candidates', 0),
            'type': int,
            'help': ("Number of fields selected at random in ensembles'"
                     " construction.")},

        # Ensemble seed. The value used in ensembles as seed
        '--ensemble-sample-seed': {
            'action': 'store',
            'dest': 'ensemble_sample_seed',
            'default': defaults.get('ensemble_sample_seed', None),
            'help': "Value used as seed in ensembles."},

        # Ensemble sampling to use when using bagging.
        '--ensemble-sample-rate': {
            'action': 'store',
            'dest': 'ensemble_sample_rate',
            'default': defaults.get('ensemble_sample_rate', 1.0),
            'type': float,
            'help': "Ensemble sampling rate for bagging."},

        # Ensemble replacement to use when using bagging.
        '--ensemble-sample-no-replacement': {
            'action': 'store_false',
            'dest': 'ensemble_sample_replacement',
            'default': defaults.get('ensemble_sample_replacement', True),
            'help': "Don't use replacement when bagging."},

        # Disables reports upload.
        '--no-upload': {
            'action': 'store_false',
            'dest': 'upload',
            'default': defaults.get('upload', True),
            'help': "Disables upload for reports"},

        # Use it to compute predictions locally.
        '--local': {
            'action': 'store_false',
            'dest': 'remote',
            'default': defaults.get('remote', False),
            'help': "Compute predictions locally"},

        # Deactivate replacement to use when using sampling.
        '--no-replacement': {
            'action': 'store_false',
            'dest': 'replacement',
            'default': defaults.get('replacement', False),
            'help': "Don't use replacement when sampling."},

        # Doesn't randomize feature selection at each split.
        '--no-randomize': {
            'action': 'store_false',
            'dest': 'randomize',
            'default': defaults.get('randomize', False),
            'help': ("Doesn't randomize feature selection at each"
                     " split.")},

        # Doesn't make model a public black-box model.
        '--no-black-box': {
            'action': 'store_false',
            'dest': 'black_box',
            'default': defaults.get('black_box', False),
            'help': "Doesn't make generated model black-box."},

        # Doesn't make model a public white-box model.
        '--no-white-box': {
            'action': 'store_false',
            'dest': 'white_box',
            'default': defaults.get('white_box', False),
            'help': "Doesn't make generated model white-box."},


        # Create a model just a dataset.
        '--no-no-model': {
            'action': 'store_false',
            'dest': 'no_model',
            'default': defaults.get('no_model', False),
            'help': "Create a model."},

        # Don't clear global bigmler log files
        '--no-clear-logs': {
            'action': 'store_false',
            'dest': 'clear_logs',
            'default': defaults.get('clear_logs', False),
            'help': "Don't clear global bigmler log files."},

        # Don't store the retrieved resources in the output directory
        '--no-store': {
            'action': 'store_false',
            'dest': 'store',
            'default': defaults.get('store', False),
            'help': ("Don't store the retrieved resources in the"
                     " output directory.")},

        # Multi-label. The objective field hasn't multiple labels.
        '--no-multi-label': {
            'action': 'store_false',
            'dest': 'multi_label',
            'default': defaults.get('multi_label', False),
            'help': "The objective field has not multiple labels."},

        # Prediction-header.
        '--no-prediction-header': {
            'action': 'store_false',
            'dest': 'prediction_header',
            'default': defaults.get('prediction_header', False),
            'help': "Headers are not added to the prediction file."},

        # Batch predictions. Remote predictions are created in batch mode.
        '--batch': {
            'action': 'store_false',
            'dest': 'no_batch',
            'default': defaults.get('no_batch', False),
            'help': "Create remote predictions in batch."},

        # Multi-dataset. Generating a new dataset from a list of existing
        # datasets.
        '--no-multi-dataset': {
            'action': 'store_false',
            'dest': 'multi_dataset',
            'default': defaults.get('multi_dataset', False),
            'help': "Do not generate a new dataset."},

        # Shared. Shares all shareable resources and uses its shared links in
        # reports
        '--unshared': {
            'action': 'store_false',
            'dest': 'shared',
            'default': defaults.get('shared', False),
            'help': ("Share resources and use its shared urls "
                     " in reports.")},

        # Enables reports upload.
        '--upload': {
            'action': 'store_true',
            'dest': 'upload',
            'default': defaults.get('upload', True),
            'help': "Enables upload for reports"},

        # Dataset-off. Turning off the dataset-off flag.
        '--no-dataset-off': {
            'action': 'store_false',
            'dest': 'dataset_off',
            'default': defaults.get('dataset_off', False),
            'help': "Turning off the dataset-off flag."},

        # No missing_splits used: Don't include missing values in branches
        # of the tree.
        '--no-missing-splits': {
            'action': 'store_false',
            'dest': 'missing_splits',
            'default': defaults.get('missing_splits', False),
            'help': ("Turning off the --missing-splits flag: don't include"
                     " missing values in branches of the tree.")},

        # Used in models combinations, ensembles predictions. Keeps prediction
        # in memory to be combined and no partial results are stored in files.
        '--fast': {
            'action': 'store_true',
            'dest': 'fast',
            'default': defaults.get('fast', True),
            'help': ("Enables fast ensemble's predictions with no partial"
                     " results files.")},

        # Used in models combinations, ensembles predictions. Stores
        # predictions for each model in files that can be used and combined
        # later
        '--no-fast': {
            'action': 'store_false',
            'dest': 'fast',
            'default': defaults.get('fast', True),
            'help': ("Enables fast ensemble's predictions with partial"
                     " results files.")},

        # Does not create a csv as output of a batch prediction.
        '--no-csv': {
            'action': 'store_true',
            'dest': 'no_csv',
            'default': defaults.get('no_csv', False),
            'help': ("Do not create a csv file as output of a batch"
                     " prediction.")},

        # Create a csv as output (as opposed to --no-csv).
        '--no-no-csv': {
            'action': 'store_false',
            'dest': 'no_csv',
            'default': defaults.get('no_csv', False),
            'help': ("Create a csv file as output of a batch"
                     " prediction (as opposed to --no-csv)")},

        # Create a dataset as ouput of a batch prediction
        '--to-dataset': {
            'action': 'store_true',
            'dest': 'to_dataset',
            'default': defaults.get('to_dataset', False),
            'help': ("Create a dataset as ouput of a batch"
                     " prediction.")},

        # Use median as predicted value in local models predictions
        '--median': {
            'action': 'store_true',
            'dest': 'median',
            'default': defaults.get('median', False),
            'help': ("Use medtan instead on mean as node"
                     " prediction.")},

        # Use mean as predicted value in local models predictions
        '--no-median': {
            'action': 'store_false',
            'dest': 'median',
            'default': defaults.get('median', False),
            'help': ("Use mean instead on median as node"
                     " prediction.")}}

    return options
