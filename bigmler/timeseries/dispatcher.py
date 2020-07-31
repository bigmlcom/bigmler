# -*- coding: utf-8 -*-
#
# Copyright 2017-2020 BigML
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

"""BigMLer - cluster subcommand processing dispatching

"""


import sys
import os

import bigml.api
import bigmler.utils as u
import bigmler.resourcesapi.common as r
import bigmler.resourcesapi.time_series as rts
import bigmler.pre_model_steps as pms
import bigmler.processing.args as a
import bigmler.processing.timeseries as pts
import bigmler.processing.datasets as pd

from bigmler.resourcesapi.forecasts import set_forecast_args
from bigmler.defaults import DEFAULTS_FILE
from bigmler.forecast import forecast, remote_forecast
from bigmler.reports import clear_reports, upload_reports
from bigmler.command import get_context
from bigmler.tsevaluation import evaluate
from bigmler.dispatcher import SESSIONS_LOG, clear_log_files, \
    get_test_dataset, get_objective_id

COMMAND_LOG = ".bigmler_time_series"
DIRS_LOG = ".bigmler_time_series_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]
MINIMUM_MODEL = "full=false"
DEFAULT_OUTPUT = "forecast"

SETTINGS = {
    "command_log": COMMAND_LOG,
    "sessions_log": SESSIONS_LOG,
    "dirs_log": DIRS_LOG,
    "default_output": DEFAULT_OUTPUT,
    "defaults_file": DEFAULTS_FILE}


def time_series_dispatcher(args=sys.argv[1:]):
    """Parses command line and calls the different processing functions

    """

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        clear_log_files(LOG_FILES)

    command_args, _, api, session_file, resume = get_context(args, SETTINGS)

    # Selects the action to perform
    if (a.has_train(command_args) or a.has_ts_test(command_args)
            or command_args.export_fields):
        output_args = a.get_output_args(api, command_args, resume)
        compute_output(**output_args)
    u.log_message("_" * 80 + "\n", log_file=session_file)


def compute_output(api, args):
    """ Creates one or more models using the `training_set` or uses the ids
    of previously created BigML models to make predictions for the `test_set`.

    """

    time_series = None
    time_series_set = None

    # variables from command-line options
    resume = args.resume_
    time_series_ids = args.time_series_ids_
    output = args.predictions
    # there's only one time_series to be generated at present
    args.max_parallel_time_series = 1
    args.max_parallel_evaluations = 1
    # time_series cannot be published yet.
    args.public_time_series = False
    # no cross-validations
    args.dataset_off = False
    args.cross_validation_rate = 0
    args.number_of_evaluations = 1

    # It is compulsory to have a description to publish either datasets or
    # time_series
    if (not args.description_ and (args.public_time_series or
                                   args.public_dataset)):
        sys.exit("You should provide a description to publish.")

    # When using --new-fields, it is compulsory to specify also a dataset
    # id
    if args.new_fields and not args.dataset:
        sys.exit("To use --new-fields you must also provide a dataset id"
                 " to generate the new dataset from it.")

    path = u.check_dir(output)
    session_file = "%s%s%s" % (path, os.sep, SESSIONS_LOG)
    csv_properties = {}
    if args.objective_field:
        csv_properties.update({'objective_field': args.objective_field})
    # If logging is required set the file for logging
    log = None
    if args.log_file:
        u.check_dir(args.log_file)
        log = args.log_file
        # If --clear_logs the log files are cleared
        clear_log_files([log])

    # basic pre-model step: creating or retrieving the source related info
    source, resume, csv_properties, fields = pms.get_source_info(
        api, args, resume, csv_properties, session_file, path, log)
    # basic pre-model step: creating or retrieving the dataset related info
    dataset_properties = pms.get_dataset_info(
        api, args, resume, source,
        csv_properties, fields, session_file, path, log)
    (_, datasets, test_dataset,
     resume, csv_properties, fields) = dataset_properties
    if datasets:
        # Now we have a dataset, let's check if there's an objective_field
        # given by the user and update it in the fields structure
        args.objective_id_ = get_objective_id(args, fields)
        # if the time series is going to be evaluated, and we don't have
        # test data, we need to divide the rows using ranges, so we'll need
        # max rows
        args.max_rows = datasets[0]["object"]["rows"]
    if args.time_series_file:
        # time-series is retrieved from the contents of the given local
        # JSON file
        time_series, csv_properties, fields = u.read_local_resource(
            args.time_series_file,
            csv_properties=csv_properties)
        time_series_set = [time_series]
        time_series_ids = [time_series['resource']]
    else:
        # time-series is retrieved from the remote object
        time_series_set, time_series_ids, resume = \
            pts.time_series_processing( \
            datasets, time_series_set, time_series_ids, \
            api, args, resume, fields=fields, \
            session_file=session_file, path=path, log=log)
        if time_series_set:
            time_series = time_series_set[0]

    # We update the time-series' public state if needed
    if time_series:
        if isinstance(time_series, str):
            query_string = r.ALL_FIELDS_QS
            time_series = u.check_resource(time_series,
                                           api.get_time_series,
                                           query_string=query_string)
        time_series_set[0] = time_series
        if (args.public_time_series or
                (args.shared_flag and r.shared_changed(args.shared,
                                                       time_series))):
            time_series_args = {}
            if args.shared_flag and r.shared_changed(args.shared,
                                                     time_series):
                time_series_args.update(shared=args.shared)
            if args.public_time_series:
                time_series_args.update( \
                    rts.set_publish_time_series_args(args))
            if time_series_args:
                time_series = rts.update_time_series( \
                    time_series, time_series_args, args,
                    api=api, path=path, \
                    session_file=session_file)
                time_series_set[0] = time_series

    """
    # We get the fields of the time-series if we haven't got
    # them yet and need them
    if time_series and (args.test_set or args.export_fields):
        fields = pts.get_time_series_fields( \
            time_series, csv_properties, args)
    """

    if fields and args.export_fields:
        fields.summary_csv(os.path.join(path, args.export_fields))

    # If forecasting
    if time_series_set and a.has_ts_test(args):
        if args.remote:
            forecast_args = set_forecast_args(
                args, fields=fields)

            remote_forecast(time_series, forecast_args, args, \
                api, resume, \
                session_file=session_file, path=path, log=log)

        else:
            forecast(time_series, args,
                     session_file=session_file)

    # If evaluate flag is on, create remote evaluation and save results in
    # json and human-readable format.
    if args.evaluate:
        # When we resume evaluation and models were already completed, we
        # should use the datasets array as test datasets
        if args.has_test_datasets_:
            test_dataset = get_test_dataset(args)
        if args.dataset_off and not args.has_test_datasets_:
            args.test_dataset_ids = datasets
        if args.test_dataset_ids and args.dataset_off:
            # Evaluate the models with the corresponding test datasets.
            test_dataset_id = bigml.api.get_dataset_id( \
                args.test_dataset_ids[0])
            test_dataset = api.check_resource(test_dataset_id)
            csv_properties.update(objective_field=None,
                                  objective_field_present=False)
            test_fields = pd.get_fields_structure(test_dataset,
                                                  csv_properties)
            resume = evaluate(time_series_set, args.test_dataset_ids, api,
                              args, resume,
                              fields=fields, dataset_fields=test_fields,
                              session_file=session_file, path=path,
                              log=log,
                              objective_field=args.objective_field)
        else:
            dataset = datasets[0]
            if args.test_split > 0 or args.has_test_datasets_:
                dataset = test_dataset
            else:
                args.range_ = [int(args.max_rows * r.EVALUATE_SAMPLE_RATE),
                               args.max_rows]
            dataset = u.check_resource(dataset, api=api,
                                       query_string=r.ALL_FIELDS_QS)
            dataset_fields = pd.get_fields_structure(dataset, None)
            resume = evaluate(time_series_set, [dataset], api,
                              args, resume,
                              fields=fields, dataset_fields=dataset_fields,
                              session_file=session_file, path=path,
                              log=log)


    u.print_generated_files(path, log_file=session_file,
                            verbosity=args.verbosity)
    if args.reports:
        clear_reports(path)
        if args.upload:
            upload_reports(args.reports, path)
