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
    update_json_args, wait_for_available_tasks, get_basic_seed

from bigmler.resourcesapi.common import SEED, FIELDS_QS, \
    ALL_FIELDS_QS, EVALUATE_SAMPLE_RATE


def set_linear_regression_args(args, name=None, fields=None,
                               objective_id=None,
                               linear_regression_fields=None):
    """Return linear regression arguments dict

    """
    if name is None:
        name = args.name
    if linear_regression_fields is None:
        linear_regression_fields = args.linear_regression_fields_
    if objective_id is None:
        objective_id = args.objective_id_

    linear_regression_args = set_basic_model_args(args, name)
    linear_regression_args.update({
        "seed": SEED if args.seed is None else args.seed
    })

    if objective_id is not None and fields is not None:
        linear_regression_args.update({"objective_field": objective_id})
    if linear_regression_fields and fields is not None:
        input_fields = configure_input_fields(fields, linear_regression_fields)
        linear_regression_args.update(input_fields=input_fields)
    if ((args.evaluate and args.test_split == 0 and args.test_datasets is None)
            or args.cross_validation_rate > 0):
        linear_regression_args.update(seed=SEED)
        if args.cross_validation_rate > 0:
            args.sample_rate = 1 - args.cross_validation_rate
            args.replacement = False
        elif (args.sample_rate == 1 and args.test_datasets is None
              and not args.dataset_off):
            args.sample_rate = EVALUATE_SAMPLE_RATE
    linear_regression_args.update({"sample_rate": args.sample_rate})
    linear_regression_args.update({"bias": args.bias})
    if args.field_codings is not None:
        linear_regression_args.update(\
            {"field_codings": args.field_codings_})

    linear_regression_args = update_sample_parameters_args( \
        linear_regression_args, args)

    if 'linear_regression' in args.json_args:
        update_json_args(linear_regression_args,
                         args.json_args.get('linear_regression'),
                         fields)
    return linear_regression_args


def create_linear_regressions(datasets, linear_regression_ids,
                              linear_regression_args,
                              args, api=None, path=None,
                              session_file=None, log=None):
    """Create remote linear regressions

    """
    if api is None:
        api = bigml.api.BigML()

    linear_regressions = linear_regression_ids[:]
    existing_linear_regressions = len(linear_regressions)
    linear_regression_args_list = []
    datasets = datasets[existing_linear_regressions:]
    # if resuming and all linear regressions were created,
    # there will be no datasets left
    if datasets:
        if isinstance(linear_regression_args, list):
            linear_regression_args_list = linear_regression_args

        # Only one linear regression per command, at present
        number_of_linear_regressions = 1
        message = dated("Creating %s.\n" %
                        plural("linear regression",
                               number_of_linear_regressions))
        log_message(message, log_file=session_file,
                    console=args.verbosity)

        query_string = FIELDS_QS
        inprogress = []
        for i in range(0, number_of_linear_regressions):
            wait_for_available_tasks(inprogress,
                                     args.max_parallel_linear_regressions,
                                     api, "linearregression")
            if linear_regression_args_list:
                linear_regression_args = linear_regression_args_list[i]
            if args.cross_validation_rate > 0:
                new_seed = get_basic_seed(i + existing_linear_regressions)
                linear_regression_args.update(seed=new_seed)

            if (args.test_datasets and args.evaluate):
                dataset = datasets[i]
                linear_regression = api.create_linear_regression( \
                    dataset, linear_regression_args, retries=None)
            elif args.dataset_off and args.evaluate:
                multi_dataset = args.test_dataset_ids[:]
                del multi_dataset[i + existing_linear_regressions]
                linear_regression = api.create_linear_regression( \
                    multi_dataset, linear_regression_args, retries=None)
            else:
                linear_regression = api.create_linear_regression( \
                datasets, linear_regression_args, retries=None)
            linear_regression_id = check_resource_error( \
                linear_regression, "Failed to create linear regression: ")
            log_message("%s\n" % linear_regression_id, log_file=log)
            linear_regression_ids.append(linear_regression_id)
            inprogress.append(linear_regression_id)
            linear_regressions.append(linear_regression)
            log_created_resources("linear_regressions",
                                  path,
                                  linear_regression_id, mode='a')

        if args.verbosity:
            if bigml.api.get_status(linear_regression)['code'] != \
                    bigml.api.FINISHED:
                try:
                    linear_regression = check_resource( \
                        linear_regression, api.get_linear_regression,
                        query_string=query_string,
                        raise_on_error=True)
                except Exception as exception:
                    sys.exit("Failed to get a finished linear regression:"
                             " %s" %
                             str(exception))
                linear_regressions[0] = linear_regression
            message = dated("linear regression created: %s\n" %
                            get_url(linear_regression))
            log_message(message, log_file=session_file,
                        console=args.verbosity)
            if args.reports:
                report(args.reports, path, linear_regression)

    return linear_regressions, linear_regression_ids


def get_linear_regressions(linear_regression_ids,
                           args, api=None, session_file=None):
    """Retrieves remote linear regression in its actual status

    """
    if api is None:
        api = bigml.api.BigML()

    linear_regression_id = ""
    linear_regressions = linear_regression_ids
    linear_regression_id = linear_regression_ids[0]
    message = dated("Retrieving %s. %s\n" %
                    (plural("linear regression", len(linear_regression_ids)),
                     get_url(linear_regression_id)))
    log_message(message, log_file=session_file, console=args.verbosity)
    # only one linear regression to predict at present
    try:
        # we need the whole fields structure when exporting fields
        query_string = FIELDS_QS if not args.export_fields else ALL_FIELDS_QS
        linear_regression = check_resource(linear_regression_ids[0],
                                           api.get_linear_regression,
                                           query_string=query_string,
                                           raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a finished linear regression: %s" % \
            str(exception))
    linear_regressions[0] = linear_regression

    return linear_regressions, linear_regression_ids


def set_publish_linear_regression_args(args):
    """Set args to publish linear regression

    """
    public_linear_regression = {}
    if args.public_linear_regression:
        public_linear_regression = {"private": False}
        if args.model_price:
            public_linear_regression.update(price=args.model_price)
        if args.cpp:
            public_linear_regression.update(credits_per_prediction=args.cpp)
    return public_linear_regression


def update_linear_regression(linear_regression, linear_regression_args,
                             args, api=None, path=None, session_file=None):
    """Updates linear regression properties

    """
    if api is None:
        api = bigml.api.BigML()

    message = dated("Updating linear regression. %s\n" %
                    get_url(linear_regression))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    linear_regression = api.update_linear_regression(linear_regression, \
        linear_regression_args)
    check_resource_error(linear_regression,
                         "Failed to update linear regression: %s"
                         % linear_regression['resource'])
    linear_regression = check_resource(linear_regression,
                                       api.get_linear_regression,
                                       query_string=FIELDS_QS,
                                       raise_on_error=True)
    if is_shared(linear_regression):
        message = dated("Shared linear regression link. %s\n" %
                        get_url(linear_regression, shared=True))
        log_message(message, log_file=session_file, console=args.verbosity)
        if args.reports:
            report(args.reports, path, linear_regression)

    return linear_regression
