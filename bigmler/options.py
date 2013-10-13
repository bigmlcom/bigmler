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


"""Parser for BigMLer

"""
from __future__ import absolute_import

import argparse
import datetime
import pkg_resources


def create_parser(defaults={}, constants={}):
    """Sets the accepted command options, variables, defaults and help

    """
    now = constants.get('NOW',
                        datetime.datetime.now().strftime("%a%b%d%y_%H%M%S"))

    max_models = constants.get('MAX_MODELS')
    plurality = constants.get('PLURALITY')

    version = pkg_resources.require("BigMLer")[0].version
    version_text = """\
BigMLer %s - A Higher Level API to BigML's API
Copyright 2012 BigML

Licensed under the Apache License, Version 2.0 (the \"License\"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an \"AS IS\" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.""" % version
    parser = argparse.ArgumentParser(
        description="A higher level API to BigML's API.",
        epilog="Happy predictive modeling!",
        version=version_text,
        formatter_class=argparse.RawTextHelpFormatter)

    # Shows log info for each https request.
    parser.add_argument('--debug',
                        action='store_true',
                        default=defaults.get('debug', False),
                        help="Activate debug level")

    # Uses BigML dev environment. Sizes must be under 1MB though.
    parser.add_argument('--dev',
                        action='store_true',
                        dest='dev_mode',
                        default=defaults.get('dev', False),
                        help=("Compute a test output using BigML FREE"
                             " development environment."))

    # BigML's username.
    parser.add_argument('--username',
                        action='store',
                        default=defaults.get('username', None),
                        help="BigML's username.")

    # BigML's API key.
    parser.add_argument('--api-key',
                        action='store',
                        dest='api_key',
                        default=defaults.get('api-key', None),
                        help="BigML's API key.")

    # Path to the training set.
    parser.add_argument('--train',
                        action='store',
                        dest='training_set',
                        nargs='?',
                        default=defaults.get('train', None),
                        help="Training set path.")

    # Path to the test set.
    parser.add_argument('--test',
                        action='store',
                        dest='test_set',
                        nargs='?',
                        default=defaults.get('test', None),
                        help="Test set path.")

    # Name of the file to output predictions.
    parser.add_argument('--output',
                        action='store',
                        dest='predictions',
                        default=defaults.get('output', None),
                        help="Path to the file to output predictions.")

    # The name of the field that represents the objective field (i.e., class or
    # label) or its column number.
    parser.add_argument('--objective',
                        action='store',
                        dest='objective_field',
                        default=defaults.get('objective', None),
                        help=("The column number of the Objective Field"
                              " or its name, if headers are given."))

    # Category code.
    parser.add_argument('--category',
                        action='store',
                        dest='category',
                        default=defaults.get('category', 12),
                        type=int,
                        help="Category code.")

    # A file including a makdown description
    parser.add_argument('--description',
                        action='store',
                        dest='description',
                        default=defaults.get('description', None),
                        help=("Path to a file with a description in plain"
                              " text or markdown."))

    # The path to a file containing names if you want to alter BigML's
    # default field names or the ones provided by the train file header.
    # Kept for backwards compatibility
    parser.add_argument('--field-names',
                        action='store',
                        dest='field_attributes',
                        default=defaults.get('field_names', None),
                        help=("Path to a csv file describing field names. One"
                              " definition per line (e.g., 0,'Last Name')."))

    # The path to a file containing attributes if you want to alter BigML's
    # default field attributes or the ones provided by the train file header.
    parser.add_argument('--field-attributes',
                        action='store',
                        dest='field_attributes',
                        default=defaults.get('field_attributes', None),
                        help=("Path to a csv file describing field attributes."
                              " One definition per line"
                              " (e.g., 0,'Last Name')."))

    # The path to a file containing types if you want to alter BigML's
    # type auto-detect.
    parser.add_argument('--types',
                        action='store',
                        dest='types',
                        default=defaults.get('types', None),
                        help=("Path to a file describing field types. One"
                              " definition per line (e.g., 0, 'numeric')."))

    # Fields to include in the dataset.
    parser.add_argument('--dataset-fields',
                        action='store',
                        dest='dataset_fields',
                        default=defaults.get('dataset_fields', None),
                        help=("Comma-separated list of field column numbers"
                              " to include in the dataset."))

    # Path to a file that includes a JSON filter.
    parser.add_argument('--json-filter',
                        action='store',
                        dest='json_filter',
                        default=defaults.get('json_filter', None),
                        help="File including a JSON filter.")

    # Path to a file that includes a lisp filter.
    parser.add_argument('--lisp-filter',
                        action='store',
                        dest='lisp_filter',
                        default=defaults.get('lisp_filter', None),
                        help="File including a Lisp filter.")

    # Input fields to include in the model.
    parser.add_argument('--model-fields',
                        action='store',
                        dest='model_fields',
                        default=defaults.get('model_fields', None),
                        help=("Comma-separated list of input fields"
                              " (predictors) to create the model."))

    # Set when the training set file doesn't include a header on the first
    # line.
    parser.add_argument('--no-train-header',
                        action='store_false',
                        dest='train_header',
                        default=defaults.get('train_header', True),
                        help="The train set file hasn't a header.")

    # Set when the test set file doesn't include a header on the first
    # line.
    parser.add_argument('--no-test-header',
                        action='store_false',
                        dest='test_header',
                        default=defaults.get('test_header', True),
                        help="The test set file hasn't a header.")

    # Name to be used with the source and then with datasets, models and
    # predicitions.
    parser.add_argument('--name',
                        action='store',
                        dest='name',
                        default=defaults.get('name', 'BigMLer_%s' % now),
                        help="Name for the resources in BigML.")

    # If a BigML source is provided, the script won't create a new one
    parser.add_argument('--source',
                        action='store',
                        dest='source',
                        default=defaults.get('source', None),
                        help="BigML source Id.")

    # If a BigML dataset is provided, the script won't create a new one
    parser.add_argument('--dataset',
                        action='store',
                        dest='dataset',
                        default=defaults.get('dataset', None),
                        help="BigML dataset Id.")

    # If a BigML model is provided, the script will use it to generate
    # predictions.
    parser.add_argument('--model',
                        action='store',
                        dest='model',
                        default=defaults.get('model', None),
                        help="BigML model Id.")

    # Use it to compute predictions remotely.
    parser.add_argument('--remote',
                        action='store_true',
                        dest='remote',
                        default=defaults.get('remote', False),
                        help="Compute predictions remotely.")

    # The path to a file containing model ids.
    parser.add_argument('--models',
                        action='store',
                        dest='models',
                        default=defaults.get('models', None),
                        help=("Path to a file containing model/ids. One model"
                              " per line (e.g., model/50a206a8035d0706dc000376"
                              ")."))

    # The path to a file containing a dataset id.
    parser.add_argument('--datasets',
                        action='store',
                        dest='datasets',
                        default=defaults.get('datasets', None),
                        help=("Path to a file containing a dataset/id. Just"
                              " one dataset"
                              " (e.g., dataset/50a20697035d0706da0004a4)."))

    # Sets pruning.
    parser.add_argument('--pruning',
                        action='store',
                        default=defaults.get('pruning', "smart"),
                        choices=["smart", "statistical", "no-pruning"],
                        help=("Set pruning type: smart, statistical,"
                              " no-pruning."))

    # Number of models to create when using ensembles.
    parser.add_argument('--number-of-models',
                        action='store',
                        dest='number_of_models',
                        default=defaults.get('number_of_models', 1),
                        type=int,
                        help=("Number of models to create when using"
                              " ensembles."))

    # Sampling to use when using bagging.
    parser.add_argument('--sample-rate',
                        action='store',
                        dest='sample_rate',
                        default=defaults.get('sample_rate', 1.0),
                        type=float,
                        help="Sample rate to create models.")

    # Replacement to use when using bagging.
    parser.add_argument('--replacement',
                        action='store_true',
                        default=defaults.get('replacement', False),
                        help="Use replacement when sampling.")

    # Max number of models to create in parallel.
    parser.add_argument('--max-parallel-models',
                        action='store',
                        dest='max_parallel_models',
                        default=defaults.get('max_parallel_models', 1),
                        type=int,
                        help="Max number of models to create in parallel.")

    # Max number of models to predict from in parallel.
    parser.add_argument('--max-batch-models',
                        action='store',
                        dest='max_batch_models',
                        default=defaults.get('max_batch_models', max_models),
                        type=int,
                        help=("Max number of models to predict from"
                              " in parallel."))

    # Randomize feature selection at each split.
    parser.add_argument('--randomize',
                        action='store_true',
                        dest='randomize',
                        default=defaults.get('randomize', False),
                        help="Randomize feature selection at each split.")

    # Use it to add a tag to the new resources created.
    defaults_tag = defaults.get('tag')
    defaults_tag = [] if defaults_tag is None else defaults_tag.split(",")
    parser.add_argument('--tag',
                        action='append',
                        default=defaults_tag,
                        help="Tag to later retrieve new resources.")
    # Avoid default tagging of resources.
    parser.add_argument('--no-tag',
                        action='store_false',
                        dest='no_tag',
                        default=defaults.get('no_tag', True),
                        help="No tag resources with default BigMLer tags.")

    # Use it to retrieve models that were tagged with tag.
    parser.add_argument('--model-tag',
                        dest='model_tag',
                        default=defaults.get('model_tag', None),
                        help="Retrieve models that were tagged with tag.")

    # Make dataset public.
    parser.add_argument('--public-dataset',
                        action='store_true',
                        dest='public_dataset',
                        default=defaults.get('public_dataset', False),
                        help="Make generated dataset public.")

    # Make model a public black-box model.
    parser.add_argument('--black-box',
                        action='store_true',
                        dest='black_box',
                        default=defaults.get('black_box', False),
                        help="Make generated model black-box.")

    # Make model a public white-box model.
    parser.add_argument('--white-box',
                        action='store_true',
                        dest='white_box',
                        default=defaults.get('white_box', False),
                        help="Make generated model white-box.")

    # Set a price tag to your white-box model.
    parser.add_argument('--model-price',
                        action='store',
                        dest='model_price',
                        type=float,
                        default=defaults.get('model_price', 0.0),
                        help=("The price other users must pay to clone your"
                              " model."))

    # Set a price tag to your dataset.
    parser.add_argument('--dataset-price',
                        action='store',
                        dest='dataset_price',
                        type=float,
                        default=defaults.get('dataset_price', 0.0),
                        help="Price for the dataset.")

    # Set credits per prediction to your white box or black box models.
    parser.add_argument('--cpp',
                        action='store',
                        type=float,
                        default=defaults.get('cpp', 0.0),
                        help=("The number of credits that other users will"
                              " consume to make a prediction with your"
                              " model."))

    # Shows progress information when uploading a file.
    parser.add_argument('--progress-bar',
                        action='store_true',
                        dest='progress_bar',
                        default=defaults.get('progress_bar', False),
                        help="Show progress details when creating a source.")

    # Does not create a dataset.
    parser.add_argument('--no-dataset',
                        action='store_true',
                        dest='no_dataset',
                        default=defaults.get('no_dataset', False),
                        help="Do not create a dataset.")

    # Does not create a model just a dataset.
    parser.add_argument('--no-model',
                        action='store_true',
                        dest='no_model',
                        default=defaults.get('no_model', False),
                        help="Do not create a model.")

    # Log file to store resources ids.
    parser.add_argument('--resources-log',
                        action='store',
                        dest='log_file',
                        default=defaults.get('resources_log', None),
                        help=("Path to a file to store new resources ids."
                              " One resource per line"
                              " (e.g., model/50a206a8035d0706dc000376)."))
    # Changes to delete mode.
    parser.add_argument('--delete',
                        action='store_true',
                        help="Delete command.")

    # Resources to be deleted.
    parser.add_argument('--ids',
                        action='store',
                        dest='delete_list',
                        help=("Select comma-separated list of"
                              " resources to be deleted."))

    # Resources to be deleted are taken from file.
    parser.add_argument('--from-file',
                        action='store',
                        dest='delete_file',
                        default=defaults.get('from_file', None),
                        help=("Path to a file containing resources ids."
                              " One resource per line"
                              " (e.g., model/50a206a8035d0706dc000376)."))

    # Sources selected by tag to be deleted.
    parser.add_argument('--source-tag',
                        dest='source_tag',
                        default=defaults.get('source_tag', None),
                        help=("Select sources tagged with tag to"
                              " be deleted"))

    # Datasets selected by tag to be deleted.
    parser.add_argument('--dataset-tag',
                        dest='dataset_tag',
                        default=defaults.get('dataset_tag', None),
                        help=("Select datasets tagged with tag to"
                              " be deleted"))

    # Predictions selected by tag to be deleted.
    parser.add_argument('--prediction-tag',
                        dest='prediction_tag',
                        default=defaults.get('prediction_tag', None),
                        help=("Select prediction tagged with tag to"
                              " be deleted."))

    # Evaluations selected by tag to be deleted.
    parser.add_argument('--evaluation-tag',
                        dest='evaluation_tag',
                        default=defaults.get('evaluation_tag', None),
                        help=("Select evaluation tagged with tag to"
                              " be deleted."))

    # Ensembles selected by tag to be deleted.
    parser.add_argument('--ensemble-tag',
                        dest='ensemble_tag',
                        default=defaults.get('ensemble_tag', None),
                        help=("Select ensemble tagged with tag to"
                              " be deleted."))

    # Resources selected by tag to be deleted.
    parser.add_argument('--all-tag',
                        dest='all_tag',
                        default=defaults.get('all_tag', None),
                        help=("Select resources tagged with tag to"
                              " be deleted."))

    # Locale settings.
    parser.add_argument('--locale',
                        action='store',
                        dest='user_locale',
                        default=defaults.get('locale', None),
                        help="Chosen locale code string.")

    # Prediction directories to be combined.
    parser.add_argument('--combine-votes',
                        action='store',
                        dest='votes_dirs',
                        default=defaults.get('combine_votes', None),
                        help=("Comma separated list of"
                              " directories that contain models' votes"
                              " for the same test set."))

    # Method to combine votes in multiple models predictions
    parser.add_argument('--method',
                        action='store',
                        dest='method',
                        default=defaults.get('method', plurality),
                        choices=["plurality", "confidence weighted",
                                 "probability weighted"],
                        help="Method to combine votes from ensemble"
                             " predictions. Allowed methods: plurality"
                             ", \"confidence weighted\" or "
                             " \"probability weighted\".")

    # Resume a partial execution
    parser.add_argument('--resume',
                        action='store_true',
                        help="Resume command.")

    # Resume a partial execution
    parser.add_argument('--stack-level',
                        action='store',
                        dest='stack_level',
                        default=0,
                        type=int,
                        help="Resume command.")

    # Evaluate a model
    parser.add_argument('--evaluate',
                        action='store_true',
                        help="Evaluate command.")

    # Turn on/off verbosity
    parser.add_argument('--verbosity',
                        action='store',
                        dest='verbosity',
                        default=defaults.get('verbosity', 1),
                        type=int,
                        choices=[0, 1],
                        help="Set verbosity: 0 to turn off, 1 to turn on.")

    # The path to a file containing the mapping of fields' ids from
    # the test dataset fields to the model fields.
    parser.add_argument('--fields-map',
                        action='store',
                        dest='fields_map',
                        default=defaults.get('fields_map', None),
                        help=("Path to a csv file describing fields mapping. "
                              "One definition per line (e.g., 00000,"
                              "00000a)."))

    # Clear global bigmler log files
    parser.add_argument('--clear-logs',
                        action='store_true',
                        dest='clear_logs',
                        default=defaults.get('clear_logs', False),
                        help="Clear global bigmler log files.")

    # Set the part of training data to be held out for cross-validation
    parser.add_argument('--cross-validation-rate',
                        action='store',
                        dest='cross_validation_rate',
                        type=float,
                        default=defaults.get('cross_validation_rate', 0.0),
                        help=("Part of training data to be held out for "
                              "cross-validation."))

    # Number of evaluations used in cross-validation
    parser.add_argument('--number-of-evaluations',
                        action='store',
                        dest='number_of_evaluations',
                        type=int,
                        default=defaults.get('number_of_evaluations', 0),
                        help=("Number of evaluations used for"
                              " cross-validation."))

    # Stores the retrieved resources in the output directory
    parser.add_argument('--store',
                        action='store_true',
                        dest='store',
                        default=defaults.get('store', False),
                        help=("Store the retrieved resources in the"
                              " output directory."))

    # Set the part of training data to be held out for testing
    parser.add_argument('--test-split',
                        action='store',
                        dest='test_split',
                        type=float,
                        default=defaults.get('test_split', 0.0),
                        help=("Part of training data to be held out for "
                              "testing (e.g. --test-split 0.2)."))

    # If a BigML ensemble is provided, the script will use it to generate
    # predictions.
    parser.add_argument('--ensemble',
                        action='store',
                        dest='ensemble',
                        default=defaults.get('ensemble', None),
                        help="BigML ensemble Id.")

    # If a BigML ensemble is created, creation will use this task-level
    # parallelism
    parser.add_argument('--tlp',
                        action='store',
                        dest='tlp',
                        default=defaults.get('tlp', 1),
                        type=int,
                        help=("BigML ensemble's creation task-level"
                              " parallelism."))

    # Prediction log format: `short` will only log predictions, `long` will
    # log also confidence information
    parser.add_argument('--prediction-info',
                        action='store',
                        dest='prediction_info',
                        default=defaults.get('prediction_info', 'normal'),
                        choices=["brief", "normal", "full", "full data"],
                        help=("Prediction log format: 'brief' will only "
                              "log predictions, 'normal' will write confidence"
                              " too, 'full' will write in a row the"
                              " input data that generates the prediction"
                              " followed by the latter."))

    # Max number of evaluations to create in parallel.
    parser.add_argument('--max-parallel-evaluations',
                        action='store',
                        dest='max_parallel_evaluations',
                        default=defaults.get('max_parallel_evaluations', 1),
                        type=int,
                        help=("Max number of evaluations to create in"
                              " parallel."))

    # Test set field separator. Defaults to the locale csv
    # separator.
    parser.add_argument('--test-separator',
                        action='store',
                        dest='test_separator',
                        default=defaults.get('test_separator', None),
                        help="Test set field separator.")

    # Multi-label. The objective field has multiple labels.
    parser.add_argument('--multi-label',
                        action='store_true',
                        dest='multi_label',
                        default=defaults.get('multi_label', False),
                        help=("The objective field has multiple labels that"
                              " should be treated independently."))

    # Multi-label labels. If set, only the given labels are expanded
    parser.add_argument('--labels',
                        action='store',
                        dest='labels',
                        default=defaults.get('labels', None),
                        help=("Comma-separated list of the labels"
                              " to be expanded from a multi-label field."))

    # Multi-label label separator. Separator used when splitting labels in the
    # objective field.
    parser.add_argument('--label-separator',
                        action='store',
                        dest='label_separator',
                        default=defaults.get('label_separator', None),
                        help=("Separator used when splitting labels in the"
                              " objective field."))

    # Training set field separator. Defaults to the locale csv
    # separator.
    parser.add_argument('--training-separator',
                        action='store',
                        dest='training_separator',
                        default=defaults.get('training_separator', None),
                        help=("Training set field separator."))

    # Prediction header. If set, headers are added to the prediction file.
    parser.add_argument('--prediction-header',
                        action='store_true',
                        dest='prediction_header',
                        default=defaults.get('prediction_header', False),
                        help="Headers are added to the prediction file.")

    # Prediction fields. A comma-separated list of the fields that should
    # be included in the prediction file.
    parser.add_argument('--prediction-fields',
                        action='store',
                        dest='prediction_fields',
                        default=defaults.get('prediction_fields', None),
                        help="Fields added to the prediction file.")

    # Seed. The value used in dataset's splits as seed
    parser.add_argument('--seed',
                        action='store',
                        dest='seed',
                        default=defaults.get('seed', None),
                        help="Value used as seed in dataset splits.")

    # Max number of ensembles to create in parallel.
    parser.add_argument('--max-parallel-ensembles',
                        action='store',
                        dest='max_parallel_ensembles',
                        default=defaults.get('max_parallel_ensembles', 1),
                        type=int,
                        help="Max number of ensembles to create in parallel.")

    # The path to a file containing ensemble ids.
    parser.add_argument('--ensembles',
                        action='store',
                        dest='ensembles',
                        default=defaults.get('ensembles', None),
                        help=("Path to a file containing ensemble/ids. One "
                              "ensemble per line (e.g., "
                              "ensemble/50a206a8035d0706dc000376)."))

    # The following options are only useful to deactivate the corresponding
    # oposed default values
    #
    # Hides log info for each https request.
    parser.add_argument('--no-debug',
                        action='store_false',
                        dest='debug',
                        default=defaults.get('debug', False),
                        help="Deactivate debug level.")

    # Uses BigML standard environment.
    parser.add_argument('--no-dev',
                        action='store_false',
                        dest='dev_mode',
                        default=defaults.get('dev', False),
                        help=("Compute a test output using BigML "
                             "standard development environment."))

    # Set when the training set file does include a header on the first
    # line.
    parser.add_argument('--train-header',
                        action='store_true',
                        dest='train_header',
                        default=defaults.get('train_header', True),
                        help="The train set file has a header.")

    # Set when the test set file does include a header on the first
    # line.
    parser.add_argument('--test-header',
                        action='store_true',
                        dest='test_header',
                        default=defaults.get('test_header', True),
                        help="The test set file has a header.")

    # Use it to compute predictions locally.
    parser.add_argument('--local',
                        action='store_false',
                        dest='remote',
                        default=defaults.get('remote', False),
                        help="Compute predictions locally")

    # Deactivate replacement to use when using bagging.
    parser.add_argument('--no-replacement',
                        action='store_false',
                        dest='replacement',
                        default=defaults.get('replacement', False),
                        help="Don't use replacement when sampling.")

    # Doesn't randomize feature selection at each split.
    parser.add_argument('--no-randomize',
                        action='store_false',
                        dest='randomize',
                        default=defaults.get('randomize', False),
                        help=("Doesn't randomize feature selection at each"
                              " split."))

    # Set default tagging of resources.
    parser.add_argument('--no-no-tag',
                        action='store_true',
                        dest='no_tag',
                        default=defaults.get('no_tag', True),
                        help="No tag resources with default BigMLer tags.")

    # Doesn't make dataset public.
    parser.add_argument('--no-public-dataset',
                        action='store_false',
                        dest='public_dataset',
                        default=defaults.get('public_dataset', False),
                        help="Doesn't make generated dataset public.")

    # Doesn't make model a public black-box model.
    parser.add_argument('--no-black-box',
                        action='store_false',
                        dest='black_box',
                        default=defaults.get('black_box', False),
                        help="Doesn't make generated model black-box.")

    # Doesn't make model a public white-box model.
    parser.add_argument('--no-white-box',
                        action='store_false',
                        dest='white_box',
                        default=defaults.get('white_box', False),
                        help="Doesn't make generated model white-box.")

    # Hides progress information when uploading a file.
    parser.add_argument('--no-progress-bar',
                        action='store_false',
                        dest='progress_bar',
                        default=defaults.get('progress_bar', False),
                        help="Show progress details when creating a source.")

    # Create a dataset.
    parser.add_argument('--no-no-dataset',
                        action='store_false',
                        dest='no_dataset',
                        default=defaults.get('no_dataset', False),
                        help="Create a dataset.")

    # Create a model just a dataset.
    parser.add_argument('--no-no-model',
                        action='store_false',
                        dest='no_model',
                        default=defaults.get('no_model', False),
                        help="Create a model.")

    # Don't clear global bigmler log files
    parser.add_argument('--no-clear-logs',
                        action='store_false',
                        dest='clear_logs',
                        default=defaults.get('clear_logs', False),
                        help="Don't clear global bigmler log files.")

    # Don't store the retrieved resources in the output directory
    parser.add_argument('--no-store',
                        action='store_false',
                        dest='store',
                        default=defaults.get('store', False),
                        help=("Don't store the retrieved resources in the"
                              " output directory."))

    # Multi-label. The objective field hasn't multiple labels.
    parser.add_argument('--no-multi-label',
                        action='store_false',
                        dest='multi_label',
                        default=defaults.get('multi_label', False),
                        help=("The objective field has not multiple labels."))

    # Prediction-header.
    parser.add_argument('--no-prediction-header',
                        action='store_false',
                        dest='prediction_header',
                        default=defaults.get('prediction_header', False),
                        help="Headers are not added to the prediction file.")
    return parser
