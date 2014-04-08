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

ACCURACY = "phi"

EXTENDED_DATASET = "kfold_dataset.json"
TEST_DATASET = "kfold_dataset-%s.json"

SELECTING_KFOLD = '["%s", %s, ["field", "%s"]]'
NEW_FIELD = '{"new_fields": [{"name": "%s", "field": "(rand-int %s)"}]}'

COMMAND_EXTENDED = ("main --dataset %s --new-field %s --no-model --output-dir "
                    "%s%sextended")
COMMAND_SELECTION = ("main --dataset %s --json-filter %s --no-model"
                     " --output-dir %s%s%s --objective %s --dataset-fields=-%s")
COMMAND_CREATE_CV = ("main --datasets %s --output-dir %s"
                     " --dataset-off --evaluate")
DEFAULT_KFOLD_FIELD = "__kfold__"

# difference needed to become new best node
EPSILON = 0.001

# per feature score penalty
DEFAULT_PENALTY = 0.001

# staleness
DEFAULT_STALENESS = 0.001


def create_kfold_cv(args, api):
    """Creates the kfold cross-validation

    """
    datasets_file = create_kfold_datasets_file(args, api)
    if datasets_file is not None:
        create_kfold_evaluations(
            datasets_file, "%s%sk_fold" % (u.check_dir(datasets_file), os.sep),
            model_fields=args.model_fields)


def create_features_analysis(args, api):
    """Analyzes the features in the dataset to find the ones that
       optimize the model performance

    """
    datasets_file = create_kfold_datasets_file(args, api)
    best_first_search(datasets_file, api, args, staleness=args.staleness,
                      penalty=args.penalty)


def create_kfold_datasets_file(args, api):
    """Create the kfold dataset resources and store their ids in a file
       one per line

    """
    if args.output_dir is None:
        args.output_dir = a.NOW
    # retrieve dataset
    dataset_id = bigml.api.get_dataset_id(args.dataset)
    if dataset_id:
        dataset = api.check_resource(dataset_id, api.get_dataset)
        # check that kfold_field is unique
        fields = Fields(dataset, {"objective_field": args.objective_field,
                                  "objective_field_present": True})
        fields.objective_field
        kfold_field_name = avoid_duplicates(DEFAULT_KFOLD_FIELD, fields)
        # creating auxiliar json files to generate test datasets
        extended_file, selecting_file_list = create_kfold_json(
            args.output_dir, kfold_field=kfold_field_name, k=args.k_folds)
        # generate test datasets, models and evaluations
        datasets_file = create_kfold_datasets(dataset_id, args.output_dir,
                                              args.k_folds,
                                              extended_file,
                                              selecting_file_list,
                                              fields.objective_field,
                                              kfold_field_name)
        return datasets_file 
    return None    


def create_kfold_json(output_dir, kfold_field=DEFAULT_KFOLD_FIELD,
                      k=5):
    """Create the files to generate a new field with a random integer from
       0 to k-1, and a filter file for each of these indexes.

    """

    new_file = NEW_FIELD % (kfold_field, k)
    try:
        extended_file = "%s%s%s" % (output_dir, os.sep, EXTENDED_DATASET) 
        with open(extended_file, "w") as extended_dataset:
            extended_dataset.write(new_file)
        selecting_file_list = []
        selecting_out_file_list = []
        for index in range(0, k):
            selecting_file = TEST_DATASET % index
            selecting_file =  "%s%s%s" % (output_dir, os.sep, selecting_file)
            selecting_file_list.append(selecting_file)
            with open(selecting_file, "w") as test_dataset:
                test_dataset.write(SELECTING_KFOLD % ("!=", index,
                                                      kfold_field))
        return (extended_file, selecting_file_list)
    except IOError:
        sys.exit("Could not create the necessary files.")


def avoid_duplicates(field_name, fields, affix="_"):
    """Checks if a field name exists already in a fields structure.

    """
    if any([field['name'] == field_name
            for _, field in fields.fields.items()]):
        return avoid_duplicates(field_name, fields, affix=affix)
    return field_name


def create_kfold_datasets(dataset, output_dir, k, extended_file,
                          selecting_file_list, objective, kfold_field):
    """Calling the bigmler procedure to create the k-fold datasets

    """
    # creating the extended dataset
    extended_dataset_file = "%s%sextended%sdataset_gen" % (output_dir, os.sep,
                                                           os.sep)
    command = COMMAND_EXTENDED % (dataset, extended_file,
                                  output_dir, os.sep)
    main_dispatcher(args=command.split())
    # getting the extended dataset id
    with open(extended_dataset_file, "r") as extended_handler:
        extended_dataset_id = extended_handler.readline().strip()
    # creating the selecting datasets
    for index in range(0, len(selecting_file_list)):
        command = COMMAND_SELECTION % (
            extended_dataset_id, selecting_file_list[index],
            output_dir, os.sep, "test", objective, kfold_field)
        print command
        main_dispatcher(args=(COMMAND_SELECTION % (
            extended_dataset_id, selecting_file_list[index],
            output_dir, os.sep, "test", objective, kfold_field)).split())
    # creating the models from the datasets' files (multidatasets excluding
    # one test dataset at a time)
    datasets_directory = "%s%stest%s" % (output_dir, os.sep, os.sep)
    datasets_file = "%sdataset_gen" % datasets_directory
    return datasets_file


def create_kfold_evaluations(datasets_file, output_dir, model_fields=None):
    """ Create k-fold cross-validation from a datasets file

    """

    command = COMMAND_CREATE_CV % (datasets_file, output_dir)
    command_list = command.split()
    if model_fields is not None:
        command_list.append("--model-fields")
        command_list.append(model_fields)
    print command_list
    main_dispatcher(args=command_list)
    evaluation_file = "%s%sevaluation.json" % (output_dir, os.sep)
    print evaluation_file
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
    """Get all connected nodes

    """
    children = []
    for i in range(len(parent)):
        child = copy(parent)
        child[i] = not child[i]
        children.append(child)
    return children


def best_first_search(datasets_file, api, args,
                      staleness=None, penalty=None):
    """Selecting the fields to be used in the model construction

    """
    if staleness is None:
        staleness = DEFAULT_STALENESS
    if penalty is None:
        penalty = DEFAULT_PENALTY
    # retrieving the first dataset in the file
    try:
        with open(datasets_file) as datasets_handler:
            dataset_id = datasets_handler.readline().strip()
    except IOError:
        sys.exit("Could not read the generated datasets file.")
    dataset = api.check_resource(dataset_id, api.get_dataset)
    # initial feature set
    fields = Fields(dataset)
    objective_id = fields.field_id(fields.objective_field)
    field_ids = [field_id for field_id in fields.preferred_fields()
                 if field_id != objective_id]
    initial_state = [False for field_id in field_ids]
    open_list = [(initial_state,0)]
    closed_list = []
    best_accuracy = -1
    best_unchanged_count = 0
    while best_unchanged_count < staleness:
        (state, score) = find_max_state(open_list)
        state_ids = [field_ids[i] for (i, val) in enumerate(state) if val]
        print "state_ids:", state_ids
        print "score:", score
        print('Max state is: %s\n Accuracy = %f' % (state_ids, score))
        closed_list.append((state, score))
        open_list.remove((state, score))
        if (score - EPSILON) > best_accuracy:
            best_state = state
            best_accuracy = score
            best_unchanged_count = 0
            print('new best state')
        else:
            best_unchanged_count += 1

        children = expand_state(state)
        for child in children:
            if (child not in [state for state, _ in open_list]
                    and child not in [state for state, _ in closed_list]):
                input_fields = [fields.field_name(field_id) for (i, field_id)
                                in enumerate(field_ids) if child[i]]
                print('Evaluating %s' % input_fields)
                # create models and evaluation with input_fields
                score = kfold_evaluate(datasets_file, api,
                                       model_fields=",".join(input_fields),
                                       penalty=penalty)
                open_list.append((child, score))

    best_features = [fields.field_name(field_ids[i]) for (i, score)
                     in enumerate(best_state) if score]
    print('The best feature subset is: %s \n Accuracy = %0.2f%%'
          % (best_features, best_accuracy*100))
    print('Evaluated %d/%d feature subsets' %
          ((len(open_list) + len(closed_list)), 2**len(field_ids)))


def kfold_evaluate(datasets_file, api, model_fields=None, 
                   penalty=DEFAULT_PENALTY,
                   measurement=ACCURACY):
    """Scoring k-fold cross-validation using the given feature subset

    """
    # create evaluation with input_fields
    evaluation = create_kfold_evaluations(
        datasets_file, "%s%skfold" % (u.check_dir(datasets_file), os.sep),
        model_fields=model_fields)

    evaluation = evaluation.get('model', {})
    measurement = "average_%s" % measurement
    if measurement in evaluation:
        return (evaluation[measurement] -
                penalty * len(model_fields.split(",")))
    else:
        sys.exit("Failed to find %s in the evaluation" % measurement)
