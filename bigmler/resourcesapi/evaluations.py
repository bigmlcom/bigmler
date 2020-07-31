# -*- coding: utf-8 -*-
#
# Copyright 2020 BigML
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
"""Resources management functions

"""



import sys

try:
    import simplejson as json
except ImportError:
    import json

import bigml.api

from bigml.multivote import THRESHOLD_CODE

from bigmler.utils import (dated, get_url, log_message, check_resource,
                           check_resource_error, log_created_resources,
                           is_shared)
from bigmler.reports import report

from bigmler.resourcesapi.common import set_basic_args, map_fields, \
    update_json_args, get_basic_seed, wait_for_available_tasks, utf8, \
    save_txt_and_json
from bigmler.labels import label_model_args
from bigmler.resourcesapi.common import EVALUATE_SAMPLE_RATE, \
    SEED


def set_evaluation_args(args, fields=None,
                        dataset_fields=None, name=None):
    """Return evaluation args dict

    """
    if name is None:
        name = args.name
    evaluation_args = set_basic_args(args, name)

    if hasattr(args, 'method') and (args.number_of_models > 1
                                    or args.ensemble):
        evaluation_args.update(combiner=args.method)
    if hasattr(args, 'method') and args.method:
        evaluation_args.update({"combiner": args.method})
        if args.method == THRESHOLD_CODE:
            threshold = {}
            if hasattr(args, 'threshold') and args.threshold is not None:
                threshold.update(k=args.threshold)
            if hasattr(args, 'threshold_class') \
                    and args.threshold_class is not None:
                threshold.update({"class": args.threshold_class})
            evaluation_args.update(threshold=threshold)
    if args.fields_map_ and fields is not None:
        if dataset_fields is None:
            dataset_fields = fields
        evaluation_args.update({"fields_map": map_fields(args.fields_map_,
                                                         fields,
                                                         dataset_fields)})
    if hasattr(args, 'missing_strategy') and args.missing_strategy:
        evaluation_args.update(missing_strategy=args.missing_strategy)
    if 'evaluation' in args.json_args:
        update_json_args(
            evaluation_args, args.json_args.get('evaluation'), fields)
    # if evaluating time series we need to use ranges
    if args.subcommand == "time-series" and args.test_split == 0 and \
            not args.has_test_datasets_:
        args.range_ = [int(args.max_rows * EVALUATE_SAMPLE_RATE) + 1,
                       args.max_rows]
        evaluation_args.update({"range": args.range_})
        return evaluation_args
    # Two cases to use out_of_bag and sample_rate: standard evaluations where
    # only the training set is provided, and cross_validation
    # [--dataset|--test] [--model|--models|--model-tag|--ensemble] --evaluate
    if (((hasattr(args, "dataset") and args.dataset) or args.test_set)
            and args.has_supervised_):
        return evaluation_args
    # [--train|--dataset] --test-split --evaluate
    if args.test_split > 0 and (args.training_set or args.dataset):
        return evaluation_args
    # --datasets --test-datasets or equivalents
    #if args.datasets and (args.test_datasets or args.dataset_off):
    if args.has_datasets_ and (args.has_test_datasets_ or args.dataset_off):
        return evaluation_args
    if args.sample_rate == 1:
        args.sample_rate = EVALUATE_SAMPLE_RATE
    evaluation_args.update(out_of_bag=True, seed=SEED,
                           sample_rate=args.sample_rate)
    return evaluation_args


def set_label_evaluation_args(args, labels, all_labels,
                              number_of_evaluations, fields, dataset_fields,
                              objective_field):
    """Set of args needed to build an evaluation per label

    """
    if objective_field is None:
        try:
            objective_id = fields.field_id(fields.objective_field)
        except ValueError as exc:
            sys.exit(exc)
        objective_field = fields.fields[objective_id]['name']
    evaluation_args_list = []

    for index in range(number_of_evaluations - 1, -1, -1):
        label = labels[index]
        new_name = label_model_args(
            args.name, label, all_labels, [], objective_field)[0]
        evaluation_args = set_evaluation_args(args,
                                              fields=fields,
                                              dataset_fields=dataset_fields,
                                              name=new_name)
        evaluation_args_list.append(evaluation_args)
    return evaluation_args_list


def create_evaluations(model_or_ensemble_ids, datasets, evaluation_args,
                       args, api=None,
                       path=None, session_file=None, log=None,
                       existing_evaluations=0):
    """Create evaluations for a list of models

       ``model_or_ensemble_ids``: list of model or ensemble ids to create
                                  an evaluation of
       ``datasets``: dataset objects or ids to evaluate with
       ``evaluation_args``: arguments for the ``create_evaluation`` call
       ``args``: input values for bigmler flags
       ``api``: api to remote objects in BigML
       ``path``: directory to store the BigMLer generated files in
       ``session_file``: file to store the messages of that session
       ``log``: user provided log file
       ``existing_evaluations``: evaluations found when attempting resume
    """

    evaluations = []
    dataset = datasets[0]
    evaluation_args_list = []
    if isinstance(evaluation_args, list):
        evaluation_args_list = evaluation_args
    if api is None:
        api = bigml.api.BigML()
    remaining_ids = model_or_ensemble_ids[existing_evaluations:]
    if args.test_dataset_ids or args.dataset_off:
        remaining_datasets = datasets[existing_evaluations:]
    number_of_evaluations = len(remaining_ids)
    message = dated("Creating evaluations.\n")
    log_message(message, log_file=session_file,
                console=args.verbosity)

    inprogress = []
    for i in range(0, number_of_evaluations):
        model = remaining_ids[i]
        if args.test_dataset_ids or args.dataset_off:
            dataset = remaining_datasets[i]
        wait_for_available_tasks(inprogress, args.max_parallel_evaluations,
                                 api, "evaluation")

        if evaluation_args_list != []:
            evaluation_args = evaluation_args_list[i]
        if args.cross_validation_rate > 0:
            new_seed = get_basic_seed(i + existing_evaluations)
            evaluation_args.update(seed=new_seed)
        evaluation = api.create_evaluation(model, dataset, evaluation_args,
                                           retries=None)
        evaluation_id = check_resource_error(evaluation,
                                             "Failed to create evaluation: ")
        inprogress.append(evaluation_id)
        log_created_resources("evaluations", path, evaluation_id,
                              mode='a')
        evaluations.append(evaluation)
        log_message("%s\n" % evaluation['resource'], log_file=log)

    if (args.number_of_evaluations < 2 and len(evaluations) == 1
            and args.verbosity):
        evaluation = evaluations[0]
        if bigml.api.get_status(evaluation)['code'] != bigml.api.FINISHED:
            try:
                evaluation = check_resource(evaluation, api.get_evaluation,
                                            raise_on_error=True)
            except Exception as exception:
                sys.exit("Failed to get a finished evaluation: %s" %
                         str(exception))
            evaluations[0] = evaluation
        message = dated("Evaluation created: %s\n" %
                        get_url(evaluation))
        log_message(message, log_file=session_file,
                    console=args.verbosity)
        if args.reports:
            report(args.reports, path, evaluation)

    return evaluations


def get_evaluation(evaluation, api=None, verbosity=True, session_file=None):
    """Retrieves evaluation in its actual state

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Retrieving evaluation. %s\n" %
                    get_url(evaluation))
    log_message(message, log_file=session_file, console=verbosity)
    try:
        evaluation = check_resource(evaluation, api.get_evaluation,
                                    raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a finished evaluation: %s" % str(exception))
    return evaluation


def update_evaluation(evaluation, evaluation_args, args,
                      api=None, path=None, session_file=None):
    """Updates evaluation properties

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Updating evaluation. %s\n" %
                    get_url(evaluation))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    evaluation = api.update_evaluation(evaluation, evaluation_args)
    check_resource_error(evaluation, "Failed to update evaluation: %s"
                         % evaluation['resource'])
    evaluation = check_resource(evaluation, api.get_evaluation,
                                raise_on_error=True)
    if is_shared(evaluation):
        message = dated("Shared evaluation link. %s\n" %
                        get_url(evaluation, shared=True))
        log_message(message, log_file=session_file, console=args.verbosity)
        if args.reports:
            report(args.reports, path, evaluation)

    return evaluation


def save_evaluation(evaluation, output, api=None):
    """Creates the evaluation .txt and .json files

    """
    if api is None:
        api = bigml.api.BigML()
    evaluation = evaluation.get('object', evaluation).get('result', evaluation)
    save_txt_and_json(evaluation, output, api=api)
