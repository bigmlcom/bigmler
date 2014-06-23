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
from bigmler.options.analyze import ACCURACY

AVG_PREFIX = "average_%s"
R_SQUARED = "r_squared"

EXTENDED_DATASET = "kfold_dataset.json"
TEST_DATASET = "kfold_dataset-%s.json"

NEW_FIELD = ('{"row_offset": %s, "row_step": %s,'
             ' "new_fields": [{"name": "%s", "field": "%s"}],'
             ' "objective_field": {"id": "%s"}}')

COMMANDS = {"selection":
                "main --dataset %s --new-field %s --no-model --output-dir %s",
            "objective":
                ("main --dataset %s --no-model --name %s "
             "--output-dir %s"),
            "create_cv":
                ("main --datasets %s --output-dir %s --dataset-off --evaluate"
             " --name %s"),
            "node_threshold":
                ("main --datasets %s --node-threshold %s --output-dir %s"
                 " --dataset-off --evaluate")}

DEFAULT_KFOLD_FIELD = "__kfold__"
KFOLD_SUBDIR = "k_fold"
DEFAULT_MIN_NODES = 3
DEFAULT_NODES_STEP = 100
PERCENT_EVAL_METRICS = [ACCURACY, "precision", "recall"]

# difference needed to become new best node
EPSILON = 0.001

# per feature score penalty
DEFAULT_PENALTY = 0.001

# per node score penalty
DEFAULT_NODES_PENALTY = 0

# staleness
DEFAULT_STALENESS = 5

# k-fold
DEFAULT_KFOLDS = 5

#subcommands
SUBCOMMAND_LOG = ".bigmler_subcmd"
SESSIONS_LOG = "bigmler_sessions"

#name max length
NAME_MAX_LENGTH = 127

subcommand_list = []
subcommand_file = None
session_file = None


def set_subcommand_file(output_dir):
    """Creates the subcommand file in the output_dir directory

    """
    global subcommand_file
    global session_file
    subcommand_file = os.path.join(output_dir, SUBCOMMAND_LOG)
    session_file = os.path.join(output_dir, SESSIONS_LOG)


def retrieve_subcommands():
    """Retrieves the executed subcommands in inverse order

    """
    global subcommand_list
    subcommand_list = open(subcommand_file).readlines()
    subcommand_list.reverse()

def create_kfold_cv(args, api, common_options, resume=False):
    """Creates the kfold cross-validation

    """
    set_subcommand_file(args.output_dir)
    if resume:
        retrieve_subcommands()
    datasets_file, objective_name, resume = create_kfold_datasets_file(
        args, api, common_options, resume=resume)
    if datasets_file is not None:
        args.output_dir = os.path.join(u.check_dir(datasets_file),
                                       KFOLD_SUBDIR)
        message = ('Creating the kfold evaluations.........\n')
        u.log_message(message, log_file=session_file,
                      console=args.verbosity)
        create_kfold_evaluations(datasets_file, args, common_options,
                                 resume=resume)


def create_features_analysis(args, api, common_options, resume=False):
    """Analyzes the features in the dataset to find the ones that
       optimize the model performance

    """
    set_subcommand_file(args.output_dir)
    if resume:
        retrieve_subcommands()
    datasets_file, objective_name, resume = create_kfold_datasets_file(
        args, api, common_options, resume=resume)
    message = ('Creating the best features set..........\n')
    u.log_message(message, log_file=session_file,
                  console=args.verbosity)
    best_first_search(datasets_file, api, args, common_options,
                      staleness=args.staleness,
                      penalty=args.penalty,
                      objective_name=objective_name, resume=resume)


def create_nodes_analysis(args, api, common_options, resume=False):
    """Analyzes the model performace as a function of node threshold.

    """
    set_subcommand_file(args.output_dir)
    if resume:
        retrieve_subcommands()
    datasets_file, objective_name, resume = create_kfold_datasets_file(
        args, api, common_options, resume=resume)
    message = ('Creating the node threshold set..........\n')
    u.log_message(message, log_file=session_file,
                  console=args.verbosity)
    best_node_threshold(datasets_file, api, args, common_options,
                        staleness=args.staleness,
                        penalty=args.penalty,
                        objective_name=objective_name, resume=resume)


def create_kfold_datasets_file(args, api, common_options, resume=False):
    """Create the kfold dataset resources and store their ids in a file
       one per line

    """
    message = ('Creating the kfold datasets............\n')
    u.log_message(message, log_file=session_file, console=args.verbosity)
    if args.output_dir is None:
        args.output_dir = a.NOW
    # retrieve dataset
    dataset_id = bigml.api.get_dataset_id(args.dataset)
    if dataset_id:
        dataset = api.check_resource(dataset_id, api.get_dataset)
        try:
            args.objective_field = int(args.objective_field)
        except (TypeError, ValueError):
            pass
        # if the user provided no objective field, try to use the one in the
        # dataset
        if args.objective_field is None:
            try:
                args.objective_field = dataset['object'][
                    'objective_field']['column_number']
            except KeyError:
                pass
        # check that kfold_field is unique
        fields = Fields(dataset, objective_field=args.objective_field,
                                 objective_field_present=True)
        objective_id = fields.field_id(fields.objective_field)
        objective_name = fields.field_name(objective_id)
        kfold_field_name = avoid_duplicates(DEFAULT_KFOLD_FIELD, fields)
        # create jsons to generate partial datasets
        selecting_file_list, resume = create_kfold_json(args, kfold_field_name,
                                                        objective_id,
                                                        resume=resume) 
        # generate test datasets
        datasets_file, resume = create_kfold_datasets(dataset_id, args,
                                                      selecting_file_list,
                                                      objective_name,
                                                      kfold_field_name,
                                                      common_options,
                                                      resume=resume)
        return datasets_file, objective_name, resume
    return None, None, None    


def create_kfold_json(args, kfold_field=DEFAULT_KFOLD_FIELD,
                      objective_field=None, resume=False):
    """Create the files to generate a new field with a random integer from
       0 to k-1, and a filter file for each of these indexes.

    """
    output_dir = args.output_dir 
    k = args.k_folds if args.k_folds else DEFAULT_KFOLDS
    try:
        selecting_file_list = []
        for index in range(0, k):
            new_field = NEW_FIELD % (index, k, kfold_field,
                                     index, objective_field)
            selecting_file = TEST_DATASET % index
            selecting_file = os.path.join(output_dir, selecting_file)
            selecting_file_list.append(selecting_file)
            # When resuming, check if the file already exists
            if not resume or not os.path.isfile(selecting_file):
                resume = False
                with open(selecting_file, "w") as test_dataset:
                    test_dataset.write(new_field)
        return selecting_file_list, resume
    except IOError:
        sys.exit("Could not create the necessary files.")


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
                          common_options, resume=False):
    """Calling the bigmler procedure to create the k-fold datasets

    """
    args.output_dir = os.path.join(args.output_dir, "test")
    output_dir = args.output_dir
    k = args.k_folds
    global subcommand_list
    # creating the selecting datasets
    for index in range(0, len(selecting_file_list)):
        command = COMMANDS["selection"] % (
            dataset, selecting_file_list[index],
            output_dir)
        command_args = command.split()
        common_options_list = u.get_options_list(args, common_options,
                                                 prioritary=command_args)
        command_args.extend(common_options_list)
        command = " ".join(command_args)
        if resume:
            next_command = subcommand_list.pop().strip()
            if next_command != command:
                resume = False
                u.log_message("%s\n" % command, log_file=subcommand_file,
                              console=False)
                main_dispatcher(args=command_args)
            elif not subcommand_list:
                main_dispatcher(args=['main', '--resume'])
                resume = False
        else:
            u.log_message("%s\n" % command, log_file=subcommand_file,
                          console=False)
            main_dispatcher(args=command_args)
    # updating the datasets to set the objective field
    datasets_file = os.path.join(output_dir, "dataset_gen")
    with open(datasets_file) as datasets_handler:
        for line in datasets_handler:
            dataset_id = line.strip()
            command = COMMANDS["objective"] % (dataset_id,
                                              "dataset_%s" % index, output_dir)
            command_args = command.split()
            command_args.append("--objective")
            command_args.append(objective)
            common_options_list = u.get_options_list(args, common_options,
                                                     prioritary=command_args)
            command_args.extend(common_options_list)
            command = " ".join(command_args)
            if resume:
                next_command = subcommand_list.pop().strip()
                if next_command != command:
                    resume = False
                    u.log_message("%s\n" % command, log_file=subcommand_file,
                                  console=False)
                    main_dispatcher(args=command_args)
                elif not subcommand_list:
                    main_dispatcher(args=['main', '--resume'])
                    resume = False
            else:
                u.log_message("%s\n" % command, log_file=subcommand_file,
                              console=False)
                main_dispatcher(args=command_args)

    return datasets_file, resume


def create_kfold_evaluations(datasets_file, args, common_options,
                             resume=False, counter=0):
    """ Create k-fold cross-validation from a datasets file

    """
    global subcommand_list
    output_dir = u.check_dir(os.path.join("%s%s" % (args.output_dir, counter),
                                          "evaluation.json"))
    model_fields = args.model_fields
    name_suffix = "_subset_%s" % counter
    name_max_length = NAME_MAX_LENGTH - len(name_suffix)
    name = "%s%s" % (args.name[0: name_max_length] , name_suffix)
    command = COMMANDS["create_cv"] % (datasets_file, output_dir, name)
    command_args = command.split()
    if model_fields:
        command_args.append("--model-fields")
        command_args.append(model_fields)
    common_options_list = u.get_options_list(args, common_options,
                                             prioritary=command_args)
    command_args.extend(common_options_list)
    command = " ".join(command_args)
    if resume:
        next_command = subcommand_list.pop().strip()
        if next_command != command:
            resume = False
            u.log_message("%s\n" % command, log_file=subcommand_file,
                          console=False)
            main_dispatcher(args=command_args)
        elif not subcommand_list:
            main_dispatcher(args=['main', '--resume'])
            resume = False
    else:
        u.log_message("%s\n" % command, log_file=subcommand_file,
                      console=False)
        main_dispatcher(args=command_args)   
    evaluation_file = os.path.join(output_dir, "evaluation.json")
    try:
        with open(evaluation_file) as evaluation_handler:
            evaluation = json.loads(evaluation_handler.read())
        return evaluation, resume
    except (ValueError, IOError):
        sys.exit("Failed to retrieve evaluation.")


def find_max_state(states):
    maxval = -1
    maxstate = None
    for (v,f) in states:
        if f > maxval:
            maxstate = v
            maxval = f
    return maxstate, maxval


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
                      staleness=None, penalty=None, objective_name=None,
                      resume=False):
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
    excluded_features = ([] if args.exclude_features is None else
                         args.exclude_features.decode("utf8").split(
                             args.args_separator))
    excluded_ids = [fields.field_id(feature) for
                    feature in excluded_features]
    objective_id = fields.field_id(objective_name)
    field_ids = [field_id for field_id in fields.preferred_fields()
                 if field_id != objective_id and
                 not field_id in excluded_ids]
    initial_state = [False for field_id in field_ids]
    open_list = [(initial_state, 0)]
    closed_list = []
    best_score = -1
    best_unchanged_count = 0
    metric = args.maximize
    while best_unchanged_count < staleness and open_list:
        (state, score) = find_max_state(open_list)
        state_fields = [fields.field_name(field_ids[i])
                        for (i, val) in enumerate(state) if val]
        closed_list.append((state, score))
        open_list.remove((state, score))
        if (score - EPSILON) > best_score:
            best_state = state
            best_score = score
            best_unchanged_count = 0
            if state_fields:
                message = 'New best state: %s\n' % (state_fields)
                u.log_message(message, log_file=session_file,
                              console=args.verbosity)
                if metric in PERCENT_EVAL_METRICS:
                    message = '%s = %0.2f%%\n' % (metric.capitalize(),
                                                  score * 100)
                else:
                    message = '%s = %f\n' % (metric.capitalize(),
                                                  score)
                u.log_message(message, log_file=session_file,
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
                args.model_fields = args.args_separator.join(input_fields)
                counter += 1
                (score, metric,
                 resume) = kfold_evaluate(datasets_file, api,
                                          args, counter, common_options,
                                          penalty=penalty, resume=resume,
                                          metric=metric)
                open_list.append((child, score))

    best_features = [fields.field_name(field_ids[i]) for (i, score)
                     in enumerate(best_state) if score]
    message = ('The best feature subset is: %s \n'
               % ", ".join(best_features))
    u.log_message(message, log_file=session_file, console=1)
    if metric in PERCENT_EVAL_METRICS:
        message = ('%s = %0.2f%%\n' % (metric.capitalize(), (best_score * 100)))
    else:
        message = ('%s = %f\n' % (metric.capitalize(), best_score))
    u.log_message(message, log_file=session_file, console=1)
    message = ('Evaluated %d/%d feature subsets\n' %
               ((len(open_list) + len(closed_list)), 2 ** len(field_ids)))
    u.log_message(message, log_file=session_file, console=1)


def kfold_evaluate(datasets_file, api, args, counter, common_options,
                   penalty=DEFAULT_PENALTY,
                   metric=ACCURACY, resume=False):
    """Scoring k-fold cross-validation using the given feature subset

    """
    # create evaluation with input_fields
    args.output_dir = os.path.join(u.check_dir(datasets_file), "kfold")
    evaluation, resume = create_kfold_evaluations(datasets_file, args,
                                                  common_options,
                                                  resume=resume,
                                                  counter=counter)

    evaluation = evaluation.get('model', {})
    avg_metric = AVG_PREFIX % metric
    metric_literal = metric
    if not avg_metric in evaluation:
        avg_metric = AVG_PREFIX % R_SQUARED
        metric_literal = R_SQUARED
        if not avg_metric in evaluation:
            sys.exit("Failed to find %s or r-squared in the evaluation"
                     % metric)
    return (evaluation[avg_metric] -
            penalty * len(args.model_fields.split(args.args_separator)),
            metric_literal, resume)


def best_node_threshold(datasets_file, api, args, common_options,
                        staleness=None, penalty=None, objective_name=None,
                        resume=False):
    """Selecting the node_limit to be used in the model construction

    """
    args.output_dir = os.path.join(args.output_dir, "node_th")
    max_nodes = args.max_nodes + 1
    if args.min_nodes is None:
        args.min_nodes = DEFAULT_MIN_NODES
    if args.nodes_step is None:
        args.nodes_step = DEFAULT_NODES_STEP
    node_threshold = args.min_nodes
    if staleness is None:
        staleness = DEFAULT_STALENESS
    if penalty is None:
        penalty = DEFAULT_NODES_PENALTY
    best_score = -1
    best_unchanged_count = 0
    metric = args.maximize
    score = best_score
    while best_unchanged_count < staleness and node_threshold < max_nodes:
        (score, metric,
         resume) = node_threshold_evaluate(
            datasets_file, api, args, node_threshold, common_options,
            penalty=penalty, resume=resume, metric=metric)
        if (score - EPSILON) > best_score:
            best_threshold = node_threshold
            best_score = score
            best_unchanged_count = 0
            message = 'New best node threshold: %s\n' % (best_threshold)
            u.log_message(message, log_file=session_file,
                          console=args.verbosity)
            if metric in PERCENT_EVAL_METRICS:
                message = '%s = %0.2f%%\n' % (metric.capitalize(),
                                              score * 100)
            else:
                message = '%s = %f\n' % (metric.capitalize(),
                                              score)
            u.log_message(message, log_file=session_file,
                          console=args.verbosity)
        else:
            best_unchanged_count += 1
        node_threshold += args.nodes_step
       


    message = ('The best node threshold is: %s \n'
               % best_threshold)
    u.log_message(message, log_file=session_file, console=1)
    if metric in PERCENT_EVAL_METRICS:
        message = ('%s = %0.2f%%\n' % (metric.capitalize(),
                                       (best_score * 100)))
    else:
        message = ('%s = %f\n' % (metric.capitalize(), best_score))
    u.log_message(message, log_file=session_file, console=1)


def node_threshold_evaluate(datasets_file, api, args, node_threshold,
                            common_options, penalty=DEFAULT_NODES_PENALTY,
                            metric=ACCURACY, resume=False):
    """Scoring node_threshold created models

    """
    # create evaluation with input_fields
    evaluation, resume = create_node_th_evaluations(
        datasets_file, args, common_options, resume=resume,
        node_threshold=node_threshold)

    evaluation = evaluation.get('model', {})
    avg_metric = AVG_PREFIX % metric
    metric_literal = metric
    if not avg_metric in evaluation:
        avg_metric = AVG_PREFIX % R_SQUARED
        metric_literal = R_SQUARED
        if not avg_metric in evaluation:
            sys.exit("Failed to find %s or r-squared in the evaluation"
                     % metric)
    return (evaluation[avg_metric] - penalty * node_threshold,
            metric_literal, resume)


def create_node_th_evaluations(datasets_file, args, common_options,
                               resume=False,
                               node_threshold=DEFAULT_MIN_NODES):
    """ Create node_threshold evaluations

    """
    global subcommand_list
    output_dir = u.check_dir(
        os.path.join("%s%s" % (args.output_dir, node_threshold),
                     "evaluation.json"))
    command = COMMANDS["node_threshold"] % (
        datasets_file, node_threshold, output_dir)
    command_args = command.split()
    common_options_list = u.get_options_list(args, common_options,
                                             prioritary=command_args)
    command_args.extend(common_options_list)
    command = " ".join(command_args)
    if resume:
        next_command = subcommand_list.pop().strip()
        if next_command != command:
            resume = False
            u.log_message("%s\n" % command, log_file=subcommand_file,
                          console=False)
            main_dispatcher(args=command_args)
        elif not subcommand_list:
            main_dispatcher(args=['main', '--resume'])
            resume = False
    else:
        u.log_message("%s\n" % command, log_file=subcommand_file,
                      console=False)
        main_dispatcher(args=command_args)   
    evaluation_file = os.path.join(output_dir, "evaluation.json")
    try:
        with open(evaluation_file) as evaluation_handler:
            evaluation = json.loads(evaluation_handler.read())
        return evaluation, resume
    except (ValueError, IOError):
        sys.exit("Failed to retrieve evaluation.")
