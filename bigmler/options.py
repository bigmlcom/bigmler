#!/usr/bin/env python
#
# Copyright 2012 BigML
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
import os
import datetime


def create_parser(defaults={}):
    """Sets the accepted command options, variables, defaults and help

    """
    now = defaults.get('NOW',
                       datetime.datetime.now().strftime("%a%b%d%y_%H%M%S"))

    max_models = defaults.get('MAX_MODELS')

    parser = argparse.ArgumentParser(
        description="A higher level API to BigML's API.",
        epilog="Happy predictive modeling!")

    # Shows log info for each https request.
    parser.add_argument('--debug',
                        action='store_true',
                        help="Activate debug level")

    # Uses BigML dev environment. Sizes must be under 1MB though.
    parser.add_argument('--dev',
                        action='store_true',
                        dest='dev_mode',
                        help=("Compute a test output using BigML FREE"
                             " development environment"))
    # BigML's username.
    parser.add_argument('--username',
                        action='store',
                        help="BigML's username")

    # BigML's API key.
    parser.add_argument('--api_key',
                        action='store',
                        help="BigML's API key")

    # Path to the training set.
    parser.add_argument('--train',
                        action='store',
                        dest='training_set',
                        help="Training set path")

    # Path to the test set.
    parser.add_argument('--test',
                        action='store',
                        dest='test_set',
                        help="Test set path")

    # Name of the file to output predictions.
    parser.add_argument('--output',
                        action='store',
                        dest='predictions',
                        default='%s%spredictions.csv' % (now, os.sep),
                        help="Path to the file to output predictions.")

    # The name of the field that represents the objective field (i.e., class or
    # label).
    parser.add_argument('--objective',
                        action='store',
                        dest='objective_field',
                        help="The column number of the Objective Field")

    # Category code.
    parser.add_argument('--category',
                        action='store',
                        dest='category',
                        default=12,
                        type=int,
                        help="Category code")

    # A file including a makdown description
    parser.add_argument('--description',
                        action='store',
                        dest='description',
                        help=("Path to a file with a description in plain"
                              " text or markdown"))

    # The path to a file containing names if you want to alter BigML's
    # default field names or the ones provided by the train file header.
    # Kept for backwards compatibility
    parser.add_argument('--field_names',
                        action='store',
                        dest='field_attributes',
                        help=("Path to a csv file describing field names. One"
                              " definition per line (e.g., 0,'Last Name')"))

    # The path to a file containing attributes if you want to alter BigML's
    # default field attributes or the ones provided by the train file header.
    parser.add_argument('--field_attributes',
                        action='store',
                        dest='field_attributes',
                        help=("Path to a csv file describing field attributes."
                              " One definition per line"
                              " (e.g., 0,'Last Name')"))

    # The path to a file containing types if you want to alter BigML's
    # type auto-detect.
    parser.add_argument('--types',
                        action='store',
                        dest='types',
                        help=("Path to a file describing field types. One"
                              " definition per line (e.g., 0, 'numeric')"))

    # Fields to include in the dataset.
    parser.add_argument('--dataset_fields',
                        action='store',
                        dest='dataset_fields',
                        help=("Comma-separated list of field column numbers"
                              " to include in the dataset"))

    # Path to a file that includes a JSON filter.
    parser.add_argument('--json_filter',
                        action='store',
                        help="File including a JSON filter")

    # Path to a file that includes a lisp filter.
    parser.add_argument('--lisp_filter',
                        action='store',
                        help="File including a Lisp filter")

    # Input fields to include in the model.
    parser.add_argument('--model_fields',
                        action='store',
                        dest='model_fields',
                        help=("Comma-separated list of input fields"
                              " (predictors) to create the model"))

    # Set when the training set file doesn't include a header on the first
    # line.
    parser.add_argument('--no-train-header',
                        action='store_false',
                        dest='train_header',
                        help="The train set file hasn't a header")

    # Set when the test set file doesn't include a header on the first
    # line.
    parser.add_argument('--no-test-header',
                        action='store_false',
                        dest='test_header',
                        help="The test set file hasn't a header")

    # Name to be used with the source and then with datasets, models and
    # predicitions.
    parser.add_argument('--name',
                        action='store',
                        dest='name',
                        default='BigMLer_%s' % now,
                        help="Name for the resources in BigML")

    # If a BigML source is provided, the script won't create a new one
    parser.add_argument('--source',
                        action='store',
                        dest='source',
                        help="BigML source Id")

    # If a BigML dataset is provided, the script won't create a new one
    parser.add_argument('--dataset',
                        action='store',
                        dest='dataset',
                        help="BigML dataset Id")

    # If a BigML model is provided, the script will use it to generate
    # predictions.
    parser.add_argument('--model',
                        action='store',
                        dest='model',
                        help="BigML model Id")

    # Use it to compute predictions remotely.
    parser.add_argument('--remote',
                        action='store_true',
                        help="Compute predictions remotely")

    # The path to a file containing model ids.
    parser.add_argument('--models',
                        action='store',
                        dest='models',
                        help=("Path to a file containing model/ids. One model"
                              " per line (e.g., model/50a206a8035d0706dc000376"
                              ")"))

    # The path to a file containing a dataset id.
    parser.add_argument('--datasets',
                        action='store',
                        dest='datasets',
                        help=("Path to a file containing a dataset/id. Just"
                              " one dataset"
                              " (e.g., dataset/50a20697035d0706da0004a4)"))

    # Set to True to active statiscal pruning.
    parser.add_argument('--stat_pruning',
                        action='store_true',
                        help="Use statiscal pruning.")

    # Set to False to deactivate statiscal pruning.
    parser.add_argument('--no_stat_pruning',
                        action='store_true',
                        help="Do not use statistical pruning.")

    # Number of models to create when using ensembles.
    parser.add_argument('--number_of_models',
                        action='store',
                        dest='number_of_models',
                        default=1,
                        type=int,
                        help="Number of models to create when using ensembles")

    # Sampling to use when using bagging.
    parser.add_argument('--sample_rate',
                        action='store',
                        dest='sample_rate',
                        default=1,
                        type=float,
                        help="Sample rate to create models")

    # Replacement to use when using bagging.
    parser.add_argument('--replacement',
                        action='store_true',
                        help="Use replacement when sampling")

    # Max number of models to create in parallel.
    parser.add_argument('--max_parallel_models',
                        action='store',
                        dest='max_parallel_models',
                        default=1,
                        type=int,
                        help="Max number of models to create in parallel")

    # Max number of models to predict from in parallel.
    parser.add_argument('--max_batch_models',
                        action='store',
                        dest='max_batch_models',
                        default=max_models,
                        type=int,
                        help=("Max number of models to predict from"
                              "in parallel"))

    # Randomize feature selection at each split.
    parser.add_argument('--randomize',
                        action='store_true',
                        help="Randomize feature selection at each split.")

    # Use it to add a tag to the new resources created.
    parser.add_argument('--tag',
                        action='append',
                        default=[],
                        help="Tag to later retrieve new resources")

    # Avoid default tagging of resources.
    parser.add_argument('--no_tag',
                        action='store_false',
                        help="No tag resources with default BigMLer tags")

    # Use it to retrieve models that were tagged with tag.
    parser.add_argument('--model_tag',
                        help="Retrieve models that were tagged with tag")

    # Make dataset public.
    parser.add_argument('--public_dataset',
                        action='store_true',
                        help="Make generated dataset public")

    # Make model a public black-box model.
    parser.add_argument('--black_box',
                        action='store_true',
                        help="Make generated model black-box")

    # Make model a public white-box model.
    parser.add_argument('--white_box',
                        action='store_true',
                        help="Make generated model white-box")

    # Set a price tag to your white-box model.
    parser.add_argument('--model_price',
                        action='store',
                        type=float,
                        default=0.0,
                        help=("The price other users must pay to clone your"
                              " model"))

    # Set a price tag to your dataset.
    parser.add_argument('--dataset_price',
                        action='store',
                        type=float,
                        default=0.0,
                        help="Price for the dataset")

    # Set credits per prediction to your white box or black box models.
    parser.add_argument('--cpp',
                        action='store',
                        type=float,
                        default=0.0,
                        help=("The number of credits that other users will"
                              " consume to make a prediction with your"
                              " model."))

    # Shows progress information when uploading a file.
    parser.add_argument('--progress_bar',
                        action='store_true',
                        help="Show progress details when creating a source.")

    # Does not create a dataset.
    parser.add_argument('--no_dataset',
                        action='store_true',
                        help="Do not create a dataset.")

    # Does not create a model just a dataset.
    parser.add_argument('--no_model',
                        action='store_true',
                        help="Do not create a model.")

    # Log file to store resources ids.
    parser.add_argument('--resources_log',
                        action='store',
                        dest='log_file',
                        help=("Path to a file to store new resources ids."
                              " One resource per line"
                              " (e.g., model/50a206a8035d0706dc000376)"))
    # Changes to delete mode.
    parser.add_argument('--delete',
                        action='store_true',
                        help="Delete command.")

    # Resources to be deleted.
    parser.add_argument('--ids',
                        action='store',
                        dest='delete_list',
                        help=("Select comma separated list of"
                              " resources to be deleted."))

    # Resources to be deleted are taken from file.
    parser.add_argument('--from_file',
                        action='store',
                        dest='delete_file',
                        help=("Path to a file containing resources ids."
                              " One resource per line"
                              " (e.g., model/50a206a8035d0706dc000376)"))

    # Sources selected by tag to be deleted.
    parser.add_argument('--source_tag',
                        help=("Select sources tagged with tag to"
                              " be deleted"))

    # Datasets selected by tag to be deleted.
    parser.add_argument('--dataset_tag',
                        help=("Select datasets tagged with tag to"
                              " be deleted"))

    # Predictions selected by tag to be deleted.
    parser.add_argument('--prediction_tag',
                        help=("Select prediction tagged with tag to"
                              " be deleted"))

    # Resources selected by tag to be deleted.
    parser.add_argument('--all_tag',
                        help=("Select resources tagged with tag to"
                              " be deleted"))

    # Locale settings.
    parser.add_argument('--locale',
                        action='store',
                        dest='user_locale',
                        default=None,
                        help="Chosen locale code string.")

    # Prediction directories to be combined.
    parser.add_argument('--combine_votes',
                        action='store',
                        dest='votes_dirs',
                        help=("Comma separated list of"
                              " directories that contain models' votes"
                              " for the same test set."))

    # Method to combine votes in multiple models predictions
    parser.add_argument('--method',
                        action='store',
                        dest='method',
                        default='plurality',
                        help="Method to combine votes from ensemble"
                             " predictions. Allowed methods: plurality"
                             " or \"confidence weighted\".")

    # Resume a partial execution
    parser.add_argument('--resume',
                        action='store_true',
                        help="Resume command.")

    # Resume a partial execution
    parser.add_argument('--stack_level',
                        action='store',
                        dest='stack_level',
                        default=0,
                        type=int,
                        help="Resume command.")

    return parser
