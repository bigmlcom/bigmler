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


def set_logistic_regression_args(args, name=None, fields=None,
                                 objective_id=None,
                                 logistic_regression_fields=None):
    """Return logistic regression arguments dict

    """
    if name is None:
        name = args.name
    if logistic_regression_fields is None:
        logistic_regression_fields = args.logistic_regression_fields_
    if objective_id is None:
        objective_id = args.objective_id_

    logistic_regression_args = set_basic_model_args(args, name)
    logistic_regression_args.update({
        "seed": SEED if args.seed is None else args.seed
    })

    if objective_id is not None and fields is not None:
        logistic_regression_args.update({"objective_field": objective_id})
    if logistic_regression_fields and fields is not None:
        input_fields = configure_input_fields(fields,
                                              logistic_regression_fields)
        logistic_regression_args.update(input_fields=input_fields)
    if ((args.evaluate and args.test_split == 0 and args.test_datasets is None)
            or args.cross_validation_rate > 0):
        logistic_regression_args.update(seed=SEED)
        if args.cross_validation_rate > 0:
            args.sample_rate = 1 - args.cross_validation_rate
            args.replacement = False
        elif (args.sample_rate == 1 and args.test_datasets is None
              and not args.dataset_off):
            args.sample_rate = EVALUATE_SAMPLE_RATE
    logistic_regression_args.update({"sample_rate": args.sample_rate})
    if args.lr_c:
        logistic_regression_args.update({"c": args.lr_c})
    logistic_regression_args.update({"bias": args.bias})
    logistic_regression_args.update( \
        {"balance_fields": args.balance_fields})
    if args.eps:
        logistic_regression_args.update({"eps": args.eps})
    if args.normalize is not None:
        logistic_regression_args.update({"normalize": args.normalize})
    if args.missing_numerics is not None:
        logistic_regression_args.update( \
            {"missing_numerics": args.missing_numerics})
    if args.field_codings is not None:
        logistic_regression_args.update(\
            {"field_codings": args.field_codings_})

    logistic_regression_args = update_sample_parameters_args( \
        logistic_regression_args, args)

    if 'logistic_regression' in args.json_args:
        update_json_args(logistic_regression_args,
                         args.json_args.get('logistic_regression'),
                         fields)
    return logistic_regression_args


def create_logistic_regressions(datasets, logistic_regression_ids,
                                logistic_regression_args,
                                args, api=None, path=None,
                                session_file=None, log=None):
    """Create remote logistic regressions

    """
    if api is None:
        api = bigml.api.BigML()

    logistic_regressions = logistic_regression_ids[:]
    existing_logistic_regressions = len(logistic_regressions)
    logistic_regression_args_list = []
    datasets = datasets[existing_logistic_regressions:]
    # if resuming and all logistic regressions were created,
    # there will be no datasets left
    if datasets:
        if isinstance(logistic_regression_args, list):
            logistic_regression_args_list = logistic_regression_args

        # Only one logistic regression per command, at present
        number_of_logistic_regressions = 1
        message = dated("Creating %s.\n" %
                        plural("logistic regression",
                               number_of_logistic_regressions))
        log_message(message, log_file=session_file,
                    console=args.verbosity)

        query_string = FIELDS_QS
        inprogress = []
        for i in range(0, number_of_logistic_regressions):
            wait_for_available_tasks(inprogress,
                                     args.max_parallel_logistic_regressions,
                                     api, "logisticregression")
            if logistic_regression_args_list:
                logistic_regression_args = logistic_regression_args_list[i]
            if args.cross_validation_rate > 0:
                new_seed = get_basic_seed(i + existing_logistic_regressions)
                logistic_regression_args.update(seed=new_seed)

            if (args.test_datasets and args.evaluate):
                dataset = datasets[i]
                logistic_regression = api.create_logistic_regression( \
                    dataset, logistic_regression_args, retries=None)
            elif args.dataset_off and args.evaluate:
                multi_dataset = args.test_dataset_ids[:]
                del multi_dataset[i + existing_logistic_regressions]
                logistic_regression = api.create_logistic_regression( \
                    multi_dataset, logistic_regression_args, retries=None)
            else:
                logistic_regression = api.create_logistic_regression( \
                datasets, logistic_regression_args, retries=None)
            logistic_regression_id = check_resource_error( \
                logistic_regression, "Failed to create logistic regression: ")
            log_message("%s\n" % logistic_regression_id, log_file=log)
            logistic_regression_ids.append(logistic_regression_id)
            inprogress.append(logistic_regression_id)
            logistic_regressions.append(logistic_regression)
            log_created_resources("logistic_regressions",
                                  path,
                                  logistic_regression_id, mode='a')

        if args.verbosity:
            if bigml.api.get_status(logistic_regression)['code'] != \
                    bigml.api.FINISHED:
                try:
                    logistic_regression = check_resource( \
                        logistic_regression, api.get_logistic_regression,
                        query_string=query_string, raise_on_error=True)
                except Exception as exception:
                    sys.exit("Failed to get a finished logistic regression:"
                             " %s" %
                             str(exception))
                logistic_regressions[0] = logistic_regression
            message = dated("Logistic regression created: %s\n" %
                            get_url(logistic_regression))
            log_message(message, log_file=session_file,
                        console=args.verbosity)
            if args.reports:
                report(args.reports, path, logistic_regression)

    return logistic_regressions, logistic_regression_ids


def get_logistic_regressions(logistic_regression_ids,
                             args, api=None, session_file=None):
    """Retrieves remote logistic regression in its actual status

    """
    if api is None:
        api = bigml.api.BigML()

    logistic_regression_id = ""
    logistic_regressions = logistic_regression_ids
    logistic_regression_id = logistic_regression_ids[0]
    message = dated("Retrieving %s. %s\n" %
                    (plural("logistic regression", len(logistic_regression_ids)),
                     get_url(logistic_regression_id)))
    log_message(message, log_file=session_file, console=args.verbosity)
    # only one logistic regression to predict at present
    try:
        # we need the whole fields structure when exporting fields
        query_string = FIELDS_QS if not args.export_fields else ALL_FIELDS_QS
        logistic_regression = check_resource(logistic_regression_ids[0],
                                             api.get_logistic_regression,
                                             query_string=query_string,
                                             raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a finished logistic regression: %s" % \
            str(exception))
    logistic_regressions[0] = logistic_regression

    return logistic_regressions, logistic_regression_ids


def set_publish_logistic_regression_args(args):
    """Set args to publish logistic regression

    """
    public_logistic_regression = {}
    if args.public_logistic_regression:
        public_logistic_regression = {"private": False}
        if args.model_price:
            public_logistic_regression.update(price=args.model_price)
        if args.cpp:
            public_logistic_regression.update(credits_per_prediction=args.cpp)
    return public_logistic_regression


def update_logistic_regression(logistic_regression, logistic_regression_args,
                               args, api=None, path=None, session_file=None):
    """Updates logistic regression properties

    """
    if api is None:
        api = bigml.api.BigML()

    message = dated("Updating logistic regression. %s\n" %
                    get_url(logistic_regression))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    logistic_regression = api.update_logistic_regression(logistic_regression, \
        logistic_regression_args)
    check_resource_error(logistic_regression,
                         "Failed to update logistic regression: %s"
                         % logistic_regression['resource'])
    logistic_regression = check_resource(logistic_regression,
                                         api.get_logistic_regression,
                                         query_string=FIELDS_QS,
                                         raise_on_error=True)
    if is_shared(logistic_regression):
        message = dated("Shared logistic regression link. %s\n" %
                        get_url(logistic_regression, shared=True))
        log_message(message, log_file=session_file, console=args.verbosity)
        if args.reports:
            report(args.reports, path, logistic_regression)

    return logistic_regression
