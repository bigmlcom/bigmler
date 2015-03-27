# -*- coding: utf-8 -*-
#
# Copyright 2014-2015 BigML
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

"""Utilities to parse and transform input args structures

"""
from __future__ import absolute_import

import sys
import os
import datetime
import StringIO

import bigml.api

import bigmler.utils as u

from bigml.multivote import COMBINATION_WEIGHTS, COMBINER_MAP
from bigml.tree import LAST_PREDICTION, PROPORTIONAL

from bigmler.resources import ADD_REMOVE_PREFIX
from bigmler.prediction import FULL_FORMAT, COMBINATION, COMBINATION_LABEL
from bigmler.train_reader import AGGREGATES

# Date and time in format SunNov0412_120510 to name and tag resources
NOW = datetime.datetime.now().strftime("%a%b%d%y_%H%M%S")
MISSING_STRATEGIES = {'last': LAST_PREDICTION, 'proportional': PROPORTIONAL}
DEFAULT_DESCRIPTION = "Created using BigMLer"
RESOURCE_TYPES = ["source", "dataset", "model", "ensemble", "batch_prediction",
                  "cluster", "centroid", "batch_centroid", "anomaly",
                  "anomaly_score", "batch_anomaly_score"]


def has_test(args):
    """Returns if some kind of test data is given in args.

    """
    return (args.test_set or args.test_source or args.test_dataset or
            args.test_stdin or args.test_datasets)


def has_train(args):
    """Returns if some kind of train data is given in args.

    """
    return (args.training_set or args.source or args.dataset or
            args.datasets or args.source_file or args.dataset_file or
            args.train_stdin or args.source_file)


def has_model(args):
    """Boolean that is set when any model option is used

    """
    return (args.model or args.models or args.model_tag or args.model_file
            or args.ensemble or args.ensembles or args.ensemble_tag
            or args.ensemble_file)


def non_compatible(args, option):
    """Return non_compatible options

    """
    if option == '--cross-validation-rate':
        return (args.test_set or args.evaluate or args.model or args.models or
                args.model_tag or args.multi_label)
    if option == '--max-categories':
        return args.evaluate or args.test_split or args.remote
    return False


def get_flags(args):
    """Returns the options set in the command line string normalized ("_" is
       transformed to "-")

    """
    train_stdin = False
    test_stdin = False
    flags = []
    for i in range(0, len(args)):
        if args[i].startswith("--"):
            flag = args[i]
            # syntax --flag=value
            value = None
            if "=" in flag:
                value = args[i][flag.index("="):]
                args[i] = args[i][0: flag.index("=")]
            args[i] = args[i].replace("_", "-")
            flag = args[i]
            if value:
                args[i] = "%s%s" % (flag, value)
            flags.append(flag)
            if (flag == '--train' and (
                    i == len(args) - 1 or args[i + 1].startswith("--"))):
                train_stdin = True
            elif (flag == '--test' and (
                    i == len(args) - 1 or args[i + 1].startswith("--"))):
                test_stdin = True
    return flags, train_stdin, test_stdin


def get_command_message(args):
    """Rebuilds the command message based on the args list

    """
    literal_args = args[:]
    for i in range(0, len(args)):
        # quoting literals with blanks: 'petal length'
        if ' ' in args[i]:
            prefix = ""
            literal = args[i]
            # literals with blanks after "+" or "-": +'petal length'
            if args[i][0] in ADD_REMOVE_PREFIX:
                prefix = args[i][0]
                literal = args[i][1:]
            literal_args[i] = '"%s%s"' % (prefix, literal)
    return u"bigmler %s\n" % u" ".join(literal_args)


def parse_and_check(command):
    """Parses and checks the given args

    """
    parser = command.parser
    args = command.args

    command_args = parser.parse_args(args)
    command_args.train_stdin = command.train_stdin
    command_args.test_stdin = command.test_stdin

    # Checks options' compatibility
    try:
        if command_args.cross_validation_rate > 0 and (
                non_compatible(command_args, '--cross-validation-rate')):
            parser.error("Non compatible flags: --cross-validation-rate"
                         " cannot be used with --evaluate, --model,"
                         " --models, --model-tag or --multi-label. Usage:\n\n"
                         "bigmler --train data/iris.csv "
                         "--cross-validation-rate 0.1")
    except AttributeError:
        pass

    try:
        if command_args.max_categories and (
                non_compatible(command_args, '--max-categories')):
            parser.error("Non compatible flags: --max-categories cannot "
                         "be used with --test-split, --remote or --evaluate.")
    except AttributeError:
        pass

    try:
        if command_args.train_stdin and command_args.multi_label:
            parser.error("Reading multi-label training sets from stream "
                         "is not yet available.")
    except AttributeError:
        pass

    try:
        if command_args.test_stdin and command_args.resume:
            parser.error("Can't resume when using stream reading test sets.")
    except AttributeError:
        pass

    try:
        if (command_args.evaluate and not has_train(command_args) and
                not (has_test(command_args) or command_args.test_split) and
                has_model(command_args)):
            parser.error("Evaluation wrong syntax.\n"
                         "\nTry for instance:\n\nbigmler --train data/iris.csv"
                         " --evaluate\nbigmler --model "
                         "model/5081d067035d076151000011 --dataset "
                         "dataset/5081d067035d076151003423 --evaluate\n"
                         "bigmler --ensemble ensemble/5081d067035d076151003443"
                         " --dataset "
                         "dataset/5081d067035d076151003423 --evaluate")
    except AttributeError:
        pass

    try:
        command_args.label_aggregates_list = []
        if command_args.label_aggregates:
            label_aggregates = command_args.label_aggregates.strip().lower()
            label_aggregates = label_aggregates.split(
                command_args.args_separator)
            for aggregate in label_aggregates:
                if not aggregate in AGGREGATES:
                    parser.error("Wrong value for the --label-aggregates "
                                 "option. The allowed values are count, first "
                                 "and last.")
                command_args.label_aggregates_list.append(aggregate)
    except AttributeError:
        pass

    return command_args


def get_api_instance(command_args, storage_path):
    """Returns an api instance using the given parameters

    """
    api_command_args = {
        'username': command_args.username,
        'api_key': command_args.api_key,
        'dev_mode': command_args.dev_mode,
        'debug': command_args.debug}

    if command_args.store:
        api_command_args.update({'storage': storage_path})

    return bigml.api.BigML(**api_command_args)


def get_output_args(api, command_args, resume):
    """Returns the output args needed for the main bigmler computation process

    """
    try:
        if command_args.train_stdin:
            if command_args.test_stdin:
                sys.exit("The standard input can't be used both for training "
                         "and testing. Choose one of them")
            command_args.training_set = StringIO.StringIO(sys.stdin.read())
        elif command_args.test_stdin:
            command_args.test_set = StringIO.StringIO(sys.stdin.read())
    except AttributeError:
        pass

    try:
        if command_args.objective_field:
            objective = command_args.objective_field
            try:
                command_args.objective_field = int(objective)
            except ValueError:
                if not command_args.train_header:
                    sys.exit("The %s has been set as objective field but"
                             " the file has not been marked as containing"
                             " headers.\nPlease set the --train-header flag if"
                             " the file has headers or use a column number"
                             " to set the objective field." % objective)
    except AttributeError:
        pass

    command_args.resume_ = resume

    # Reads description if provided.
    try:
        if command_args.description:
            description_arg = u.read_description(command_args.description)
            command_args.description_ = description_arg
        else:
            command_args.description_ = DEFAULT_DESCRIPTION
    except AttributeError:
        pass

    # Parses fields if provided.
    try:
        if command_args.field_attributes:
            field_attributes_arg = (
                u.read_field_attributes(command_args.field_attributes))
            command_args.field_attributes_ = field_attributes_arg
        else:
            command_args.field_attributes_ = []
    except AttributeError:
        pass
    try:
        if command_args.test_field_attributes:
            field_attributes_arg = (
                u.read_field_attributes(command_args.test_field_attributes))
            command_args.test_field_attributes_ = field_attributes_arg
        else:
            command_args.test_field_attributes_ = []
    except AttributeError:
        pass

    # Parses types if provided.
    try:
        if command_args.types:
            types_arg = u.read_types(command_args.types)
            command_args.types_ = types_arg
        else:
            command_args.types_ = None
        if command_args.test_types:
            types_arg = u.read_types(command_args.test_types)
            command_args.test_types_ = types_arg
        else:
            command_args.test_types_ = None
    except AttributeError:
        pass


    # Parses dataset fields if provided.
    try:
        if command_args.dataset_fields:
            dataset_fields_arg = [
                field.strip() for field in command_args.dataset_fields.split(
                    command_args.args_separator)]
            command_args.dataset_fields_ = dataset_fields_arg
        else:
            command_args.dataset_fields_ = []
    except AttributeError:
        pass

    # Parses model input fields if provided.
    try:
        if command_args.model_fields:
            model_fields_arg = [
                field.strip() for field in command_args.model_fields.split(
                    command_args.args_separator)]
            command_args.model_fields_ = model_fields_arg
        else:
            command_args.model_fields_ = []
    except AttributeError:
        pass

    # Parses cluster input fields if provided.
    try:
        if command_args.cluster_fields:
            cluster_fields_arg = [
                field.strip() for field in command_args.cluster_fields.split(
                    command_args.args_separator)]
            command_args.cluster_fields_ = cluster_fields_arg
        else:
            command_args.cluster_fields_ = []
    except AttributeError:
        pass

    # Parses anomaly input fields if provided.
    try:
        if command_args.anomaly_fields:
            anomaly_fields_arg = [
                field.strip() for field in command_args.anomaly_fields.split(
                    command_args.args_separator)]
            command_args.anomaly_fields_ = anomaly_fields_arg
        else:
            command_args.anomaly_fields_ = []
    except AttributeError:
        pass

    model_ids = []
    try:
        # Parses model/ids if provided.
        if command_args.models:
            model_ids = u.read_resources(command_args.models)
        command_args.model_ids_ = model_ids
    except AttributeError:
        pass

    # Retrieve model/ids if provided.
    try:
        if command_args.model_tag:
            model_ids = (model_ids +
                         u.list_ids(api.list_models,
                                    "tags__in=%s" % command_args.model_tag))
        command_args.model_ids_ = model_ids
    except AttributeError:
        pass

    # Reads votes files in the provided directories.
    try:
        if command_args.votes_dirs:
            dirs = [
                directory.strip() for directory in
                command_args.votes_dirs.split(
                    command_args.args_separator)]
            votes_path = os.path.dirname(command_args.predictions)
            votes_files = u.read_votes_files(dirs, votes_path)
            command_args.votes_files_ = votes_files
        else:
            command_args.votes_files_ = []
    except AttributeError:
        pass

    # Parses fields map if provided.
    try:
        if command_args.fields_map:
            fields_map_arg = u.read_fields_map(command_args.fields_map)
            command_args.fields_map_ = fields_map_arg
        else:
            command_args.fields_map_ = None
    except AttributeError:
        pass

    cluster_ids = []
    try:
        # Parses cluster/ids if provided.
        if command_args.clusters:
            cluster_ids = u.read_resources(command_args.clusters)
        command_args.cluster_ids_ = cluster_ids
    except AttributeError:
        pass

    # Retrieve cluster/ids if provided.
    try:
        if command_args.cluster_tag:
            cluster_ids = (cluster_ids +
                           u.list_ids(api.list_clusters,
                                      "tags__in=%s" %
                                      command_args.cluster_tag))
        command_args.cluster_ids_ = cluster_ids
    except AttributeError:
        pass

    # Parses cluster names to generate datasets if provided
    try:
        if command_args.cluster_datasets:
            cluster_datasets_arg = [
                dataset.strip() for dataset in
                command_args.cluster_datasets.split(
                    command_args.args_separator)]
            command_args.cluster_datasets_ = cluster_datasets_arg
        else:
            command_args.cluster_datasets_ = []
    except AttributeError:
        pass

    anomaly_ids = []
    try:
        # Parses anomaly/ids if provided.
        if command_args.anomalies:
            anomaly_ids = u.read_resources(command_args.anomalies)
        command_args.anomaly_ids_ = anomaly_ids
    except AttributeError:
        pass

    # Retrieve anomaly/ids if provided.
    try:
        if command_args.anomaly_tag:
            anomaly_ids = (anomaly_ids +
                           u.list_ids(api.list_anomalies,
                                      "tags__in=%s" %
                                      command_args.anomaly_tag))
        command_args.anomaly_ids_ = anomaly_ids
    except AttributeError:
        pass

    sample_ids = []
    try:
        # Parses sample/ids if provided.
        if command_args.samples:
            sample_ids = u.read_resources(command_args.samples)
        command_args.sample_ids_ = sample_ids
    except AttributeError:
        pass

    # Retrieve sample/ids if provided.
    try:
        if command_args.sample_tag:
            sample_ids = (
                sample_ids + u.list_ids(api.list_samples,
                                        "tags__in=%s" %
                                        command_args.sample_tag))
        command_args.sample_ids_ = sample_ids
    except AttributeError:
        pass

    # Parses sample row fields
    try:
        if command_args.row_fields:
            row_fields_arg = [field.strip() for field in
                              command_args.row_fields.split(
                                  command_args.args_separator)]
            command_args.row_fields_ = row_fields_arg
        else:
            command_args.row_fields_ = []
    except AttributeError:
        pass

    # Parses sample stat_fields
    try:
        if command_args.stat_fields:
            stat_fields_arg = [field.strip() for field in
                               command_args.stat_fields.split(
                                   command_args.args_separator)]
            command_args.stat_fields_ = stat_fields_arg
        else:
            command_args.stat_fields_ = []
    except AttributeError:
        pass

    return {"api": api, "args": command_args}


def transform_args(command_args, flags, api, user_defaults):
    """Transforms the formatted argument strings into structured arguments

    """
    # Parses attributes in json format if provided
    command_args.json_args = {}

    for resource_type in RESOURCE_TYPES:
        attributes_file = getattr(command_args,
                                  "%s_attributes" % resource_type, None)
        if attributes_file is not None:
            command_args.json_args[resource_type] = u.read_json(
                attributes_file)
        else:
            command_args.json_args[resource_type] = {}

    # Parses dataset generators in json format if provided
    if command_args.new_fields:
        json_generators = u.read_json(command_args.new_fields)
        command_args.dataset_json_generators = json_generators
    else:
        command_args.dataset_json_generators = {}

    # Parses multi-dataset attributes in json such as field maps
    if command_args.multi_dataset_attributes:
        multi_dataset_json = u.read_json(command_args.multi_dataset_attributes)
        command_args.multi_dataset_json = multi_dataset_json
    else:
        command_args.multi_dataset_json = {}

    dataset_ids = None
    command_args.dataset_ids = []
    # Parses dataset/id if provided.
    if command_args.datasets:
        dataset_ids = u.read_datasets(command_args.datasets)
        if len(dataset_ids) == 1:
            command_args.dataset = dataset_ids[0]
        command_args.dataset_ids = dataset_ids

    test_dataset_ids = None
    command_args.test_dataset_ids = []
    try:
        # Parses dataset/id if provided.
        if command_args.test_datasets:
            test_dataset_ids = u.read_datasets(command_args.test_datasets)
            command_args.test_dataset_ids = test_dataset_ids
    except AttributeError:
        pass

    # Retrieve dataset/ids if provided.
    if command_args.dataset_tag:
        dataset_ids = dataset_ids.extend(
            u.list_ids(api.list_datasets,
                       "tags__in=%s" % command_args.dataset_tag))
        if len(dataset_ids) == 1:
            command_args.dataset = dataset_ids[0]
        command_args.dataset_ids = dataset_ids

    # Reads a json filter if provided.
    if command_args.json_filter:
        json_filter = u.read_json_filter(command_args.json_filter)
        command_args.json_filter = json_filter

    # Reads a lisp filter if provided.
    if command_args.lisp_filter:
        lisp_filter = u.read_lisp_filter(command_args.lisp_filter)
        command_args.lisp_filter = lisp_filter

    # Adds default tags unless that it is requested not to do so.
    if command_args.no_tag:
        command_args.tag.append('BigMLer')
        command_args.tag.append('BigMLer_%s' % NOW)

    # Checks combined votes method
    try:
        if (command_args.method and command_args.method != COMBINATION_LABEL
                and not (command_args.method in COMBINATION_WEIGHTS.keys())):
            command_args.method = 0
        else:
            combiner_methods = dict(
                [[value, key] for key, value in COMBINER_MAP.items()])
            combiner_methods[COMBINATION_LABEL] = COMBINATION
            command_args.method = combiner_methods.get(command_args.method, 0)
    except AttributeError:
        pass

    # Checks missing_strategy
    try:
        if (command_args.missing_strategy and
                not (command_args.missing_strategy in
                     MISSING_STRATEGIES.keys())):
            command_args.missing_strategy = 0
        else:
            command_args.missing_strategy = MISSING_STRATEGIES.get(
                command_args.missing_strategy, 0)
    except AttributeError:
        pass

    # Adds replacement=True if creating ensemble and nothing is specified
    try:
        if (command_args.number_of_models > 1 and
                not command_args.replacement and
                not '--no-replacement' in flags and
                not 'replacement' in user_defaults and
                not '--no-randomize' in flags and
                not 'randomize' in user_defaults and
                not '--sample-rate' in flags and
                not 'sample_rate' in user_defaults):
            command_args.replacement = True
    except AttributeError:
        pass
    try:
        # Old value for --prediction-info='full data' maps to 'full'
        if command_args.prediction_info == 'full data':
            print ("WARNING: 'full data' is a deprecated value. Use"
                   " 'full' instead")
            command_args.prediction_info = FULL_FORMAT
    except AttributeError:
        pass

    # Parses class, weight pairs for objective weight
    try:
        if command_args.objective_weights:
            objective_weights = (
                u.read_objective_weights(command_args.objective_weights))
            command_args.objective_weights_json = objective_weights
    except AttributeError:
        pass

    try:
        command_args.multi_label_fields_list = []
        if command_args.multi_label_fields is not None:
            multi_label_fields = command_args.multi_label_fields.strip()
            command_args.multi_label_fields_list = multi_label_fields.split(
                command_args.args_separator)
    except AttributeError:
        pass

    # Sets shared_flag if --shared or --unshared has been used
    if '--shared' in flags or '--unshared' in flags:
        command_args.shared_flag = True
    else:
        command_args.shared_flag = False

    command_args.has_models_ = (
        (hasattr(command_args, 'model') and command_args.model) or
        (hasattr(command_args, 'models') and command_args.models) or
        (hasattr(command_args, 'ensemble') and command_args.ensemble) or
        (hasattr(command_args, 'ensembles') and command_args.ensembles) or
        (hasattr(command_args, 'cluster') and command_args.cluster) or
        (hasattr(command_args, 'clusters') and command_args.clusters) or
        (hasattr(command_args, 'model_tag') and command_args.model_tag) or
        (hasattr(command_args, 'anomaly') and command_args.anomaly) or
        (hasattr(command_args, 'anomalies') and command_args.anomalies) or
        (hasattr(command_args, 'ensemble_tag')
         and command_args.ensemble_tag) or
        (hasattr(command_args, 'cluster_tag') and command_args.cluster_tag) or
        (hasattr(command_args, 'anomaly_tag') and command_args.anomaly_tag))

    command_args.has_datasets_ = (
        (hasattr(command_args, 'dataset') and command_args.dataset) or
        (hasattr(command_args, 'datasets') and command_args.datasets) or
        (hasattr(command_args, 'dataset_tag') and command_args.dataset_tag))
