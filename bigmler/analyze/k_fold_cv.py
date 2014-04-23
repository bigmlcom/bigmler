# -*- coding: utf-8 -*-
#
# Copyright 2012-2014 BigML
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

"""k-fold cross-validation procedure (analysis subcommand)

   Functions used in k-fold cross-validation procedure.


"""
from __future__ import absolute_import


import os
import sys
import json

import bigml

import bigmler.processing.args as a
import bigmler.utils as u

from copy import copy

from bigml.fields import Fields

from bigmler.dispatcher import main_dispatcher
from bigmler.processing.datasets import get_fields_structure

ACCURACY = "accuracy"
AVG_PREFIX = "average_%s"
R_SQUARED = "r_squared"

EXTENDED_DATASET = "kfold_dataset.json"
TEST_DATASET = "kfold_dataset-%s.json"

NEW_FIELD = ('{"row_offset": %s, "row_step": %s,'
             ' "new_fields": [{"name": "%s", "field": "%s"}],'
             ' "objective_field": {"id": "%s"}}')

COMMAND_SELECTION = ("main --dataset %s --new-field %s --no-model --output-dir"
                     " %s")
COMMAND_OBJECTIVE = ("main --dataset %s --objective %s --no-model"
                     " --name %s --output-dir %s")
COMMAND_CREATE_CV = ("main --datasets %s --output-dir %s"
                     " --dataset-off --evaluate"
                     " --name eval_%s")
DEFAULT_KFOLD_FIELD = "__kfold__"

# difference needed to become new best node
EPSILON = 0.001

# per feature score penalty
DEFAULT_PENALTY = 0.001

# staleness
DEFAULT_STALENESS = 5


def create_kfold_cv(args, api, common_options):
    """Creates the kfold cross-validation

    """
    datasets_file, objective_column = create_kfold_datasets_file(
        args, api, common_options)
    if datasets_file is not None:
        args.output_dir = "%s%sk_fold" % (u.check_dir(datasets_file), os.sep)
        message = ('Creating the kfold evaluations.........\n')
        u.log_message(message, log_file=args.session_file,
                      console=args.verbosity)
        create_kfold_evaluations(datasets_file, args, common_options)


def create_features_analysis(args, api, common_options):
    """Analyzes the features in the dataset to find the ones that
       optimize the model performance

    """
    datasets_file, objective_column = create_kfold_datasets_file(
        args, api, common_options)
    message = ('Creating the best features set..........\n')
    u.log_message(message, log_file=args.session_file,
                  console=args.verbosity)
    best_first_search(datasets_file, api, args, common_options,
                      staleness=args.staleness,
                      penalty=args.penalty, objective_column=objective_column)


def create_kfold_datasets_file(args, api, common_options):
    """Create the kfold dataset resources and store their ids in a file
       one per line

    """
    message = ('Creating the kfold datasets............\n')
    u.log_message(message, log_file=args.session_file, console=args.verbosity)
    if args.output_dir is None:
        args.output_dir = a.NOW
    # retrieve dataset
    dataset_id = bigml.api.get_dataset_id(args.dataset)
    if dataset_id:
        dataset = api.check_resource(dataset_id, api.get_dataset)
        # check that kfold_field is unique
        fields = Fields(dataset, {"objective_field": args.objective_field,
                                  "objective_field_present": True})
        objective_id = fields.field_id(fields.objective_field)
        kfold_field_name = avoid_duplicates(DEFAULT_KFOLD_FIELD, fields)
        # create jsons to generate partial datasets
        selecting_file_list = create_kfold_json(args.output_dir,
                                                kfold_field_name, args.k_folds,
                                                objective_id) 
        # generate test datasets
        datasets_file = create_kfold_datasets(dataset_id, args,
                                              selecting_file_list,
                                              fields.objective_field,
                                              kfold_field_name,
                                              common_options)
        return datasets_file, fields.field_column_number(objective_id)
    return None    


def create_kfold_json(output_dir, kfold_field=DEFAULT_KFOLD_FIELD,
                      k=5, objective_field=None):
    """Create the files to generate a new field with a random integer from
       0 to k-1, and a filter file for each of these indexes.

    """

    try:
        selecting_file_list = []
        for index in range(0, k):
            new_field = NEW_FIELD % (index, k, kfold_field,
                                     index, objective_field)
            selecting_file = TEST_DATASET % index
            selecting_file =  "%s%s%s" % (output_dir, os.sep, selecting_file)
            selecting_file_list.append(selecting_file)
            with open(selecting_file, "w") as test_dataset:
                test_dataset.write(new_field)
        return selecting_file_list
    except IOError, exc:
        sys.exit("Could not create the necessary files: %s" % str(exc))


def avoid_duplicates(field_name, fields, affix="_"):
    """Checks if a field name already exists in a fields structure.

    """
    if any([field['name'] == field_name
            for _, field in fields.fields.items()]):
        return avoid_duplicates("%s%s%s" % (affix, field_name, affix),
                                fields, affix=affix)
    return field_name


def create_kfold_datasets(dataset, args,
                          selecting_file_list, objective, kfold_field,
                          common_options):
    """Calling the bigmler procedure to create the k-fold datasets

    """
    output_dir = "%s%s%s" % (args.output_dir, os.sep, "test")
    k = args.k_folds
    # creating the selecting datasets
    for index in range(0, len(selecting_file_list)):
        command = COMMAND_SELECTION % (
            dataset, selecting_file_list[index],
            output_dir)
        command_args = command.split()
        common_options_list = u.get_options_list(args, common_options,
                                                 prioritary=command_args)
        command_args.extend(common_options_list)
        main_dispatcher(args=command_args)
    # creating the models from the datasets' files (multidatasets excluding
    # one test dataset at a time)
    datasets_file = "%s%sdataset_gen" % (output_dir, os.sep)
    try:
        with open(datasets_file) as datasets_handler:
            for line in datasets_handler:
                dataset_id = line.strip()
                command = COMMAND_OBJECTIVE % (dataset_id, objective,
                                               "dataset_%s" % index, output_dir)
                command_args = command.split()
                common_options_list = u.get_options_list(args, common_options,
                                                         prioritary=command_args)
                command_args.extend(common_options_list)
                main_dispatcher(args=command_args)
    except IOError, exc:
        sys.exit("Failed to read the datasets file: %s" % str(exc))

    return datasets_file


def create_kfold_evaluations(datasets_file, args, counter, common_options):
    """ Create k-fold cross-validation from a datasets file

    """
    output_dir = u.check_dir("%s%s/evaluation.json" % (args.output_dir,
                                                       counter))
    model_fields = args.model_fields
    command = COMMAND_CREATE_CV % (datasets_file, output_dir,
                                   args.model_fields.replace(" ", "_"))
    command_args = command.split()
    if model_fields:
        command_args.append("--model-fields")
        command_args.append(model_fields)
    common_options_list = u.get_options_list(args, common_options,
                                             prioritary=command_args)
    command_args.extend(common_options_list)
    main_dispatcher(args=command_args)
    evaluation_file = "%s%sevaluation.json" % (output_dir, os.sep)
    try:
        with open(evaluation_file) as evaluation_handler:
            evaluation = json.loads(evaluation_handler.read())
        return evaluation
    except (ValueError, IOError):
        sys.exit("Failed to retrieve evaluation.")


def find_max_state(states):
    maxval = -1
    maxstate = ''
    for (v,f) in states:
        if f > maxval:
            maxstate = v
            maxval = f
    return maxstate,maxval


def expand_state(parent):
    """Get all connected states

    """
    children = []
    for i in range(len(parent)):
        child = copy(parent)
        child[i] = not child[i]
        children.append(child)
    return children


def best_first_search(datasets_file, api, args, common_options,
                      staleness=None, penalty=None, objective_column=None):
    """Selecting the fields to be used in the model construction

    """
    counter = 0
    if staleness is None:
        staleness = DEFAULT_STALENESS
    if penalty is None:
        penalty = DEFAULT_PENALTY
    # retrieving the first dataset in the file
    try:
        with open(datasets_file) as datasets_handler:
            dataset_id = datasets_handler.readline().strip()
    except IOError, exc:
        sys.exit("Could not read the generated datasets file: %s" % str(exc))
    dataset = api.check_resource(dataset_id, api.get_dataset)
    # initial feature set
    fields = Fields(dataset)
    objective_id = fields.field_id(objective_column)
    field_ids = [field_id for field_id in fields.preferred_fields()
                 if field_id != objective_id]
    initial_state = [False for field_id in field_ids]
    open_list = [(initial_state,0)]
    closed_list = []
    best_accuracy = -1
    best_unchanged_count = 0
    measurement = ACCURACY.capitalize()
    while best_unchanged_count < staleness:
        (state, score) = find_max_state(open_list)
        state_fields = [fields.field_name(field_ids[i])
                        for (i, val) in enumerate(state) if val]
        closed_list.append((state, score))
        open_list.remove((state, score))
        if (score - EPSILON) > best_accuracy:
            best_state = state
            best_accuracy = score
            best_unchanged_count = 0
            if state_fields:
                message = 'New best state: %s\n' % (state_fields)
                u.log_message(message, log_file=args.session_file,
                              console=args.verbosity)
                message = '%s = %0.2f%%\n' % (measurement, score)
                u.log_message(message, log_file=args.session_file,
                              console=args.verbosity)
        else:
            best_unchanged_count += 1

        children = expand_state(state)
        for child in children:
            if (child not in [state for state, _ in open_list]
                    and child not in [state for state, _ in closed_list]):
                input_fields = [fields.field_name(field_id) for (i, field_id)
                                in enumerate(field_ids) if child[i]]
                # create models and evaluation with input_fields
                args.model_fields = ",".join(input_fields)
                counter += 1
                score, measurement = kfold_evaluate(
                    datasets_file, api, args, counter, common_options,
                    penalty=penalty)
                open_list.append((child, score))

    best_features = [fields.field_name(field_ids[i]) for (i, score)
                     in enumerate(best_state) if score]
    message = ('The best feature subset is: %s \n'
               % ", ".join(best_features))
    u.log_message(message, log_file=args.session_file, console=1)
    message = ('%s = %0.2f%%\n' % (measurement, (best_accuracy * 100)))
    u.log_message(message, log_file=args.session_file, console=1)
    message = ('Evaluated %d/%d feature subsets\n' %
               ((len(open_list) + len(closed_list)), 2 ** len(field_ids)))
    u.log_message(message, log_file=args.session_file, console=1)


def kfold_evaluate(datasets_file, api, args, counter, common_options,
                   penalty=DEFAULT_PENALTY,
                   measurement=ACCURACY):
    """Scoring k-fold cross-validation using the given feature subset

    """
    # create evaluation with input_fields
    args.output_dir = "%s%skfold" % (u.check_dir(datasets_file), os.sep)
    evaluation = create_kfold_evaluations(datasets_file, args,
                                          counter, common_options)

    evaluation = evaluation.get('model', {})
    avg_measurement = AVG_PREFIX % measurement
    if not avg_measurement in evaluation:
        avg_measurement = AVG_PREFIX % R_SQUARED
        if not avg_measurement in evaluation:
            sys.exit("Failed to find %s or r-squared in the evaluation"
                     % measurement)
    return (evaluation[avg_measurement] -
            penalty * len(args.model_fields.split(",")),
            measurement.capitalize())
