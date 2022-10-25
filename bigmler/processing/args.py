# -*- coding: utf-8 -*-
#
# Copyright 2014-2022 BigML
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


import sys
import os
import datetime
import json

from io import StringIO

import bigml.api

from bigml.multivote import COMBINATION_WEIGHTS, COMBINER_MAP
from bigml.constants import LAST_PREDICTION, PROPORTIONAL

import bigmler.utils as u

from bigmler.resourcesapi.common import ADD_REMOVE_PREFIX
from bigmler.prediction import FULL_FORMAT, COMBINATION, COMBINATION_LABEL
from bigmler.train_reader import AGGREGATES
from bigmler.utils import check_dir


# Date and time in format SunNov0412_120510 to name and tag resources
NOW = datetime.datetime.now().strftime("%a%b%d%y_%H%M%S")
OUTPUT_DIR = os.path.join(".bigmler_outputs", NOW)
MISSING_STRATEGIES = {'last': LAST_PREDICTION, 'proportional': PROPORTIONAL}
DEFAULT_DESCRIPTION = "Created using BigMLer"
RESOURCE_TYPES = ["source", "dataset", "model", "ensemble", "batch_prediction",
                  "cluster", "centroid", "batch_centroid", "anomaly",
                  "anomaly_score", "batch_anomaly_score", "project", "sample",
                  "association", "logistic_regression", "deepnet", "script",
                  "library", "execution", "evaluation", "topic_model",
                  "linear_regression", "fusion", "prediction", "pca",
                  "external_connector"]

STORED_MODELS = ["model_file", "ensemble_file", "logistic_file",
                 "cluster_file", "anomaly_file", "deepnet_file",
                 "linear_file", "topic_model_file", "association_file",
                 "pca_file"]

def has_value(args, attrs):
    """Returns a list of booleans checking whether each attribute is set and
       his value

    """
    if isinstance(attrs, list):
        return [hasattr(args, attr) and getattr(args, attr)
                for attr in attrs]
    if isinstance(attrs, str):
        return hasattr(args, attrs) and getattr(args, attrs)
    return False


def has_test(args):
    """Returns if some kind of test data is given in args.

    """
    return any(has_value(args, ["test_set", "test_source", "test_dataset",
                                "test_stdin", "test_datasets"]))

def has_ts_test(args):
    """Returns if some kind of test data for time series is given in args.

    """
    return any(has_value(args, ["test_set", "test_stdin", "forecast",
                                "horizon"]))


def has_train(args):
    """Returns if some kind of train data is given in args.

    """
    return any(has_value(args, ["training_set", "source", "source_in",
                                "dataset", "datasets", "source_file",
                                "dataset_file", "train_stdin", "source_tag",
                                "dataset_tag"]))


def has_source(args):
    """Returns if some kind of source is given in args.

    """
    return any(has_value(args, ["source", "sources", "source_file",
                                "source_tag"]))


def has_model(args):
    """Boolean that is set when any model option is used

    """
    return any(has_value(args, ["model", "models", "model_tag", "model_file",
                                "ensemble", "ensembles", "ensemble_tag",
                                "ensemble_file"]))


def has_anomaly(args):
    """Boolean that is set when any anomaly option is used

    """
    return any(has_value(args, ["anomaly", "anomalies", "anomaly_tag",
                                "anomaly_file"]))


def non_compatible(args, option):
    """Return non_compatible options

    """
    if option == '--cross-validation-rate':
        return any(has_value(args, ["test_set", "evaluate", "model",
                                    "models", "model_tag", "multi_label"]))
    if option == '--max-categories':
        return any(has_value(args, ["evaluate", "test_split", "remote"]))
    return False


def get_flags(args):
    """Returns the options set in the command line string normalized ("_" is
       transformed to "-")

    """
    train_stdin = False
    test_stdin = False
    flags = []
    for i, arg in enumerate(args):
        if arg.startswith("--"):
            flag = args[i]
            # syntax --flag=value
            value = None
            if "=" in flag:
                value = arg[flag.index("="):]
                args[i] = arg[0: flag.index("=")]
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


def comma_to_list(comma_arg, separator, none=False):
    """Returns the list of elements defined in a comma-separated string
    adapting to the actual command separator

    """
    if comma_arg is None and none:
        return None

    if comma_arg:
        list_arg = [option.strip() for option in
            comma_arg.split(separator)]
    else:
        list_arg = []

    return list_arg


def get_command_message(args):
    """Rebuilds the command message based on the args list

    """
    literal_args = args[:]
    for i, arg in enumerate(args):
        # quoting literals with blanks: 'petal length'
        if ' ' in arg:
            prefix = ""
            literal = arg
            # literals with blanks after "+" or "-": +'petal length'
            if arg[0] in ADD_REMOVE_PREFIX:
                prefix = arg[0]
                literal = arg[1:]
            literal_args[i] = '"%s%s"' % (prefix, literal)
    return "bigmler %s\n" % " ".join(literal_args)


def parse_and_check(command):
    """Parses and checks the given args

    """
    parser = command.parser
    args = command.args

    command_args = parser.parse_args(args)
    command_args.train_stdin = command.train_stdin
    command_args.test_stdin = command.test_stdin
    command_args.subcommand = command.command.split(" ")[1]
    if command_args.subcommand.startswith("-"):
        command_args.subcommand = "main"

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
        'debug': command_args.debug}

    if command_args.store:
        api_command_args.update({'storage': storage_path})
    if hasattr(command_args, "org_project") and command_args.org_project:
        api_command_args.update({'project': command_args.org_project})
    if hasattr(command_args, "organization") and command_args.organization:
        api_command_args.update({"organization": command_args.organization})

    command_args.api_ = bigml.api.BigML(**api_command_args)

    # if locally stored models are used, local predicting objects should use
    # this directory to look for the model information first. Otherwise,
    # use the storage_path and if not set ./storage directory
    retrieve_dir = None
    for stored_model in STORED_MODELS:
        if hasattr(command_args, stored_model) and \
                getattr(command_args, stored_model) is not None:
            retrieve_dir = check_dir(getattr(command_args, stored_model))
            break
    if retrieve_dir is None:
        retrieve_dir = storage_path if command_args.store else './storage'

    command_args.retrieve_api_ = bigml.api.BigML(**{ \
        'username': command_args.username,
        'api_key': command_args.api_key,
        'debug': command_args.debug,
        'storage': retrieve_dir})

    return command_args.api_


def get_output_args(api, command_args, resume):
    """Returns the output args needed for the main bigmler computation process

    """
    try:
        if command_args.train_stdin:
            if command_args.test_stdin:
                sys.exit("The standard input can't be used both for training "
                         "and testing. Choose one of them")
            command_args.training_set = StringIO(sys.stdin.read())
        elif command_args.test_stdin:
            command_args.test_set = StringIO(sys.stdin.read())
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
    command_args.predictions = command_args.output
    command_args.projections = command_args.output


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
        command_args.dataset_fields_ = comma_to_list(command_args.dataset_fields,
                                                     command_args.args_separator)
    except AttributeError:
        pass

    # Parses model input fields if provided.
    try:
        command_args.model_fields_ = comma_to_list(command_args.model_fields,
                                                   command_args.args_separator)
    except AttributeError:
        pass

    # Parses cluster input fields if provided.
    try:
        command_args.cluster_fields_ = comma_to_list(command_args.cluster_fields,
                                                     command_args.args_separator)
    except AttributeError:
        pass

    # Parses association input fields if provided.
    try:
        command_args.association_fields_ = comma_to_list(
            command_args.association_fields, command_args.args_separator)
    except AttributeError:
        pass

    # Parses anomaly input fields if provided.
    try:
        command_args.anomaly_fields_ = comma_to_list(
            command_args.anomaly_fields, command_args.args_separator)
    except AttributeError:
        pass

    # Parses logistic regression input fields if provided.
    try:
        command_args.logistic_fields_ = comma_to_list(
            command_args.logistic_fields, command_args.args_separator)
    except AttributeError:
        pass

    # Parses linear regression input fields if provided.
    try:
        command_args.linear_fields_ = comma_to_list(
            command_args.linear_fields, command_args.args_separator)
    except AttributeError:
        pass

    # Parses deepnet input fields if provided.
    try:
        command_args.deepnet_fields_ = comma_to_list(
            command_args.deepnet_fields, command_args.args_separator)
    except AttributeError:
        pass

    # Parses topic model fields if provided.
    try:
        command_args.topic_fields_ = comma_to_list(
            command_args.topic_fields, command_args.args_separator)
    except AttributeError:
        pass

    # Parses pca fields if provided.
    try:
        command_args.pca_fields_ = comma_to_list(
            command_args.pca_fields, command_args.args_separator)
    except AttributeError:
        pass

    # Parses field_codings for deepnet
    try:
        if command_args.field_codings:
            command_args.field_codings_ = u.read_json(
                command_args.field_codings)
        else:
            command_args.field_codings_ = []
    except AttributeError:
        pass

    # Parses imports for scripts and libraries.
    try:
        command_args.imports_ = comma_to_list(
            command_args.imports, command_args.args_separator)
    except AttributeError:
        pass

    # Parses objective fields for time-series.
    try:
        command_args.objectives_ = comma_to_list(
            command_args.objectives, command_args.args_separator)
    except AttributeError:
        pass

    # Parses range.
    try:
        command_args.range_ = comma_to_list(
            command_args.range, command_args.args_separator)
    except AttributeError:
        pass

    # Parses parameters for scripts.
    try:
        if command_args.declare_inputs:
            command_args.parameters_ = u.read_json(command_args.declare_inputs)
        else:
            command_args.parameters_ = []
    except AttributeError:
        pass

    # Parses creation_defaults for executions.
    try:
        if command_args.creation_defaults:
            command_args.creation_defaults_ = u.read_json(
                command_args.creation_defaults)
        else:
            command_args.creation_defaults_ = {}
    except AttributeError:
        pass

    # Parses arguments for executions.
    try:
        if command_args.inputs:
            command_args.arguments_ = u.read_json(command_args.inputs)
        else:
            command_args.arguments_ = []
    except AttributeError:
        pass

    # Parses input maps for executions.
    try:
        if command_args.input_maps:
            command_args.input_maps_ = u.read_json(command_args.input_maps)
        else:
            command_args.input_maps_ = []
    except AttributeError:
        pass

    # Parses outputs for executions.
    try:
        if command_args.outputs:
            command_args.outputs_ = u.read_json(command_args.outputs)
        else:
            command_args.outputs_ = []
    except AttributeError:
        pass

    # Parses outputs for scripts.
    try:
        if command_args.declare_outputs:
            command_args.declare_outputs_ = \
                u.read_json(command_args.declare_outputs)
        else:
            command_args.declare_outputs_ = []
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

    association_ids = []
    try:
        # Parses association/ids if provided.
        if command_args.associations:
            association_ids = u.read_resources(command_args.associations)
        command_args.association_ids_ = association_ids
    except AttributeError:
        pass

    # Retrieve association/ids if provided.
    try:
        if command_args.association_tag:
            association_ids = (association_ids +
                               u.list_ids(api.list_associations,
                                          "tags__in=%s" %
                                          command_args.association_tag))
        command_args.association_ids_ = association_ids
    except AttributeError:
        pass

    logistic_regression_ids = []
    try:
        # Parses logisticregression/ids if provided.
        if command_args.logistic_regressions:
            logistic_regression_ids = u.read_resources( \
                command_args.logistic_regressions)
        command_args.logistic_regression_ids_ = logistic_regression_ids
    except AttributeError:
        pass

    # Retrieve logsticregression/ids if provided.
    try:
        if command_args.logistic_regression_tag:
            logistic_regression_ids = (logistic_regression_ids + \
                u.list_ids(api.list_logistic_regressions,
                           "tags__in=%s" %
                           command_args.logistic_regression_tag))
        command_args.logistic_regression_ids_ = logistic_regression_ids
    except AttributeError:
        pass

    linear_regression_ids = []
    try:
        # Parses linearregression/ids if provided.
        if command_args.linear_regressions:
            linear_regression_ids = u.read_resources( \
                command_args.linear_regressions)
        command_args.linear_regression_ids_ = linear_regression_ids
    except AttributeError:
        pass

    # Retrieve linearregression/ids if provided.
    try:
        if command_args.linear_regression_tag:
            linear_regression_ids = (linear_regression_ids + \
                u.list_ids(api.list_linear_regressions,
                           "tags__in=%s" %
                           command_args.linear_regression_tag))
        command_args.linear_regression_ids_ = linear_regression_ids
    except AttributeError:
        pass


    deepnet_ids = []
    try:
        # Parses deepnet/ids if provided.
        if command_args.deepnets:
            deepnet_ids = u.read_resources( \
                command_args.deepnets)
        command_args.deepnet_ids_ = deepnet_ids
    except AttributeError:
        pass

    # Retrieve deepnet/ids if provided.
    try:
        if command_args.deepnet_tag:
            deepnet_ids = (deepnet_ids + \
                u.list_ids(api.list_deepnets,
                           "tags__in=%s" % command_args.deepnet_tag))
        command_args.deepnet_ids_ = deepnet_ids
    except AttributeError:
        pass

    topic_model_ids = []
    try:
        # Parses topicmodel/ids if provided.
        if command_args.topic_models:
            topic_model_ids = u.read_resources(command_args.topic_models)
        command_args.topic_model_ids_ = topic_model_ids
    except AttributeError:
        pass

    # Retrieve topicmodel/ids if provided.
    try:
        if command_args.topic_model_tag:
            topic_model_ids = (topic_model_ids +
                               u.list_ids(api.list_topic_models,
                                          "tags__in=%s" %
                                          command_args.topic_model_tag))
        command_args.topic_model_ids_ = topic_model_ids
    except AttributeError:
        pass


    time_series_ids = []
    try:
        # Parses timeseries/ids if provided.
        if command_args.time_series_set:
            time_series_ids = u.read_resources(command_args.time_series)
        command_args.time_series_ids_ = time_series_ids
    except AttributeError:
        pass

    # Retrieve timeseries/ids if provided.
    try:
        if command_args.time_series_tag:
            time_series_ids = (time_series_ids +
                               u.list_ids(api.list_time_series,
                                          "tags__in=%s" %
                                          command_args.time_series_tag))
        command_args.time_series_ids_ = time_series_ids
    except AttributeError:
        pass

    pca_ids = []
    try:
        # Parses pca/ids if provided.
        if command_args.pcas:
            pca_ids = u.read_resources(command_args.pcas)
        command_args.pca_ids_ = pca_ids
    except AttributeError:
        pass

    # Retrieve pca/ids if provided.
    try:
        if command_args.pca_tag:
            pca_ids = (pca_ids +
                       u.list_ids(api.pca_series,
                                  "tags__in=%s" %
                                  command_args.pca_tag))
        command_args.pca_ids_ = pca_ids
    except AttributeError:
        pass

    # Parses models list for fusions if provided.
    try:
        command_args.fusion_models_ = comma_to_list(
            command_args.fusion_models, command_args.args_separator)
    except AttributeError:
        pass

    # Parses models list for fusions if provided.
    if not has_value(command_args, "fusion_models_"):
        try:
            if command_args.fusion_models_file:
                fusion_models_arg = u.read_json(
                    command_args.fusion_models_file)
                command_args.fusion_models_ = fusion_models_arg
            else:
                command_args.fusion_models_ = []
        except AttributeError:
            pass

    fusion_ids = []
    try:
        # Parses fusion/ids if provided.
        if command_args.fusions:
            fusion_ids = u.read_resources(command_args.fusions)
        command_args.fusion_ids_ = fusion_ids
    except AttributeError:
        pass

    # Retrieve fusion/ids if provided.
    try:
        if command_args.fusion_tag:
            fusion_ids = (fusion_ids +
                          u.list_ids(api.fusion_series,
                                     "tags__in=%s" %
                                     command_args.fusion_tag))
        command_args.fusion_ids_ = fusion_ids
    except AttributeError:
        pass

    # Parses cluster names to generate datasets if provided
    try:
        command_args.cluster_datasets_ = comma_to_list(
            command_args.cluster_datasets, command_args.args_separator)
    except AttributeError:
        pass

    # Parses cluster names to generate models if provided
    try:
        command_args.cluster_models_ = comma_to_list(
            command_args.cluster_models, command_args.args_separator)
    except AttributeError:
        pass

    # Parses summary_fields to exclude from the clustering algorithm
    try:
        command_args.summary_fields_ = comma_to_list(
            command_args.summary_fields, command_args.args_separator)
    except AttributeError:
        pass

    # Parses image_augmentations
    try:
        command_args.image_augmentations_ = comma_to_list(
            command_args.image_augmentations, command_args.args_separator)
    except AttributeError:
        pass

    # Parses add_sources
    try:
        command_args.add_sources_ = comma_to_list(
            command_args.add_sources, command_args.args_separator)
    except AttributeError:
        pass

    # Parses remove_sources
    try:
        command_args.remove_sources_ = comma_to_list(
            command_args.remove_sources, command_args.args_separator)
    except AttributeError:
        pass

    # Parses delete_sources
    try:
        command_args.delete_sources_ = comma_to_list(
            command_args.delete_sources, command_args.args_separator)
    except AttributeError:
        pass

    # Parses sources
    try:
        command_args.sources_ = comma_to_list(
            command_args.sources, command_args.args_separator, none=True)
    except AttributeError:
        pass

    # Parses include_extracted_features
    try:
        if command_args.include_extracted_features:
            include_extracted_features_arg = [
                field.strip() for field in
                command_args.include_extracted_features.split(
                    command_args.args_separator)]
            if include_extracted_features_arg == ["all"]:
                include_extracted_features_arg = True
            elif include_extracted_features_arg == ["none"]:
                include_extracted_features_arg = False
            command_args.include_extracted_features_ = \
                include_extracted_features_arg
        else:
            command_args.include_extracted_features_ = []
    except AttributeError:
        pass

    # Parses row_components
    try:
        command_args.row_components_ = comma_to_list(
            command_args.row_components, command_args.args_separator)
    except AttributeError:
        pass


    # Parses row_indices
    try:
        command_args.row_indices_ = comma_to_list(
            command_args.row_indices, command_args.args_separator)
    except AttributeError:
        pass

    # Parses id_fields to exclude from the anomaly detector algorithm
    try:
        if command_args.id_fields:
            id_fields_arg = [
                field.strip() for field in
                command_args.id_fields.split(
                    command_args.args_separator)]
            command_args.id_fields_ = id_fields_arg
        else:
            command_args.id_fields_ = []
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
        command_args.row_fields_ = comma_to_list(
            command_args.row_fields, command_args.args_separator)
    except AttributeError:
        pass

    # Parses sample stat_fields
    try:
        command_args.stat_fields_ = comma_to_list(
            command_args.stat_fields, command_args.args_separator)
    except AttributeError:
        pass

    # if boosting arguments are used, set on boosting
    try:
        if command_args.iterations or command_args.learning_rate \
                or command_args.early_holdout:
            command_args.boosting = True
    except AttributeError:
        pass

    # Extracts the imports from the JSON metadata file
    try:
        if command_args.embedded_imports:
            command_args.embedded_imports_ = u.read_resources( \
                command_args.embedded_imports)
        else:
            command_args.embedded_imports_ = []
    except AttributeError:
        pass

    # Parses hidden_layers for deepnets.
    try:
        if command_args.hidden_layers:
            command_args.hidden_layers_ = u.read_json(
                command_args.hidden_layers)
        else:
            command_args.hidden_layers_ = []
    except AttributeError:
        pass

    # Parses operating_point for predictions.
    try:
        if command_args.operating_point:
            command_args.operating_point_ = u.read_json(
                command_args.operating_point)
        else:
            command_args.operating_point_ = []
    except AttributeError:
        pass

    # Parses the json_query
    try:
        if command_args.json_query:
            command_args.json_query_ = u.read_json(command_args.json_query)
        else:
            command_args.json_query_ = None
    except AttributeError:
        pass

    # Parses the models_file
    try:
        if command_args.models_file:
            command_args.models_file_ = u.read_json(command_args.models_file)
        else:
            command_args.models_file_ = None
    except AttributeError:
        pass

    # Parses the sql_output_fields
    try:
        if command_args.sql_output_fields:
            command_args.sql_output_fields_ = u.read_json( \
                command_args.sql_output_fields)
        else:
            command_args.sql_output_fields_ = None
    except AttributeError:
        pass

    # Parses connection info for external connectors
    try:
        if command_args.connection_json:
            command_args.connection_json_ = u.read_json(
                command_args.connection_json)
        else:
            command_args.connection_json_ = {}
    except AttributeError:
        pass

    return {"api": api, "args": command_args}


def attribute_args(command_args):
    """Reads the attributes in JSON files

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


def transform_args(command_args, flags, api):
    """Transforms the formatted argument strings into structured arguments

    """
    attribute_args(command_args)

    # Parses dataset generators in json format if provided
    try:
        if command_args.new_fields:
            json_generators = u.read_json(command_args.new_fields)
            command_args.dataset_json_generators = json_generators
        else:
            command_args.dataset_json_generators = {}
    except AttributeError:
        pass

    # Parses multi-dataset attributes in json such as field maps
    try:
        if command_args.multi_dataset_attributes:
            multi_dataset_json = u.read_json(
                command_args.multi_dataset_attributes)
            command_args.multi_dataset_json = multi_dataset_json
        else:
            command_args.multi_dataset_json = {}
    except AttributeError:
        pass

    transform_dataset_options(command_args, api)

    script_ids = None
    command_args.script_ids = []
    # Parses script/id if provided.
    try:
        if command_args.scripts:
            script_ids = u.read_resources(command_args.scripts)
            if len(script_ids) == 1:
                command_args.script = script_ids[0]
            command_args.script_ids = script_ids
    except AttributeError:
        pass

    # Retrieve script/ids if provided.
    try:
        if command_args.script_tag:
            script_ids = script_ids.extend(
                u.list_ids(api.list_scripts,
                           "tags__in=%s" % command_args.script_tag))
            if len(script_ids) == 1:
                command_args.script = script_ids[0]
            command_args.script_ids = script_ids
    except AttributeError:
        pass

    # Reads a json filter if provided.
    try:
        if command_args.json_filter:
            json_filter = u.read_json_filter(command_args.json_filter)
            command_args.json_filter = json_filter
    except AttributeError:
        pass

    # Reads a lisp filter if provided.
    try:
        if command_args.lisp_filter:
            lisp_filter = u.read_lisp_filter(command_args.lisp_filter)
            command_args.lisp_filter = lisp_filter
    except AttributeError:
        pass

    # Reads a json row_values object.
    command_args.row_values = None
    try:
        if command_args.row_values_json:
            row_values = u.read_json(command_args.row_values_json)
            command_args.row_values = row_values
    except AttributeError:
        pass

    # Adds default tags unless that it is requested not to do so.
    try:
        if command_args.no_tag:
            command_args.tag.append('BigMLer')
            command_args.tag.append('BigMLer_%s' % NOW)
    except AttributeError:
        pass

    # Checks combined votes method
    try:
        if (command_args.method and command_args.method != COMBINATION_LABEL
                and not command_args.method in list(COMBINATION_WEIGHTS.keys())):
            command_args.method = 0
        else:
            combiner_methods = {
                value: key for key, value in list(COMBINER_MAP.items())}
            combiner_methods[COMBINATION_LABEL] = COMBINATION
            command_args.method = combiner_methods.get(command_args.method, 0)
    except AttributeError:
        pass

    # Checks missing_strategy
    try:
        if (command_args.missing_strategy and
                not (command_args.missing_strategy in
                     list(MISSING_STRATEGIES.keys()))):
            command_args.missing_strategy = 0
        else:
            command_args.missing_strategy = MISSING_STRATEGIES.get(
                command_args.missing_strategy, 0)
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
    command_args.shared_flag = '--shared' in flags or '--unshared' in flags

    # Set remote on if scoring a trainind dataset in bigmler anomaly
    try:
        if command_args.score:
            command_args.remote = True
            if not "--prediction-info" in flags:
                command_args.prediction_info = FULL_FORMAT
    except AttributeError:
        pass

    command_args.has_supervised_ = (
        (hasattr(command_args, 'model') and command_args.model) or
        (hasattr(command_args, 'models') and command_args.models) or
        (hasattr(command_args, 'ensemble') and command_args.ensemble) or
        (hasattr(command_args, 'ensembles') and command_args.ensembles) or
        (hasattr(command_args, 'model_tag') and command_args.model_tag) or
        (hasattr(command_args, 'logistic_regression') and
         command_args.logistic_regression) or
        (hasattr(command_args, 'logistic_regressions') and
         command_args.logistic_regressions) or
        (hasattr(command_args, 'logistic_regression_tag') and
         command_args.logistic_regression_tag) or
        (hasattr(command_args, 'deepnet') and
         command_args.deepnet) or
        (hasattr(command_args, 'deepnets') and
         command_args.deepnets) or
        (hasattr(command_args, 'deepnet_tag') and
         command_args.deepnet_tag) or
        (hasattr(command_args, 'ensemble_tag')
         and command_args.ensemble_tag))

    command_args.has_models_ = (
        command_args.has_supervised_ or
        (hasattr(command_args, 'cluster') and command_args.cluster) or
        (hasattr(command_args, 'clusters') and command_args.clusters) or
        (hasattr(command_args, 'anomaly') and command_args.anomaly) or
        (hasattr(command_args, 'anomalies') and command_args.anomalies) or
        (hasattr(command_args, 'cluster_tag') and command_args.cluster_tag) or
        (hasattr(command_args, 'anomaly_tag') and command_args.anomaly_tag))

    command_args.has_datasets_ = (
        (hasattr(command_args, 'dataset') and command_args.dataset) or
        (hasattr(command_args, 'datasets') and command_args.datasets) or
        (hasattr(command_args, 'dataset_ids') and command_args.dataset_ids) or
        (hasattr(command_args, 'dataset_tag') and command_args.dataset_tag))


    command_args.has_test_datasets_ = (
        (hasattr(command_args, 'test_dataset') and
         command_args.test_dataset) or
        (hasattr(command_args, 'test_datasets') and
         command_args.test_datasets) or
        (hasattr(command_args, 'test_dataset_tag') and
         command_args.test_dataset_tag))

    command_args.new_dataset = (
        (hasattr(command_args, 'datasets_json') and
         command_args.datasets_json) or
        (hasattr(command_args, 'multi_dataset') and
         command_args.multi_dataset) or
        (hasattr(command_args, 'juxtapose') and command_args.juxtapose) or
        (hasattr(command_args, 'sql_query') and command_args.sql_query) or
        (hasattr(command_args, 'sql_output_fields') and
         command_args.sql_output_fields) or
        (hasattr(command_args, 'json_query') and
         command_args.json_query))


def transform_dataset_options(command_args, api):
    """Retrieves the dataset ids from the different input options

    """
    command_args.dataset_ids = []
    command_args.test_dataset_ids = []

    try:
        dataset_ids = None
        # Parses dataset/id if provided.
        if command_args.datasets:
            dataset_ids = u.read_datasets(command_args.datasets)
            if dataset_ids:
                command_args.dataset = dataset_ids[-1]
            command_args.dataset_ids = dataset_ids
    except Exception:
        pass

    # Reading test dataset ids is delayed till the very moment of use to ensure
    # that the newly generated resources files can be used there too
    try:
        # Retrieve dataset/ids if provided.
        if command_args.dataset_tag:
            dataset_ids = dataset_ids.extend(
                u.list_ids(api.list_datasets,
                           "tags__in=%s" % command_args.dataset_tag))
            if dataset_ids:
                command_args.dataset = dataset_ids[-1]
            command_args.dataset_ids = dataset_ids
    except Exception:
        pass

    # if datasets_json is set, read it info in datasets
    try:
        if hasattr(command_args, 'datasets_json') \
                and command_args.datasets_json:
            command_args.dataset_ids = json.loads(command_args.datasets_json)
            if dataset_ids:
                command_args.dataset = command_args.dataset_ids[-1]
    except AttributeError:
        pass
