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

import bigml.api

from bigmler.utils import (dated, get_url, log_message, check_resource,
                           plural, is_shared,
                           check_resource_error, log_created_resources)
from bigmler.reports import report

from bigmler.resourcesapi.common import set_basic_model_args, \
    configure_input_fields, update_sample_parameters_args, \
    update_json_args, wait_for_available_tasks, get_basic_seed, \
    relative_input_fields, get_all_labels, label_model_args

from bigmler.resourcesapi.common import SEED, FIELDS_QS, \
    ALL_FIELDS_QS, EVALUATE_SAMPLE_RATE


def set_model_args(args, name=None, objective_id=None, fields=None,
                   model_fields=None, other_label=None):
    """Return model arguments dict

    """
    if name is None:
        name = args.name
    if objective_id is None and args.max_categories is None:
        objective_id = args.objective_id_
    if args.max_categories > 0:
        objective_id = args.objective_field
    if model_fields is None:
        model_fields = args.model_fields_

    model_args = set_basic_model_args(args, name)
    model_args.update({"missing_splits": args.missing_splits})
    if objective_id is not None and fields is not None:
        model_args.update({"objective_field": objective_id})

    # If evaluate flag is on and no test_split flag is provided,
    # we choose a deterministic sampling with
    # args.sample_rate (80% by default) of the data to create the model
    # If cross_validation_rate = n/100, then we choose to run 2 * n evaluations
    # by holding out a n% of randomly sampled data.

    if ((args.evaluate and args.test_split == 0 and args.test_datasets is None)
            or args.cross_validation_rate > 0):
        model_args.update(seed=SEED)
        if args.cross_validation_rate > 0:
            args.sample_rate = 1 - args.cross_validation_rate
            args.replacement = False
        elif (args.sample_rate == 1 and args.test_datasets is None
              and not args.dataset_off):
            args.sample_rate = EVALUATE_SAMPLE_RATE
    if model_fields and fields is not None:
        input_fields = configure_input_fields(
            fields, model_fields, by_name=(args.max_categories > 0))
        model_args.update(input_fields=input_fields)

    if args.pruning and args.pruning != 'smart':
        model_args.update(stat_pruning=(args.pruning == 'statistical'))

    if args.node_threshold > 0:
        model_args.update(node_threshold=args.node_threshold)

    if args.balance:
        model_args.update(balance_objective=True)

    if args.split_field:
        model_args.update(split_field=args.split_field)

    if args.focus_field:
        model_args.update(focus_field=args.focus_field)

    if args.weight_field:
        try:
            weight_field = fields.field_id(args.weight_field)
        except ValueError as exc:
            sys.exit(exc)
        model_args.update(weight_field=weight_field)

    if args.objective_weights:
        model_args.update(objective_weights=args.objective_weights_json)

    if args.max_categories > 0:
        model_args.update(
            user_metadata={'other_label': other_label,
                           'max_categories': args.max_categories})

    model_args = update_sample_parameters_args(model_args, args)

    if 'model' in args.json_args:
        update_json_args(model_args, args.json_args.get('model'), fields)

    return model_args


def set_label_model_args(args, fields, labels, multi_label_data):
    """Set of args needed to build a model per label

    """

    objective_field = args.objective_field
    if not args.model_fields_:
        model_fields = []
    else:
        model_fields = relative_input_fields(fields, args.model_fields_)
    if objective_field is None:
        objective_field = fields.objective_field
    try:
        objective_id = fields.field_id(objective_field)
        objective_field = fields.field_name(objective_id)
    except ValueError as exc:
        sys.exit(exc)
    all_labels = get_all_labels(multi_label_data)
    model_args_list = []

    for index in range(args.number_of_models - 1, -1, -1):
        label = labels[index]
        (new_name, label_field, single_label_fields) = label_model_args(
            args.name, label, all_labels, model_fields,
            objective_field)
        model_args = set_model_args(args, name=new_name,
                                    objective_id=label_field, fields=fields,
                                    model_fields=single_label_fields)
        if multi_label_data is not None:
            model_args.update(
                user_metadata={'multi_label_data': multi_label_data})
        model_args_list.append(model_args)
    return model_args_list


def create_models(datasets, model_ids, model_args,
                  args, api=None, path=None,
                  session_file=None, log=None):
    """Create remote models

    """
    if api is None:
        api = bigml.api.BigML()

    models = model_ids[:]
    existing_models = len(models)
    model_args_list = []
    if args.dataset_off and args.evaluate:
        args.test_dataset_ids = datasets[:]
    if not args.multi_label:
        datasets = datasets[existing_models:]
    # if resuming and all models were created, there will be no datasets left
    if datasets:
        dataset = datasets[0]
        if isinstance(model_args, list):
            model_args_list = model_args
        if args.number_of_models > 0:
            message = dated("Creating %s.\n" %
                            plural("model", args.number_of_models))
            log_message(message, log_file=session_file,
                        console=args.verbosity)

            single_model = args.number_of_models == 1 and existing_models == 0
            # if there's more than one model the first one must contain
            # the entire field structure to be used as reference.
            query_string = (FIELDS_QS if single_model and (args.test_header \
                and not args.export_fields) else ALL_FIELDS_QS)
            inprogress = []
            for i in range(0, args.number_of_models):
                wait_for_available_tasks(inprogress, args.max_parallel_models,
                                         api, "model")
                if model_args_list:
                    model_args = model_args_list[i]
                if args.cross_validation_rate > 0:
                    new_seed = get_basic_seed(i + existing_models)
                    model_args.update(seed=new_seed)
                # one model per dataset (--max-categories or single model)
                if (args.max_categories > 0 or
                        (args.test_datasets and args.evaluate)):
                    dataset = datasets[i]
                    model = api.create_model(dataset, model_args, retries=None)
                elif args.dataset_off and args.evaluate:
                    multi_dataset = args.test_dataset_ids[:]
                    del multi_dataset[i + existing_models]
                    model = api.create_model(multi_dataset, model_args,
                                             retries=None)
                else:
                    model = api.create_model(datasets, model_args,
                                             retries=None)
                model_id = check_resource_error(model,
                                                "Failed to create model: ")
                log_message("%s\n" % model_id, log_file=log)
                model_ids.append(model_id)
                inprogress.append(model_id)
                models.append(model)
                log_created_resources("models", path, model_id, mode='a')

            if args.number_of_models < 2 and args.verbosity:
                if bigml.api.get_status(model)['code'] != bigml.api.FINISHED:
                    try:
                        model = check_resource(model, api.get_model,
                                               query_string=query_string,
                                               raise_on_error=True)
                    except Exception as exception:
                        sys.exit("Failed to get a finished model: %s" %
                                 str(exception))
                    models[0] = model
                message = dated("Model created: %s\n" %
                                get_url(model))
                log_message(message, log_file=session_file,
                            console=args.verbosity)
                if args.reports:
                    report(args.reports, path, model)

    return models, model_ids


def create_model(cluster, model_args, args, api=None,
                 path=None, session_file=None, log=None, model_type=None):
    """Creates remote model from cluster and centroid

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Creating model.\n")
    log_message(message, log_file=session_file, console=args.verbosity)
    model = api.create_model(cluster, model_args, retries=None)
    suffix = "" if model_type is None else "_%s" % model_type
    log_created_resources("models%s" % suffix, path,
                          bigml.api.get_model_id(model), mode='a')
    model_id = check_resource_error(model, "Failed to create model: ")
    try:
        model = check_resource(model, api.get_model,
                               query_string=ALL_FIELDS_QS,
                               raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a finished model: %s" % str(exception))
    message = dated("Model created: %s\n" % get_url(model))
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % model_id, log_file=log)
    if args.reports:
        report(args.reports, path, model)
    return model


def update_model(model, model_args, args,
                 api=None, path=None, session_file=None):
    """Updates model properties

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Updating model. %s\n" %
                    get_url(model))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    model = api.update_model(model, model_args)
    check_resource_error(model, "Failed to update model: %s"
                         % model['resource'])
    model = check_resource(model, api.get_model, query_string=ALL_FIELDS_QS,
                           raise_on_error=True)
    if is_shared(model):
        message = dated("Shared model link. %s\n" %
                        get_url(model, shared=True))
        log_message(message, log_file=session_file, console=args.verbosity)
        if args.reports:
            report(args.reports, path, model)

    return model


def get_models(model_ids, args, api=None, session_file=None):
    """Retrieves remote models in its actual status

    """
    if api is None:
        api = bigml.api.BigML()
    model_id = ""
    models = model_ids
    single_model = len(model_ids) == 1
    if single_model:
        model_id = model_ids[0]
    message = dated("Retrieving %s. %s\n" %
                    (plural("model", len(model_ids)),
                     get_url(model_id)))
    log_message(message, log_file=session_file, console=args.verbosity)
    if len(model_ids) < args.max_batch_models:
        models = []
        for model in model_ids:
            try:
                # if there's more than one model the first one must contain
                # the entire field structure to be used as reference.
                query_string = (
                    ALL_FIELDS_QS if (
                        (not single_model and (not models or
                                               args.multi_label)) or
                        not args.test_header)
                    else FIELDS_QS)
                model = check_resource(model, api.get_model,
                                       query_string=query_string,
                                       raise_on_error=True)
            except Exception as exception:
                sys.exit("Failed to get a finished model: %s" %
                         str(exception))
            models.append(model)
        model = models[0]
    else:
        try:
            query_string = (ALL_FIELDS_QS if not single_model or
                            not args.test_header
                            else FIELDS_QS)
            model = check_resource(model_ids[0], api.get_model,
                                   query_string=query_string,
                                   raise_on_error=True)
        except Exception as exception:
            sys.exit("Failed to get a finished model: %s" % str(exception))
        models[0] = model

    return models, model_ids


def set_publish_model_args(args):
    """Set args to publish model

    """
    public_model = {}
    if args.black_box:
        public_model = {"private": False}
    if args.white_box:
        public_model = {"private": False, "white_box": True}
        if args.model_price:
            public_model.update(price=args.model_price)
        if args.cpp:
            public_model.update(credits_per_prediction=args.cpp)
    return public_model
