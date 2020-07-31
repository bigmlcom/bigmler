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
    update_json_args, wait_for_available_tasks

from bigmler.resourcesapi.common import FIELDS_QS, EVALUATE_SAMPLE_RATE, \
    ALL_FIELDS_QS


def set_time_series_args(args, name=None, fields=None,
                         objective_id=None):
    """Return time-series arguments dict

    """
    if name is None:
        name = args.name
    if objective_id is None:
        objective_id = args.objective_id_

    time_series_args = set_basic_model_args(args, name)
    time_series_args.update({
        "all_numeric_objectives": args.all_numeric_objectives,
        "period": args.period
    })

    # if we need to evaluate and there's no previous split, use a range
    if args.evaluate and args.test_split == 0 and not args.has_test_datasets_:
        args.range_ = [1, int(args.max_rows * EVALUATE_SAMPLE_RATE)]
    if objective_id is not None:
        time_series_args.update({"objective_field": objective_id})
    if args.objectives:
        time_series_args.update({"objective_fields": args.objective_fields_})
    if args.damped_trend is not None:
        time_series_args.update({"damped_trend": args.damped_trend})
    if args.error is not None:
        time_series_args.update({"error": args.error})
    if args.field_parameters:
        time_series_args.update({"field_parameters": args.field_parameters_})
    if args.range_:
        time_series_args.update({"range": args.range_})
    if args.seasonality is not None:
        time_series_args.update({"seasonality": args.seasonality})
    if args.trend is not None:
        time_series_args.update({"trend": args.trend})

    if args.time_start or args.time_end or args.time_interval or \
            args.time_interval_unit:
        time_range = {}
        if args.time_start:
            time_range.update({"start": args.time_start})
        if args.time_end:
            time_range.update({"end": args.time_end})
        if args.time_interval:
            time_range.update({"interval": args.time_interval})
        if args.time_interval_unit:
            time_range.update({"interval_unit": args.time_interval_unit})
        time_series_args.update({"time_range": time_range})

    if 'time_series' in args.json_args:
        update_json_args(time_series_args,
                         args.json_args.get('time_series'),
                         fields)
    return time_series_args


def create_time_series(datasets, time_series_ids,
                       time_series_args,
                       args, api=None, path=None,
                       session_file=None, log=None):
    """Create remote time-series

    """
    if api is None:
        api = bigml.api.BigML()

    time_series_set = time_series_ids[:]
    existing_time_series = len(time_series_set)
    time_series_args_list = []
    datasets = datasets[existing_time_series:]
    # if resuming and all time-series were created,
    # there will be no datasets left
    if datasets:
        if isinstance(time_series_args, list):
            time_series_args_list = time_series_args

        # Only one time-series per command, at present
        number_of_time_series = 1
        message = dated("Creating %s time-series.\n" %
                        number_of_time_series)
        log_message(message, log_file=session_file,
                    console=args.verbosity)

        query_string = FIELDS_QS
        inprogress = []
        for i in range(0, number_of_time_series):
            wait_for_available_tasks(inprogress,
                                     args.max_parallel_time_series,
                                     api, "timeseries")
            if time_series_args_list:
                time_series_args = time_series_args_list[i]

            if (args.test_datasets and args.evaluate):
                dataset = datasets[i]
                time_series = api.create_time_series( \
                    dataset, time_series_args, retries=None)
            else:
                time_series = api.create_time_series( \
                datasets, time_series_args, retries=None)
            time_series_id = check_resource_error( \
                time_series, "Failed to create time-series: ")
            log_message("%s\n" % time_series_id, log_file=log)
            time_series_ids.append(time_series_id)
            inprogress.append(time_series_id)
            time_series_set.append(time_series)
            log_created_resources("time_series",
                                  path,
                                  time_series_id, mode='a')

        if args.verbosity:
            if bigml.api.get_status(time_series)['code'] != \
                    bigml.api.FINISHED:
                try:
                    time_series = check_resource( \
                        time_series, api.get_time_series,
                        query_string=query_string,
                        raise_on_error=True)
                except Exception as exception:
                    sys.exit("Failed to get a finished time-series:"
                             " %s" %
                             str(exception))
                time_series_set[0] = time_series
            message = dated("Time-series created: %s\n" %
                            get_url(time_series))
            log_message(message, log_file=session_file,
                        console=args.verbosity)
            if args.reports:
                report(args.reports, path, time_series)

    return time_series_set, time_series_ids


def get_time_series(time_series_ids,
                    args, api=None, session_file=None):
    """Retrieves remote time-series in its actual status

    """
    if api is None:
        api = bigml.api.BigML()

    time_series_id = ""
    time_series_set = time_series_ids
    time_series_id = time_series_ids[0]
    message = dated("Retrieving %s. %s\n" %
                    (plural("time-series", len(time_series_ids)),
                     get_url(time_series_id)))
    log_message(message, log_file=session_file, console=args.verbosity)
    # only one time-series to predict at present
    try:
        # we need the whole fields structure when exporting fields
        query_string = FIELDS_QS if not args.export_fields else ALL_FIELDS_QS
        time_series = check_resource(time_series_ids[0],
                                     api.get_time_series,
                                     query_string=query_string,
                                     raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a finished time-series: %s" % \
            str(exception))
    time_series_set[0] = time_series

    return time_series_set, time_series_ids


def set_publish_time_series_args(args):
    """Set args to publish time-series

    """
    public_time_series = {}
    if args.public_time_series:
        public_time_series = {"private": False}
        if args.model_price:
            public_time_series.update(price=args.model_price)
        if args.cpp:
            public_time_series.update(credits_per_prediction=args.cpp)
    return public_time_series


def update_time_series(time_series, time_series_args,
                       args, api=None, path=None, session_file=None):
    """Updates time-series properties

    """
    if api is None:
        api = bigml.api.BigML()

    message = dated("Updating time-series. %s\n" %
                    get_url(time_series))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    time_series = api.update_time_series(time_series, \
        time_series_args)
    check_resource_error(time_series,
                         "Failed to update time-series: %s"
                         % time_series['resource'])
    time_series = check_resource(time_series,
                                 api.get_time_series,
                                 query_string=FIELDS_QS,
                                 raise_on_error=True)
    if is_shared(time_series):
        message = dated("Shared time-series link. %s\n" %
                        get_url(time_series, shared=True))
        log_message(message, log_file=session_file, console=args.verbosity)
        if args.reports:
            report(args.reports, path, time_series)

    return time_series
