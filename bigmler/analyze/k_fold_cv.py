# -*- coding: utf-8 -*-
#
# Copyright 2012-2020 BigML
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



import os
import sys
import json
import re

from copy import copy

import bigml

from bigml.fields import Fields
from bigml.io import UnicodeWriter

import bigmler.processing.args as a
import bigmler.utils as u

from bigmler.dispatcher import main_dispatcher
from bigmler.options.analyze import ACCURACY, MINIMIZE_OPTIONS
from bigmler.resourcesapi.common import ALL_FIELDS_QS

AVG_PREFIX = "average_%s"
R_SQUARED = "r_squared"
PER_CLASS = "per_class_statistics"

EXTENDED_DATASET = "kfold_dataset.json"
TEST_DATASET = "kfold_dataset-%s.json"

NEW_FIELD = ('{"row_offset": %s, "row_step": %s,'
             ' "new_fields": [{"name": "%s", "field": "%s"}],'
             ' "objective_field": {"id": "%s"}}')


COMMANDS = {"selection":
                ("main --dataset %s --new-field %s --no-model --output-dir %s"
                 " --store"),
            "create_cv":
                ("main --datasets %s --output-dir %s --dataset-off --evaluate"
                 " --name %s --dataset-file %s"),
            "node_threshold":
                ("main --datasets %s --node-threshold %s --output-dir %s"
                 " --dataset-off --evaluate"),
            "random_candidates":
                ("main --datasets %s --random-candidates %s --output-dir %s"
                 " --randomize --dataset-off --evaluate"),
            "prediction":
                ("main --test-datasets %s/dataset_gen"
                 " --%s %s/%s"
                 " --dataset-off --remote --output-dir %s_pred"
                 " --prediction-info full --prediction-header --to-dataset")}

DEFAULT_KFOLD_FIELD = "__kfold__"
KFOLD_SUBDIR = "k_fold"
DEFAULT_MIN_NODES = 3
DEFAULT_NODES_STEP = 100
DEFAULT_MIN_CANDIDATES = 1
DEFAULT_CANDIDATES_STEP = 1
PERCENT_EVAL_METRICS = [ACCURACY, "precision", "recall"]

# difference needed to become new best node
EPSILON = 0.001

# per feature score penalty
DEFAULT_PENALTY = 0.001

# per node score penalty
DEFAULT_NODES_PENALTY = 0

# per candidate score penalty
DEFAULT_CANDIDATES_PENALTY = 0

# staleness
DEFAULT_STALENESS = 5

# k-fold
DEFAULT_KFOLDS = 5

#subcommands
SUBCOMMAND_LOG = ".bigmler_subcmd"
SESSIONS_LOG = "bigmler_sessions"
FEATURES_LOG = "features_sets.csv"
NODES_LOG = "nodes_sets.csv"
CANDIDATES_LOG = "random_candidate_sets.csv"

#name max length
NAME_MAX_LENGTH = 127

#default number of models for --random-fields random forests
DEFAULT_NUMBER_OF_MODELS = 10

# CSV summary files headers
FEATURES_HEADER = ["step", "state", "score", "metric_value", "best_score"]
NODES_HEADER = ["step", "node_threshold", "score", "metric_value",
                "best_score"]
CANDIDATES_HEADER = ["step", "random_candidates", "score", "metric_value",
                     "best_score"]

subcommand_list = []
subcommand_file = None
session_file = None


def set_subcommand_file(output_dir):
    """Creates the subcommand file in the output_dir directory

    """
    global subcommand_file
    global session_file
    subcommand_file = os.path.normpath(os.path.join(output_dir,
                                                    SUBCOMMAND_LOG))
    session_file = os.path.normpath(os.path.join(output_dir, SESSIONS_LOG))

def retrieve_subcommands():
    """Retrieves the executed subcommands in inverse order

    """
    global subcommand_list
    subcommand_list = open(subcommand_file, u.open_mode("r")).readlines()
    subcommand_list.reverse()


def rebuild_command(args):
    """Rebuilds a unicode command string prepared to be stored in a file

    """
    return "%s\n" % (" ".join(args)).replace("\\", "\\\\")


def different_command(next_command, command):
    if next_command == command:
        return False
    else:
        if 'name=BigMLer_' in command:
            # the difference may be due to the timestamp of default name
            # parameter
            pattern = re.compile(r'name=Bigmler_[^\s]+')
            return re.sub(pattern, "", next_command) == re.sub(pattern,
                                                               "", command)
        return False


def create_prediction_dataset(base_path, folder, args, resume):
    """Creates batch prediction datasets and a multidataset with the prediction
    results for the best scoring model in the folder set by the argument

    """
    args.output_dir = os.path.join(base_path, "%s_pred" % folder)
    folder = os.path.join(base_path, folder)
    model_type = "ensembles" if hasattr(args, "number_of_models") and \
        args.number_of_models > 1 else "models"
    global subcommand_list
    # creating the predictions CSV file
    command = COMMANDS["prediction"] % (base_path, model_type, folder,
                                        model_type, folder)
    command_args = command.split()
    if resume:
        next_command = subcommand_list.pop()
        if different_command(next_command, command):
            resume = False
            u.sys_log_message(command, log_file=subcommand_file)
            main_dispatcher(args=command_args)
        elif not subcommand_list:
            main_dispatcher(args=['main', '--resume'])
            resume = False
    else:
        u.sys_log_message(command, log_file=subcommand_file)
        main_dispatcher(args=command_args)
    return resume


def create_kfold_cv(args, api, command_obj, resume=False):
    """Creates the kfold cross-validation

    """
    set_subcommand_file(args.output_dir)
    if resume:
        retrieve_subcommands()
    datasets_file, objective_name, resume = create_kfold_datasets_file(
        args, api, command_obj, resume=resume)
    if datasets_file is not None:
        args.output_dir = os.path.normpath(
            os.path.join(u.check_dir(datasets_file),
                         KFOLD_SUBDIR))
        message = ('Creating the kfold evaluations.........\n')
        u.log_message(message, log_file=session_file,
                      console=args.verbosity)
        args.objective_field = objective_name
        create_kfold_evaluations(datasets_file, args, command_obj,
                                 resume=resume)


def create_features_analysis(args, api, command_obj, resume=False):
    """Analyzes the features in the dataset to find the ones that
       optimize the model performance

    """
    set_subcommand_file(args.output_dir)
    output_dir = args.output_dir
    if resume:
        retrieve_subcommands()
    datasets_file, objective_name, resume = create_kfold_datasets_file(
        args, api, command_obj, resume=resume)
    args.objective_field = objective_name
    message = ('Creating the best features set..........\n')
    u.log_message(message, log_file=session_file,
                  console=args.verbosity)
    model_fields = best_first_search(
        datasets_file, api, args, command_obj,
        staleness=args.staleness,
        penalty=args.penalty,
        objective_name=objective_name, resume=resume)

    # showing the instruction to create the complete model with the
    # selected feature subset
    bigmler_command = 'bigmler --dataset %s --model-fields="%s"' % ( \
        args.dataset, ",".join(model_fields))
    if args.number_of_models > 1:
        bigmler_command = "%s --number-of-models %s" % ( \
            bigmler_command, args.number_of_models)
    connection_args = command_obj.propagate([], connection_only=True)
    bigmler_command = "%s %s" % (bigmler_command, " ".join(connection_args))
    message = ('To create the final model with the entire dataset using '
               'the selected feature subset use:\n%s\n\n' %
               bigmler_command)
    u.log_message(message, log_file=session_file, console=1)
    # showing the instruction to delete the user-given output-dir
    bigmler_command = ('bigmler delete --from-dir %s') % (
        output_dir)
    bigmler_command = "%s %s" % (bigmler_command, " ".join(connection_args))
    message = ('To delete all the resources generated by this analyze'
               ' subcommand use:\n%s\n\n') % bigmler_command
    u.log_message(message, log_file=session_file, console=1)



def create_nodes_analysis(args, api, command_obj, resume=False):
    """Analyzes the model performance as a function of node threshold.

    """
    set_subcommand_file(args.output_dir)
    output_dir = args.output_dir
    if resume:
        retrieve_subcommands()
    datasets_file, objective_name, resume = create_kfold_datasets_file(
        args, api, command_obj, resume=resume)
    args.objective_field = objective_name
    message = ('Creating the node threshold set..........\n')
    u.log_message(message, log_file=session_file,
                  console=args.verbosity)
    node_threshold = best_node_threshold(
        datasets_file, args, command_obj,
        staleness=args.staleness,
        penalty=args.penalty,
        resume=resume)
    # showing the instruction to create the complete model with the
    # chosen node threshold
    bigmler_command = ('bigmler --dataset %s --node-threshold %s') % (
        args.dataset, node_threshold)
    message = ('To create the final model with the entire dataset using '
               'the selected maximum number of nodes use:\n%s\n\n' %
               bigmler_command)
    u.log_message(message, log_file=session_file, console=1)
    # showing the instruction to delete the user-given output-dir
    bigmler_command = ('bigmler delete --from-dir %s') % (
        output_dir)
    message = ('To delete all the resources generated by this analyze'
               ' subcommand use:\n%s\n\n') % bigmler_command
    u.log_message(message, log_file=session_file, console=1)


def create_kfold_datasets_file(args, api, command_obj, resume=False):
    """Create the kfold dataset resources and store their ids in a file
       one per line

    """
    message = ('Creating the kfold datasets............\n')
    u.log_message(message, log_file=session_file, console=args.verbosity)
    if args.output_dir is None:
        args.output_dir = a.NOW

    csv_properties = {}
    fields = None
    dataset = None
    datasets = []
    if args.dataset_file:
        # dataset is retrieved from the contents of the given local JSON file
        model_dataset, csv_properties, fields = u.read_local_resource(
            args.dataset_file,
            csv_properties=csv_properties)
        if not args.datasets:
            datasets = [model_dataset]
            dataset = model_dataset
        else:
            datasets = u.read_datasets(args.datasets)
        dataset_id = dataset['resource']
    elif args.dataset:
        dataset_id = bigml.api.get_dataset_id(args.dataset)
        datasets = [dataset_id]
    elif args.dataset_ids:
        datasets = args.dataset_ids
        dataset_id = datasets[0]

    if dataset_id:
        if not dataset:
            dataset = api.check_resource(dataset_id,
                                         query_string=ALL_FIELDS_QS)
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
        if args.random_fields:
            default_candidates_limits(args, fields)
        try:
            objective_id = fields.field_id(fields.objective_field)
            objective_name = fields.field_name(objective_id)
        except ValueError as exc:
            sys.exit(exc)
        kfold_field_name = avoid_duplicates(DEFAULT_KFOLD_FIELD, fields)
        # create jsons to generate partial datasets
        selecting_file_list, resume = create_kfold_json(args, kfold_field_name,
                                                        objective_id,
                                                        resume=resume)
        # generate test datasets
        datasets_file, resume = create_kfold_datasets(dataset_id, args,
                                                      selecting_file_list,
                                                      command_obj,
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
            selecting_file = os.path.normpath(os.path.join(output_dir,
                                                           selecting_file))
            selecting_file_list.append(selecting_file)
            # When resuming, check if the file already exists
            if not resume or not os.path.isfile(selecting_file):
                resume = False
                with open(selecting_file, u.open_mode("w")) as test_dataset:
                    test_dataset.write(new_field)
        return selecting_file_list, resume
    except IOError:
        sys.exit("Could not create the necessary files.")


def avoid_duplicates(field_name, fields, affix="_"):
    """Checks if a field name already exists in a fields structure.

    """
    if any([field['name'] == field_name
            for _, field in list(fields.fields.items())]):
        return avoid_duplicates("%s%s%s" % (affix, field_name, affix),
                                fields, affix=affix)
    return field_name


def create_kfold_datasets(dataset, args,
                          selecting_file_list,
                          command_obj, resume=False):
    """Calling the bigmler procedure to create the k-fold datasets

    """
    args.output_dir = os.path.normpath(os.path.join(args.output_dir, "test"))
    output_dir = args.output_dir
    global subcommand_list
    # creating the selecting datasets
    for index in range(0, len(selecting_file_list)):
        command = COMMANDS["selection"] % (
            dataset, selecting_file_list[index],
            output_dir)
        command_args = command.split()
        command_obj.propagate(command_args)
        command = rebuild_command(command_args)
        if resume:
            next_command = subcommand_list.pop()
            if different_command(next_command, command):
                resume = False
                u.sys_log_message(command, log_file=subcommand_file)
                main_dispatcher(args=command_args)
            elif not subcommand_list:
                main_dispatcher(args=['main', '--resume'])
                resume = False
        else:
            u.sys_log_message(command, log_file=subcommand_file)
            main_dispatcher(args=command_args)
    datasets_file = os.path.normpath(os.path.join(output_dir, "dataset_gen"))
    return datasets_file, resume


def add_model_options(command_args, args):
    """Adds the command options used to configure models or ensembles

    """
    if args.balance:
        command_args.append("--balance")
    if args.missing_splits:
        command_args.append("--missing-splits")
    if args.pruning:
        command_args.append("--pruning")
        command_args.append(args.pruning)
    if args.weight_field:
        command_args.append("--weight-field")
        command_args.append(args.weight_field)
    if args.objective_weights:
        command_args.append("--objective-weights")
        command_args.append(args.objective_weights)
    if args.model_attributes:
        command_args.append("--model-attributes")
        command_args.append(args.model_attributes)
    if args.number_of_models > 1:
        command_args.append("--number-of-models")
        command_args.append(str(args.number_of_models))
        # ensembles options
        if args.sample_rate < 1:
            command_args.append("--sample-rate")
            command_args.append(str(args.sample_rate))
        if args.replacement:
            command_args.append("--replacement")
        if not args.ensemble_sample_replacement:
            command_args.append("--ensemble-sample-no-replacement")
        if args.ensemble_sample_seed:
            command_args.append("--ensemble-sample-seed")
            command_args.append(args.ensemble_sample_seed)
        if args.ensemble_sample_rate < 1:
            command_args.append("--ensemble-sample-rate")
            command_args.append(str(args.ensemble_sample_rate))
        if args.randomize:
            command_args.append("--randomize")
        if args.ensemble_attributes:
            command_args.append("--ensemble-attributes")
            command_args.append(args.ensemble_attributes)
    return command_args


def create_kfold_evaluations(datasets_file, args, command_obj,
                             resume=False, counter=0):
    """ Create k-fold cross-validation from a datasets file

    """
    global subcommand_list
    output_dir = os.path.normpath(
        u.check_dir(os.path.join("%s%s" % (args.output_dir, counter),
                                 "evaluation.json")))
    model_fields = args.model_fields
    name_suffix = "_subset_%s" % counter
    name_max_length = NAME_MAX_LENGTH - len(name_suffix)
    name = "%s%s" % (args.name[0: name_max_length], name_suffix)
    dataset_id = u.read_datasets(datasets_file)[0]
    model_dataset = os.path.normpath(
        os.path.join(u.check_dir(datasets_file), dataset_id.replace("/", "_")))
    command = COMMANDS["create_cv"] % (datasets_file, output_dir, name,
                                       model_dataset)
    command_args = command.split()

    if model_fields:
        command_args.append("--model-fields")
        command_args.append(model_fields)
    command_args.append("--objective")
    command_args.append(args.objective_field)
    command_args = add_model_options(command_args, args)
    """
    common_options_list = u.get_options_list(args, command_obj.common_options,
                                             prioritary=command_args)
    command_args.extend(common_options_list)
    """
    command_obj.propagate(command_args, exclude=["--dataset",
                                                 "--datasets",
                                                 "--dataset-file"])
    command = rebuild_command(command_args)
    if resume:
        next_command = subcommand_list.pop()
        if different_command(next_command, command):
            resume = False
            u.sys_log_message(command, log_file=subcommand_file)
            main_dispatcher(args=command_args)
        elif not subcommand_list:
            main_dispatcher(args=['main', '--resume'])
            resume = False
    else:
        u.sys_log_message(command, log_file=subcommand_file)
        main_dispatcher(args=command_args)
    evaluation_file = os.path.normpath(os.path.join(output_dir,
                                                    "evaluation.json"))
    try:
        with open(evaluation_file) as evaluation_handler:
            evaluation = json.loads(evaluation_handler.read())
        return evaluation, resume
    except (ValueError, IOError):
        sys.exit("Failed to retrieve evaluation.")


def find_max_state(states_list):

    max_state, max_score, max_metric_value, max_counter = (
        None, - float('inf'), - float('inf'), 0)
    for (state, score, metric_value, counter) in states_list:
        if score > max_score or max_state is None and max_score == score:
            max_state, max_score, max_metric_value, max_counter = (
                state, score, metric_value, counter)
    return max_state, max_score, max_metric_value, max_counter


def expand_state(parent):
    """Get all connected states

    """
    children = []
    for i in range(len(parent)):
        child = copy(parent)
        child[i] = not child[i]
        children.append(child)
    return children


def best_first_search(datasets_file, api, args, command_obj,
                      staleness=None, penalty=None, objective_name=None,
                      resume=False):
    """Selecting the fields to be used in the model construction

    """
    counter = 0
    loop_counter = 0
    features_file = os.path.normpath(os.path.join(args.output_dir,
                                                  FEATURES_LOG))
    features_writer = UnicodeWriter(features_file).open_writer()
    features_header = FEATURES_HEADER
    if staleness is None:
        staleness = DEFAULT_STALENESS
    if penalty is None:
        penalty = DEFAULT_PENALTY
    # retrieving the first dataset in the file
    try:
        with open(datasets_file, u.open_mode("r")) as datasets_handler:
            dataset_id = datasets_handler.readline().strip()
    except IOError as exc:
        sys.exit("Could not read the generated datasets file: %s" %
                 str(exc))
    try:
        stored_dataset = u.storage_file_name(args.output_dir, dataset_id)
        with open(stored_dataset, u.open_mode("r")) as dataset_handler:
            dataset = json.loads(dataset_handler.read())
    except IOError:
        dataset = api.check_resource(dataset_id,
                                     query_string=ALL_FIELDS_QS)
    # initial feature set
    fields = Fields(dataset)
    excluded_features = ([] if args.exclude_features is None else
                         args.exclude_features.split(
                             args.args_separator))
    try:
        excluded_ids = [fields.field_id(feature) for
                        feature in excluded_features]
        objective_id = fields.field_id(objective_name)
    except ValueError as exc:
        sys.exit(exc)
    field_ids = [field_id for field_id in fields.preferred_fields()
                 if field_id != objective_id and
                 not field_id in excluded_ids]
    field_ids.sort()
    # headers are extended with a column per field
    fields_names = [fields.field_name(field_id) for field_id in field_ids]
    features_header.extend(fields_names)
    features_writer.writerow(features_header)
    initial_state = [False for field_id in field_ids]
    open_list = [(initial_state, - float('inf'), -float('inf'), 0)]
    closed_list = []
    best_state, best_score, best_metric_value, best_counter = open_list[0]
    best_unchanged_count = 0
    metric = args.optimize
    while best_unchanged_count < staleness and open_list:
        loop_counter += 1
        features_set = find_max_state(open_list)
        state, score, metric_value, _ = features_set
        if loop_counter > 1:
            csv_results = [loop_counter - 1, \
                [int(in_set) for in_set in state], \
                score, metric_value, best_score]
            csv_results.extend([int(in_set) for in_set in state])
            features_writer.writerow(csv_results)
        try:
            state_fields = [fields.field_name(field_ids[index])
                            for (index, in_set) in enumerate(state)
                            if in_set]
        except ValueError as exc:
            sys.exit(exc)
        closed_list.append(features_set)
        open_list.remove(features_set)
        if (score - EPSILON) > best_score:
            best_state, best_score, best_metric_value, best_counter = \
                features_set
            best_unchanged_count = 0
            if state_fields:
                message = 'New best state: %s\n' % (state_fields)
                u.log_message(message, log_file=session_file,
                              console=args.verbosity)
                if metric in PERCENT_EVAL_METRICS:
                    message = '%s = %0.2f%% (score = %s)\n' % (
                        metric.capitalize(), metric_value * 100, score)
                else:
                    message = '%s = %f (score = %s)\n' % (
                        metric.capitalize(), metric_value, score)
                u.log_message(message, log_file=session_file,
                              console=args.verbosity)
        else:
            best_unchanged_count += 1

        children = expand_state(state)
        for child in children:
            if (child not in [state for state, _, _, _ in open_list] and
                    child not in [state for state, _, _, _ in closed_list]):
                try:
                    # we need to keep names instead of IDs because
                    # IDs can change for different datasets
                    input_fields = [fields.field_name(field_id)
                                    for (i, field_id)
                                    in enumerate(field_ids) if child[i]]
                except ValueError as exc:
                    sys.exit(exc)
                # create models and evaluation with input_fields
                args.model_fields = args.args_separator.join(input_fields)
                counter += 1
                (score,
                 metric_value,
                 metric,
                 resume) = kfold_evaluate(datasets_file,
                                          args, counter, command_obj,
                                          penalty=penalty, resume=resume,
                                          metric=metric)
                open_list.append((child, score, metric_value, counter))
    try:
        best_features = [fields.field_name(field_ids[i]) for (i, score)
                         in enumerate(best_state) if score]
    except ValueError as exc:
        sys.exit(exc)
    message = ('The best feature subset is: %s \n'
               % ", ".join(best_features))
    u.log_message(message, log_file=session_file, console=1)
    if metric in PERCENT_EVAL_METRICS:
        message = ('%s = %0.2f%%\n' % (metric.capitalize(),
                                        (best_metric_value * 100)))
    else:
        message = ('%s = %f\n' % (metric.capitalize(), best_metric_value))
    u.log_message(message, log_file=session_file, console=1)
    output_dir = os.path.normpath(u.check_dir(datasets_file))
    if args.predictions_csv:
        resume = create_prediction_dataset(output_dir, "kfold%s" % best_counter,
                                           args, resume)
    message = ('Evaluated %d/%d feature subsets\n\n' %
               ((len(open_list) + len(closed_list) - 1),
                2 ** len(field_ids) - 1))
    u.log_message(message, log_file=session_file, console=1)
    features_writer.close_writer()
    return best_features


def extract_evaluation_info(evaluation, category):
    """Returns the evaluation metrics for the chosen
       category or the average.

    """
    evaluation = evaluation.get("model", {})
    if category and PER_CLASS in evaluation:
        for class_evaluation in evaluation[PER_CLASS]:
            if category == class_evaluation["class_name"]:
                return class_evaluation
    return evaluation


def kfold_evaluate(datasets_file, args, counter, command_obj,
                   penalty=DEFAULT_PENALTY,
                   metric=ACCURACY, resume=False):
    """Scoring k-fold cross-validation using the given feature subset

    """
    # create evaluation with input_fields
    args.output_dir = os.path.normpath(os.path.join(u.check_dir(datasets_file),
                                                    "kfold"))
    evaluation, resume = create_kfold_evaluations(datasets_file, args,
                                                  command_obj,
                                                  resume=resume,
                                                  counter=counter)

    evaluation = extract_evaluation_info(
        evaluation, args.optimize_category)
    avg_metric = AVG_PREFIX % metric
    metric_literal = metric
    if not avg_metric in evaluation:
        avg_metric = AVG_PREFIX % R_SQUARED
        metric_literal = R_SQUARED
        if not avg_metric in evaluation:
            sys.exit("Failed to find %s or r-squared in the evaluation"
                     % metric)
    invert = -1 if metric in MINIMIZE_OPTIONS else 1
    return (invert * (evaluation[avg_metric] -
                      invert * penalty *
                      len(args.model_fields.split(args.args_separator))),
            evaluation[avg_metric],
            metric_literal, resume)


def best_node_threshold(datasets_file, args, command_obj,
                        staleness=None, penalty=None,
                        resume=False):
    """Selecting the node_limit to be used in the model construction

    """
    loop_counter = 0
    nodes_file = os.path.normpath(os.path.join(args.output_dir,
                                               NODES_LOG))
    nodes_writer = UnicodeWriter(nodes_file).open_writer()
    nodes_writer.writerow(NODES_HEADER)
    args.output_dir = os.path.normpath(os.path.join(args.output_dir,
                                                    "node_th"))
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
    best_score = - float('inf')
    best_unchanged_count = 0
    metric = args.optimize
    score = best_score
    best_counter = 0
    while best_unchanged_count < staleness and node_threshold < max_nodes:
        loop_counter += 1
        (score,
         metric_value,
         metric,
         resume) = node_threshold_evaluate(datasets_file, args,
                                           node_threshold, command_obj,
                                           penalty=penalty, resume=resume,
                                           metric=metric)
        nodes_writer.writerow([
            loop_counter - 1, node_threshold, score, metric_value, best_score])
        if (score - EPSILON) > best_score:
            best_threshold = node_threshold
            best_score = score
            best_unchanged_count = 0
            best_counter = loop_counter
            message = 'New best node threshold: %s\n' % (best_threshold)
            u.log_message(message, log_file=session_file,
                          console=args.verbosity)
            if metric in PERCENT_EVAL_METRICS:
                message = '%s = %0.2f%% (score = %s)\n' % (
                    metric.capitalize(), metric_value * 100, score)
            else:
                message = '%s = %f (score = %s)\n' % (metric.capitalize(),
                                                      metric_value,
                                                      score)
            u.log_message(message, log_file=session_file,
                          console=args.verbosity)
        else:
            best_unchanged_count += 1
        node_threshold += args.nodes_step
    if args.predictions_csv:
        resume = create_prediction_dataset(args.output_dir,
                                           "node_th%s" % best_counter,
                                           args, resume)
    message = ('The best node threshold is: %s \n'
               % best_threshold)
    u.log_message(message, log_file=session_file, console=1)
    if metric in PERCENT_EVAL_METRICS:
        message = ('%s = %0.2f%%\n' % (metric.capitalize(),
                                       (best_score * 100)))
    else:
        message = ('%s = %f\n' % (metric.capitalize(), best_score))
    u.log_message(message, log_file=session_file, console=1)
    nodes_writer.close_writer()
    return best_threshold


def node_threshold_evaluate(datasets_file, args, node_threshold,
                            command_obj, penalty=DEFAULT_NODES_PENALTY,
                            metric=ACCURACY, resume=False):
    """Scoring node_threshold created models

    """
    # create evaluation with input_fields
    evaluation, resume = create_node_th_evaluations(
        datasets_file, args, command_obj, resume=resume,
        node_threshold=node_threshold)

    evaluation = extract_evaluation_info(
        evaluation, args.optimize_category)
    avg_metric = AVG_PREFIX % metric
    metric_literal = metric
    if not avg_metric in evaluation:
        avg_metric = AVG_PREFIX % R_SQUARED
        metric_literal = R_SQUARED
        if not avg_metric in evaluation:
            sys.exit("Failed to find %s or r-squared in the evaluation"
                     % metric)
    invert = -1 if metric in MINIMIZE_OPTIONS else 1
    return (invert * (evaluation[avg_metric] -
                      invert * penalty * node_threshold),
            evaluation[avg_metric],
            metric_literal, resume)


def create_node_th_evaluations(datasets_file, args, command_obj,
                               resume=False,
                               node_threshold=DEFAULT_MIN_NODES):
    """ Create node_threshold evaluations

    """
    global subcommand_list
    output_dir = os.path.normpath(u.check_dir(
        os.path.join("%s%s" % (args.output_dir, node_threshold),
                     "evaluation.json")))
    command = COMMANDS["node_threshold"] % (
        datasets_file, node_threshold, output_dir)
    command_args = command.split()
    command_obj.propagate(command_args, exclude=["--dataset",
                                                 "--datasets",
                                                 "--dataset-file"])
    command = rebuild_command(command_args)
    if resume:
        next_command = subcommand_list.pop()
        if different_command(next_command, command):
            resume = False
            u.sys_log_message(command, log_file=subcommand_file)
            main_dispatcher(args=command_args)
        elif not subcommand_list:
            main_dispatcher(args=['main', '--resume'])
            resume = False
    else:
        u.sys_log_message(command, log_file=subcommand_file)
        main_dispatcher(args=command_args)
    evaluation_file = os.path.normpath(os.path.join(output_dir,
                                                    "evaluation.json"))
    try:
        with open(evaluation_file, u.open_mode("r")) as evaluation_handler:
            evaluation = json.loads(evaluation_handler.read())
        return evaluation, resume
    except (ValueError, IOError):
        sys.exit("Failed to retrieve evaluation.")


def default_candidates_limits(args, fields):
    """Setting the limits of default random candidates in the random
       candidates analyze

    """
    args.min_candidates = DEFAULT_MIN_CANDIDATES
    args.max_candidates = len(list(fields.preferred_fields().keys()))


def create_candidates_analysis(args, api, command_obj, resume=False):
    """Analyzes the model performance as a function of the number of
       random candidates.

    """
    set_subcommand_file(args.output_dir)
    output_dir = args.output_dir
    if resume:
        retrieve_subcommands()
    datasets_file, objective_name, resume = create_kfold_datasets_file(
        args, api, command_obj, resume=resume)
    args.objective_field = objective_name
    if args.number_of_models == 1:
        args.number_of_models = DEFAULT_NUMBER_OF_MODELS
    message = ('Creating the random candidates set..........\n')
    u.log_message(message, log_file=session_file,
                  console=args.verbosity)
    random_candidates = best_candidates_number(
        datasets_file, args, command_obj,
        penalty=args.penalty,
        resume=resume)
    # showing the instruction to create the complete model with the
    # chosen random candidates number
    bigmler_command = ('bigmler --dataset %s --number-of-models %s'
                       ' --randomize --random-candidates %s') % ( \
        args.dataset, args.number_of_models, random_candidates)
    message = ('To create the final ensemble with the entire dataset using '
               'the selected number of random candidates use:\n%s\n\n' %
               bigmler_command)
    u.log_message(message, log_file=session_file, console=1)
    # showing the instruction to delete the user-given output-dir
    bigmler_command = ('bigmler delete --from-dir %s') % (
        output_dir)
    message = ('To delete all the resources generated by this analyze'
               ' subcommand use:\n%s\n\n') % bigmler_command
    u.log_message(message, log_file=session_file, console=1)


def best_candidates_number(datasets_file, args, command_obj,
                           penalty=None,
                           resume=False):
    """Selecting the best number of random candidates
       to be used in the ensemble construction

    """
    loop_counter = 0
    candidates_file = os.path.normpath(os.path.join(args.output_dir,
                                                    CANDIDATES_LOG))
    candidates_writer = UnicodeWriter(candidates_file).open_writer()
    candidates_writer.writerow(CANDIDATES_HEADER)
    args.output_dir = os.path.normpath(os.path.join(args.output_dir,
                                                    "random"))
    max_candidates = args.max_candidates + 1

    if args.nodes_step is None:
        args.nodes_step = DEFAULT_CANDIDATES_STEP
    random_candidates = args.min_candidates

    if penalty is None:
        penalty = DEFAULT_CANDIDATES_PENALTY
    best_score = - float('inf')
    metric = args.optimize
    score = best_score
    best_counter = 0
    while random_candidates < max_candidates:
        loop_counter += 1
        (score,
         metric_value,
         metric,
         resume) = candidates_evaluate(datasets_file, args,
                                       random_candidates, command_obj,
                                       penalty=penalty, resume=resume,
                                       metric=metric)
        candidates_writer.writerow([
            loop_counter, random_candidates, score, metric_value,
            best_score])
        if (score - EPSILON) > best_score:
            best_candidates = random_candidates
            best_score = score
            best_counter = loop_counter
            message = 'New best random candidates number is: %s\n' % \
                best_candidates
            u.log_message(message, log_file=session_file,
                          console=args.verbosity)
            if metric in PERCENT_EVAL_METRICS:
                message = '%s = %0.2f%% (score = %s)\n' % (
                    metric.capitalize(), metric_value * 100, score)
            else:
                message = '%s = %f (score = %s)\n' % (metric.capitalize(),
                                                      metric_value,
                                                      score)
            u.log_message(message, log_file=session_file,
                          console=args.verbosity)
        random_candidates += DEFAULT_CANDIDATES_STEP
    if args.predictions_csv:
        resume = create_prediction_dataset(args.output_dir,
                                           "random%s" % best_counter,
                                           args, resume)
    message = ('The best random candidates number is: %s \n'
               % best_candidates)
    u.log_message(message, log_file=session_file, console=1)
    if metric in PERCENT_EVAL_METRICS:
        message = ('%s = %0.2f%%\n' % (metric.capitalize(),
                                       (best_score * 100)))
    else:
        message = ('%s = %f\n' % (metric.capitalize(), best_score))
    u.log_message(message, log_file=session_file, console=1)
    candidates_writer.close_writer()
    return best_candidates


def candidates_evaluate(datasets_file, args, random_candidates,
                        command_obj, penalty=DEFAULT_CANDIDATES_PENALTY,
                        metric=ACCURACY, resume=False):
    """Scoring random candidates ensembles

    """
    # create evaluation with input_fields
    evaluation, resume = create_candidates_evaluations(
        datasets_file, args, command_obj, resume=resume,
        random_candidates=random_candidates)

    evaluation = extract_evaluation_info(
        evaluation, args.optimize_category)
    avg_metric = AVG_PREFIX % metric
    metric_literal = metric
    if not avg_metric in evaluation:
        avg_metric = AVG_PREFIX % R_SQUARED
        metric_literal = R_SQUARED
        if not avg_metric in evaluation:
            sys.exit("Failed to find %s or r-squared in the evaluation"
                     % metric)
    invert = -1 if metric in MINIMIZE_OPTIONS else 1
    return (invert * (evaluation[avg_metric] -
                      invert * penalty * random_candidates),
            evaluation[avg_metric],
            metric_literal, resume)


def create_candidates_evaluations(datasets_file, args, command_obj,
                                  resume=False,
                                  random_candidates=DEFAULT_MIN_CANDIDATES):
    """ Create random candidates ensembles evaluations

    """
    global subcommand_list
    output_dir = os.path.normpath(u.check_dir(
        os.path.join("%s%s" % (args.output_dir, random_candidates),
                     "evaluation.json")))
    command = COMMANDS["random_candidates"] % (
        datasets_file, random_candidates, output_dir)
    command_args = command.split()
    """
    common_options_list = u.get_options_list(args, command_obj.common_options,
                                             prioritary=command_args)
    command_args.extend(common_options_list)
    """
    command_args.append("--objective")
    command_args.append(args.objective_field)
    command_args = add_model_options(command_args, args)

    command_obj.propagate(command_args, exclude=["--dataset",
                                                 "--datasets",
                                                 "--dataset-file"])
    command = rebuild_command(command_args)
    if resume:
        next_command = subcommand_list.pop()
        if different_command(next_command, command):
            resume = False
            u.sys_log_message(command, log_file=subcommand_file)
            main_dispatcher(args=command_args)
        elif not subcommand_list:
            main_dispatcher(args=['main', '--resume'])
            resume = False
    else:
        u.sys_log_message(command, log_file=subcommand_file)
        main_dispatcher(args=command_args)
    evaluation_file = os.path.normpath(os.path.join(output_dir,
                                                    "evaluation.json"))
    try:
        with open(evaluation_file, u.open_mode("r")) as evaluation_handler:
            evaluation = json.loads(evaluation_handler.read())
        return evaluation, resume
    except (ValueError, IOError):
        sys.exit("Failed to retrieve evaluation.")
