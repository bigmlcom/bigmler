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
                           plural,
                           check_resource_error, log_created_resources)
from bigmler.reports import report

from bigmler.resourcesapi.common import set_basic_model_args, \
    update_json_args, configure_input_fields, update_sample_parameters_args,\
    wait_for_available_tasks, relative_input_fields, update_attributes
from bigmler.labels import label_model_args, get_all_labels
from bigmler.resourcesapi.common import SEED, EVALUATE_SAMPLE_RATE, \
    ALL_FIELDS_QS, BOOSTING_OPTIONS


def set_label_ensemble_args(args, labels, multi_label_data,
                            number_of_ensembles, fields):
    """Set of args needed to build an ensemble per label

    """

    if not args.model_fields_:
        args.model_fields_ = relative_input_fields(fields, args.model_fields_)
    if args.objective_field is None:
        args.objective_field = fields.objective_field
    try:
        objective_id = fields.field_id(args.objective_field)
    except ValueError as exc:
        sys.exit(exc)
    objective_field = fields.fields[objective_id]['name']
    ensemble_args_list = []

    for index in range(number_of_ensembles - 1, -1, -1):
        label = labels[index]
        all_labels = get_all_labels(multi_label_data)
        (new_name, label_field, single_label_fields) = label_model_args(
            args.name, label, all_labels, args.model_fields_,
            objective_field)
        ensemble_args = set_ensemble_args(args, name=new_name,
                                          objective_id=label_field,
                                          model_fields=single_label_fields,
                                          fields=fields)
        if multi_label_data is not None:
            ensemble_args.update(
                user_metadata={'multi_label_data': multi_label_data})

        ensemble_args_list.append(ensemble_args)
    return ensemble_args_list


def set_ensemble_args(args, name=None,
                      objective_id=None, model_fields=None, fields=None):
    """Return ensemble arguments dict

    """
    if name is None:
        name = args.name
    if objective_id is None:
        objective_id = args.objective_id_
    if model_fields is None:
        model_fields = args.model_fields_

    ensemble_args = set_basic_model_args(args, name)
    ensemble_args.update({
        "missing_splits": args.missing_splits,
        "ensemble_sample": {"seed": SEED if args.ensemble_sample_seed is None \
            else args.ensemble_sample_seed},
        "seed": SEED if args.seed is None else args.seed
    })
    if objective_id is not None and fields is not None:
        ensemble_args.update({"objective_field": objective_id})

    if args.boosting:
        boosting_args = {}
        for option in BOOSTING_OPTIONS:
            if hasattr(args, option) and getattr(args, option) is not None:
                boosting_args.update({option: getattr(args, option)})
        ensemble_args.update({"boosting": boosting_args})
    else:
        ensemble_args.update({"number_of_models": args.number_of_models})

    # If evaluate flag is on and no test_split flag is provided,
    # we choose a deterministic sampling with
    # args.sample_rate (80% by default) of the data to create the model

    if (args.evaluate and args.test_split == 0 and
            args.test_datasets is None and not args.dataset_off):
        ensemble_args.update({"seed": SEED})
        if args.sample_rate == 1:
            args.sample_rate = EVALUATE_SAMPLE_RATE

    if model_fields and fields is not None:
        input_fields = configure_input_fields(fields, model_fields)
        ensemble_args.update(input_fields=input_fields)

    if args.pruning and args.pruning != 'smart':
        ensemble_args.update(stat_pruning=(args.pruning == 'statistical'))
    if args.node_threshold > 0:
        ensemble_args.update(node_threshold=args.node_threshold)
    if args.balance:
        ensemble_args.update(balance_objective=True)
    if args.weight_field:
        try:
            weight_field = fields.field_id(args.weight_field)
        except ValueError as exc:
            sys.exit(exc)
        ensemble_args.update(weight_field=weight_field)
    if args.objective_weights:
        ensemble_args.update(objective_weights=args.objective_weights_json)
    if args.random_candidates:
        ensemble_args.update(random_candidates=args.random_candidates)

    update_attributes(ensemble_args, args.json_args.get('model'))

    ensemble_args = update_sample_parameters_args(ensemble_args, args)

    ensemble_args["ensemble_sample"].update( \
        {"rate": args.ensemble_sample_rate,
         "replacement": args.ensemble_sample_replacement})

    if 'ensemble' in args.json_args:
        update_json_args(ensemble_args, args.json_args.get('ensemble'), fields)

    return ensemble_args


def create_ensembles(datasets, ensemble_ids, ensemble_args, args,
                     number_of_ensembles=1,
                     api=None, path=None, session_file=None, log=None):
    """Create ensembles from input data

    """

    if api is None:
        api = bigml.api.BigML()
    ensembles = ensemble_ids[:]
    existing_ensembles = len(ensembles)
    model_ids = []
    ensemble_args_list = []
    if isinstance(ensemble_args, list):
        ensemble_args_list = ensemble_args
    if args.dataset_off and args.evaluate:
        args.test_dataset_ids = datasets[:]
    if not args.multi_label:
        datasets = datasets[existing_ensembles:]
    if number_of_ensembles > 0:
        message = dated("Creating %s.\n" %
                        plural("ensemble", number_of_ensembles))
        log_message(message, log_file=session_file,
                    console=args.verbosity)
        inprogress = []
        for i in range(0, number_of_ensembles):
            wait_for_available_tasks(inprogress, args.max_parallel_ensembles,
                                     api, "ensemble",
                                     wait_step=args.number_of_models)

            if ensemble_args_list:
                ensemble_args = ensemble_args_list[i]

            if args.dataset_off and args.evaluate:
                multi_dataset = args.test_dataset_ids[:]
                del multi_dataset[i + existing_ensembles]
                ensemble = api.create_ensemble(multi_dataset,
                                               ensemble_args,
                                               retries=None)
            else:
                ensemble = api.create_ensemble(datasets, ensemble_args,
                                               retries=None)
            ensemble_id = check_resource_error(ensemble,
                                               "Failed to create ensemble: ")
            log_message("%s\n" % ensemble_id, log_file=log)
            ensemble_ids.append(ensemble_id)
            inprogress.append(ensemble_id)
            ensembles.append(ensemble)
            log_created_resources("ensembles", path, ensemble_id,
                                  mode='a')
        models, model_ids = retrieve_ensembles_models(ensembles, api, path)
        if number_of_ensembles < 2 and args.verbosity:
            message = dated("Ensemble created: %s\n" %
                            get_url(ensemble))
            log_message(message, log_file=session_file,
                        console=args.verbosity)
            if args.reports:
                report(args.reports, path, ensemble)

    return ensembles, ensemble_ids, models, model_ids


def retrieve_ensembles_models(ensembles, api, path=None):
    """Retrieves the models associated to a list of ensembles

    """
    models = []
    model_ids = []
    for index, ensemble in enumerate(ensembles):
        if (isinstance(ensemble, str) or
                bigml.api.get_status(ensemble)['code'] != bigml.api.FINISHED):
            try:
                ensemble = check_resource(ensemble, api.get_ensemble,
                                          raise_on_error=True)
                ensembles[index] = ensemble
            except Exception as exception:
                sys.exit("Failed to get a finished ensemble: %s" %
                         str(exception))
        model_ids.extend(ensemble['object']['models'])
    if path is not None:
        for model_id in model_ids:
            log_created_resources("models", path, model_id, mode='a')
    models = model_ids[:]
    models[0] = check_resource(models[0], api.get_model,
                               query_string=ALL_FIELDS_QS,
                               raise_on_error=True)
    return models, model_ids


def get_ensemble(ensemble, api=None, verbosity=True, session_file=None):
    """Retrieves remote ensemble in its actual status

    """
    if api is None:
        api = bigml.api.BigML()
    if (isinstance(ensemble, str) or
            bigml.api.get_status(ensemble)['code'] != bigml.api.FINISHED):
        message = dated("Retrieving ensemble. %s\n" %
                        get_url(ensemble))
        log_message(message, log_file=session_file,
                    console=verbosity)
        ensemble = check_resource(ensemble, api.get_ensemble,
                                  raise_on_error=True)
        check_resource_error(ensemble, "Failed to get ensemble: ")
    return ensemble
