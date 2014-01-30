# -*- coding: utf-8 -*-
#!/usr/bin/env python
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

from bigmler.resources import ADD_REMOVE_PREFIX
from bigmler.prediction import FULL_FORMAT, COMBINATION, COMBINATION_LABEL
from bigmler.train_reader import AGGREGATES

# Date and time in format SunNov0412_120510 to name and tag resources
NOW = datetime.datetime.now().strftime("%a%b%d%y_%H%M%S")


def non_compatible(args, option):
    """Return non_compatible options

    """
    if option == '--cross-validation-rate':
        return (args.test_set or args.evaluate or args.model or args.models or
                args.model_tag or args.multi_label)
    if option == '--max-categories':
        return (args.evaluate or args.test_split or args.remote)
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
            if (flag == '--train' and
                    (i == len(args) - 1 or args[i + 1].startswith("--"))):
                train_stdin = True
            elif (flag == '--test' and
                    (i == len(args) - 1 or args[i + 1].startswith("--"))):
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
            literal_args[i] = '%s"%s"' % (prefix, literal)
    return "bigmler %s\n" % " ".join(literal_args)


def parse_and_check(parser, args, train_stdin, test_stdin):
    """Parses and checks the given args

    """
    command_args = parser.parse_args(args)

    # Checks options' compatibility
    if command_args.cross_validation_rate > 0 and (
            non_compatible(command_args, '--cross-validation-rate')):
        parser.error("Non compatible flags: --cross-validation-rate"
                     " cannot be used with --evaluate, --model,"
                     " --models, --model-tag or --multi-label. Usage:\n\n"
                     "bigmler --train data/iris.csv "
                     "--cross-validation-rate 0.1")

    if command_args.max_categories and (
            non_compatible(command_args, '--max-categories')):
        parser.error("Non compatible flags: --max-categories cannot "
                     "be used with --test-split, --remote or --evaluate.")

    if train_stdin and command_args.multi_label:
        parser.error("Reading multi-label training sets from stream "
                     "is not yet available.")

    if test_stdin and command_args.resume:
        parser.error("Can't resume when using stream reading test sets.")

    if (command_args.evaluate
        and not (command_args.training_set or command_args.source
                 or command_args.dataset)
        and not ((command_args.test_set or command_args.test_split) and
                 (command_args.model or
                  command_args.models or command_args.model_tag or
                  command_args.ensemble or command_args.ensembles or
                  command_args.ensemble_tag))):
        parser.error("Evaluation wrong syntax.\n"
                     "\nTry for instance:\n\nbigmler --train data/iris.csv"
                     " --evaluate\nbigmler --model "
                     "model/5081d067035d076151000011 --dataset "
                     "dataset/5081d067035d076151003423 --evaluate\n"
                     "bigmler --ensemble ensemble/5081d067035d076151003443"
                     " --dataset "
                     "dataset/5081d067035d076151003423 --evaluate")

    command_args.label_aggregates_list = []
    if command_args.label_aggregates:
        label_aggregates = command_args.label_aggregates.strip().lower()
        label_aggregates = label_aggregates.split(',')
        for aggregate in label_aggregates:
            if not aggregate in AGGREGATES:
                parser.error("Wrong value for the --label-aggregates "
                             "option. The allowed values are count, first and "
                             "last.")
            command_args.label_aggregates_list.append(aggregate)

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


def get_output_args(api, train_stdin, test_stdin, command_args, resume):
    """Returns the output args needed for the main bigmler computation process

    """
    if train_stdin:
        if test_stdin:
            sys.exit("The standard input can't be used both for training and"
                     " testing. Choose one of them")
        command_args.training_set = StringIO.StringIO(sys.stdin.read())
    elif test_stdin:
        command_args.test_set = StringIO.StringIO(sys.stdin.read())

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

    output_args = {
        "api": api,
        "training_set": command_args.training_set,
        "test_set": command_args.test_set,
        "output": command_args.predictions,
        "objective_field": command_args.objective_field,
        "name": command_args.name,
        "training_set_header": command_args.train_header,
        "test_set_header": command_args.test_header,
        "args": command_args,
        "resume": resume,
    }

    # Reads description if provided.
    if command_args.description:
        description_arg = u.read_description(command_args.description)
        output_args.update(description=description_arg)
    else:
        output_args.update(description="Created using BigMLer")

    # Parses fields if provided.
    if command_args.field_attributes:
        field_attributes_arg = (
            u.read_field_attributes(command_args.field_attributes))
        output_args.update(field_attributes=field_attributes_arg)
    if command_args.test_field_attributes:
        field_attributes_arg = (
            u.read_field_attributes(command_args.test_field_attributes))
        output_args.update(test_field_attributes=field_attributes_arg)

    # Parses types if provided.
    if command_args.types:
        types_arg = u.read_types(command_args.types)
        output_args.update(types=types_arg)
    if command_args.test_types:
        types_arg = u.read_types(command_args.test_types)
        output_args.update(test_types=types_arg)

    # Parses dataset fields if provided.
    if command_args.dataset_fields:
        dataset_fields_arg = map(str.strip,
                                 command_args.dataset_fields.split(','))
        output_args.update(dataset_fields=dataset_fields_arg)

    # Parses model input fields if provided.
    if command_args.model_fields:
        model_fields_arg = map(str.strip,
                               command_args.model_fields.split(','))
        output_args.update(model_fields=model_fields_arg)

    model_ids = []
    # Parses model/ids if provided.
    if command_args.models:
        model_ids = u.read_resources(command_args.models)
        output_args.update(model_ids=model_ids)

    # Retrieve model/ids if provided.
    if command_args.model_tag:
        model_ids = (model_ids +
                     u.list_ids(api.list_models,
                                "tags__in=%s" % command_args.model_tag))
        output_args.update(model_ids=model_ids)

    # Reads votes files in the provided directories.
    if command_args.votes_dirs:
        dirs = map(str.strip, command_args.votes_dirs.split(','))
        votes_path = os.path.dirname(command_args.predictions)
        votes_files = u.read_votes_files(dirs, votes_path)
        output_args.update(votes_files=votes_files)

    # Parses fields map if provided.
    if command_args.fields_map:
        fields_map_arg = u.read_fields_map(command_args.fields_map)
        output_args.update(fields_map=fields_map_arg)

    return output_args


def transform_args(command_args, flags, api, user_defaults):
    """Transforms the formatted argument strings into structured arguments

    """
    # Parses attributes in json format if provided
    command_args.json_args = {}

    json_attribute_options = {
        'source': command_args.source_attributes,
        'dataset': command_args.dataset_attributes,
        'model': command_args.model_attributes,
        'ensemble': command_args.ensemble_attributes,
        'evaluation': command_args.evaluation_attributes,
        'batch_prediction': command_args.batch_prediction_attributes}

    for resource_type, attributes_file in json_attribute_options.items():
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

    dataset_ids = None
    command_args.dataset_ids = []
    # Parses dataset/id if provided.
    if command_args.datasets:
        dataset_ids = u.read_datasets(command_args.datasets)
        if len(dataset_ids) == 1:
            command_args.dataset = dataset_ids[0]
        command_args.dataset_ids = dataset_ids

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
    if (command_args.method and command_args.method != COMBINATION_LABEL and
            not (command_args.method in COMBINATION_WEIGHTS.keys())):
        command_args.method = 0
    else:
        combiner_methods = dict([[value, key]
                                for key, value in COMBINER_MAP.items()])
        combiner_methods[COMBINATION_LABEL] = COMBINATION
        command_args.method = combiner_methods.get(command_args.method, 0)

    # Adds replacement=True if creating ensemble and nothing is specified
    if (command_args.number_of_models > 1 and
            not command_args.replacement and
            not '--no-replacement' in flags and
            not 'replacement' in user_defaults and
            not '--no-randomize' in flags and
            not 'randomize' in user_defaults and
            not '--sample-rate' in flags and
            not 'sample_rate' in user_defaults):
        command_args.replacement = True

    # Old value for --prediction-info='full data' maps to 'full'
    if command_args.prediction_info == 'full data':
        print "WARNING: 'full data' is a deprecated value. Use 'full' instead"
        command_args.prediction_info = FULL_FORMAT

    # Parses class, weight pairs for objective weight
    if command_args.objective_weights:
        objective_weights = (
            u.read_objective_weights(command_args.objective_weights))
        command_args.objective_weights_json = objective_weights

    command_args.multi_label_fields_list = []
    if command_args.multi_label_fields is not None:
        multi_label_fields = command_args.multi_label_fields.strip()
        command_args.multi_label_fields_list = multi_label_fields.split(',')
