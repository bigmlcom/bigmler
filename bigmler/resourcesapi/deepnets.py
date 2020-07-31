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
                           is_shared, plural,
                           check_resource_error, log_created_resources)
from bigmler.reports import report

from bigmler.resourcesapi.common import set_basic_model_args, \
    update_json_args, configure_input_fields, update_sample_parameters_args,\
    wait_for_available_tasks, get_basic_seed

from bigmler.resourcesapi.common import SEED, FIELDS_QS, EVALUATE_SAMPLE_RATE, \
    ALL_FIELDS_QS


def set_deepnet_args(args, name=None, fields=None,
                     objective_id=None,
                     deepnet_fields=None):
    """Return deepnet arguments dict

    """
    if name is None:
        name = args.name
    if deepnet_fields is None:
        deepnet_fields = args.deepnet_fields_
    if objective_id is None:
        objective_id = args.objective_id_

    deepnet_args = set_basic_model_args(args, name)
    deepnet_args.update({
        "seed": SEED if args.seed is None else args.seed
    })

    if objective_id is not None and fields is not None:
        deepnet_args.update({"objective_field": objective_id})
    if deepnet_fields and fields is not None:
        input_fields = configure_input_fields(fields, deepnet_fields)
        deepnet_args.update(input_fields=input_fields)
    if ((args.evaluate and args.test_split == 0 and args.test_datasets is None)
            or args.cross_validation_rate > 0):
        deepnet_args.update(seed=SEED)
        if args.cross_validation_rate > 0:
            args.sample_rate = 1 - args.cross_validation_rate
            args.replacement = False
        elif (args.sample_rate == 1 and args.test_datasets is None
              and not args.dataset_off):
            args.sample_rate = EVALUATE_SAMPLE_RATE
    deepnet_args.update({"sample_rate": args.sample_rate})


    if args.batch_normalization is not None:
        deepnet_args.update({"batch_normalization": args.batch_normalization})
    if args.dropout_rate:
        deepnet_args.update({"dropout_rate": args.dropout_rate})

    if args.hidden_layers is not None:
        deepnet_args.update({"hidden_layers": args.hidden_layers_})

    if args.learn_residuals is not None:
        deepnet_args.update( \
            {"learn_residuals": args.learn_residuals})

    if args.max_iterations is not None:
        deepnet_args.update(\
            {"learning_rate": args.learning_rate})

    if args.max_training_time is not None:
        deepnet_args.update(\
            {"max_training_time": args.max_training_time})

    if args.number_of_hidden_layers is not None:
        deepnet_args.update(\
            {"number_of_hidden_layers": args.number_of_hidden_layers})

    if args.number_of_model_candidates is not None:
        deepnet_args.update(\
            {"number_of_model_candidates": args.number_of_model_candidates})

    if args.search is not None:
        deepnet_args.update(\
            {"search": args.search})

    if args.suggest_structure is not None:
        deepnet_args.update(\
            {"suggest_structure": args.suggest_structure})

    if not args.missing_numerics:
        deepnet_args.update(\
            {"missing_numerics": args.missing_numerics})

    if args.tree_embedding:
        deepnet_args.update(\
            {"tree_embedding": args.tree_embedding})

    deepnet_args = update_sample_parameters_args( \
        deepnet_args, args)

    if 'deepnet' in args.json_args:
        update_json_args(deepnet_args,
                         args.json_args.get('deepnet'),
                         fields)
    return deepnet_args


def create_deepnets(datasets, deepnet_ids,
                    deepnet_args,
                    args, api=None, path=None,
                    session_file=None, log=None):
    """Create remote deepnets

    """
    if api is None:
        api = bigml.api.BigML()

    deepnets = deepnet_ids[:]
    existing_deepnets = len(deepnets)
    deepnet_args_list = []
    datasets = datasets[existing_deepnets:]
    # if resuming and all deepnets were created,
    # there will be no datasets left
    if datasets:
        if isinstance(deepnet_args, list):
            deepnet_args_list = deepnet_args

        # Only one deepnet per command, at present
        number_of_deepnets = 1
        message = dated("Creating %s.\n" %
                        plural("deepnet",
                               number_of_deepnets))
        log_message(message, log_file=session_file,
                    console=args.verbosity)

        query_string = FIELDS_QS
        inprogress = []
        for i in range(0, number_of_deepnets):
            wait_for_available_tasks(inprogress,
                                     args.max_parallel_deepnets,
                                     api, "deepnet")
            if deepnet_args_list:
                deepnet_args = deepnet_args_list[i]
            if args.cross_validation_rate > 0:
                new_seed = get_basic_seed(i + existing_deepnets)
                deepnet_args.update(seed=new_seed)

            if (args.test_datasets and args.evaluate):
                dataset = datasets[i]
                deepnet = api.create_deepnet( \
                    dataset, deepnet_args, retries=None)
            elif args.dataset_off and args.evaluate:
                multi_dataset = args.test_dataset_ids[:]
                del multi_dataset[i + existing_deepnets]
                deepnet = api.create_deepnet( \
                    multi_dataset, deepnet_args, retries=None)
            else:
                deepnet = api.create_deepnet( \
                    datasets, deepnet_args, retries=None)
            deepnet_id = check_resource_error( \
                deepnet, "Failed to create deepnet: ")
            log_message("%s\n" % deepnet_id, log_file=log)
            deepnet_ids.append(deepnet_id)
            inprogress.append(deepnet_id)
            deepnets.append(deepnet)
            log_created_resources("deepnets",
                                  path,
                                  deepnet_id, mode='a')

        if args.verbosity:
            if bigml.api.get_status(deepnet)['code'] != \
                    bigml.api.FINISHED:
                try:
                    deepnet = check_resource( \
                        deepnet, api.get_deepnet,
                        query_string=query_string,
                        raise_on_error=True)
                except Exception as exception:
                    sys.exit("Failed to get a finished deepnet:"
                             " %s" %
                             str(exception))
                deepnets[0] = deepnet
            message = dated("Deepnet created: %s\n" %
                            get_url(deepnet))
            log_message(message, log_file=session_file,
                        console=args.verbosity)
            if args.reports:
                report(args.reports, path, deepnet)

    return deepnets, deepnet_ids


def get_deepnets(deepnet_ids, args, api=None, session_file=None):
    """Retrieves remote deepnet in its actual status

    """
    if api is None:
        api = bigml.api.BigML()

    deepnet_id = ""
    deepnets = deepnet_ids
    deepnet_id = deepnet_ids[0]
    message = dated("Retrieving %s. %s\n" %
                    (plural("deepnet", len(deepnet_ids)),
                     get_url(deepnet_id)))
    log_message(message, log_file=session_file, console=args.verbosity)
    # only one deepnet to predict at present
    try:
        # we need the whole fields structure when exporting fields
        query_string = FIELDS_QS if not args.export_fields else ALL_FIELDS_QS
        deepnet = check_resource(deepnet_ids[0],
                                 api.get_deepnet,
                                 query_string=query_string,
                                 raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a finished deepnet: %s" % \
            str(exception))
    deepnets[0] = deepnet

    return deepnets, deepnet_ids


def update_deepnet(deepnet, deepnet_args,
                   args, api=None, path=None, session_file=None):
    """Updates deepnet properties

    """
    if api is None:
        api = bigml.api.BigML()

    message = dated("Updating deepnet. %s\n" %
                    get_url(deepnet))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    deepnet = api.update_deepnet(deepnet, deepnet_args)
    check_resource_error(deepnet,
                         "Failed to update deepnet: %s"
                         % deepnet['resource'])
    deepnet = check_resource(deepnet,
                             api.get_deepnet,
                             query_string=FIELDS_QS,
                             raise_on_error=True)
    if is_shared(deepnet):
        message = dated("Shared deepnet link. %s\n" %
                        get_url(deepnet, shared=True))
        log_message(message, log_file=session_file, console=args.verbosity)
        if args.reports:
            report(args.reports, path, deepnet)

    return deepnet
