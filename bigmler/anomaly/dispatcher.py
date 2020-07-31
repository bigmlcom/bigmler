# -*- coding: utf-8 -*-
#
# Copyright 2014-2020 BigML
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

"""BigMLer - anomaly subcommand processing dispatching

"""


import sys
import os

import bigml.api

from bigml.anomaly import Anomaly

import bigmler.utils as u
import bigmler.resourcesapi.common as r
import bigmler.resourcesapi.anomalies as ra
import bigmler.pre_model_steps as pms
import bigmler.processing.args as a
import bigmler.processing.anomalies as pa
import bigmler.processing.sources as ps
import bigmler.processing.datasets as pd

from bigmler.resourcesapi.datasets import set_basic_dataset_args
from bigmler.resourcesapi.batch_anomaly_scores import \
    set_batch_anomaly_score_args
from bigmler.defaults import DEFAULTS_FILE
from bigmler.anomaly_score import anomaly_score, remote_anomaly_score
from bigmler.reports import clear_reports, upload_reports
from bigmler.command import get_context
from bigmler.dispatcher import SESSIONS_LOG, clear_log_files, get_test_dataset
from bigmler.options.anomaly import ANOMALIES_IN

COMMAND_LOG = ".bigmler_anomaly"
DIRS_LOG = ".bigmler_anomaly_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]
MINIMUM_MODEL = "full=false"
EXCLUDE_TREES = "exclude=trees"
DEFAULT_OUTPUT = "anomaly_scores.csv"

SETTINGS = {
    "command_log": COMMAND_LOG,
    "sessions_log": SESSIONS_LOG,
    "dirs_log": DIRS_LOG,
    "default_output": DEFAULT_OUTPUT,
    "defaults_file": DEFAULTS_FILE}


def anomaly_dispatcher(args=sys.argv[1:]):
    """Parses command line and calls the different processing functions

    """

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        clear_log_files(LOG_FILES)

    command_args, _, api, session_file, resume = get_context(args,
                                                             SETTINGS)
    # Selects the action to perform
    if (a.has_train(command_args) or a.has_test(command_args) or
            command_args.score or
            a.has_anomaly(command_args)):
        output_args = a.get_output_args(api, command_args, resume)
        compute_output(**output_args)
    u.log_message("_" * 80 + "\n", log_file=session_file)


def compute_output(api, args):
    """ Creates one or more anomaly detectors using the `training_set`
        or uses the ids of previously created BigML models to make
        predictions for the `test_set`.

    """

    anomaly = None
    anomalies = None
    # no multi-label support at present

    # variables from command-line options
    resume = args.resume_
    anomaly_ids = args.anomaly_ids_
    output = args.predictions
    # there's only one anomaly detector to be generated at present
    args.max_parallel_anomalies = 1
    # anomalies cannot be published yet.
    args.public_anomaly = False

    # It is compulsory to have a description to publish either datasets or
    # anomalies
    if (not args.description_ and (args.public_anomaly or
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
    (_, datasets, test_dataset, resume,
     csv_properties, fields) = dataset_properties
    if args.anomaly_file:
        # anomaly is retrieved from the contents of the given local JSON file
        anomaly, csv_properties, fields = u.read_local_resource(
            args.anomaly_file,
            csv_properties=csv_properties)
        anomalies = [anomaly]
        anomaly_ids = [anomaly['resource']]
    else:
        # anomaly is retrieved from the remote object
        anomalies, anomaly_ids, resume = pa.anomalies_processing(
            datasets, anomalies, anomaly_ids, api, args, resume, fields=fields,
            session_file=session_file, path=path, log=log)
    if anomalies:
        anomaly = anomalies[0]

    # We update the anomaly's public state if needed
    if anomaly:
        if not a.has_test(args) and not args.anomalies_dataset:
            query_string = MINIMUM_MODEL
        elif not a.has_test(args):
            query_string = ";".join([EXCLUDE_TREES, r.ALL_FIELDS_QS])
        else:
            query_string = r.ALL_FIELDS_QS
        try:
            anomaly_id = anomaly.get('resource', anomaly)
        except AttributeError:
            anomaly_id = anomaly
        anomaly = u.check_resource(anomaly_id,
                                   query_string=query_string,
                                   api=api)
        anomalies[0] = anomaly
        if (args.public_anomaly or
                (args.shared_flag and r.shared_changed(args.shared, anomaly))):
            anomaly_args = {}
            if args.shared_flag and r.shared_changed(args.shared, anomaly):
                anomaly_args.update(shared=args.shared)
            if args.public_anomaly:
                anomaly_args.update(ra.set_publish_anomaly_args(args))
            if anomaly_args:
                anomaly = ra.update_anomaly(anomaly, anomaly_args, args,
                                            api=api, path=path,
                                            session_file=session_file)
                anomalies[0] = anomaly

    # We get the fields of the anomaly detector if we haven't got
    # them yet and need them
    if anomaly and (args.test_set or args.export_fields):
        fields = pa.get_anomaly_fields(anomaly, csv_properties, args)

    # If creating a top anomalies excluded/included dataset
    if args.anomalies_dataset and anomaly:
        origin_dataset = anomaly['object'].get('dataset')
        if origin_dataset is None:
            sys.exit("The dataset used to generate the anomaly detector "
                     "cannot be found. Failed to generate the anomalies "
                     " dataset.")
        local_anomaly = Anomaly(anomaly)
        include = args.anomalies_dataset == ANOMALIES_IN
        args.anomaly_filter_ = local_anomaly.anomalies_filter(include=include)
        _, resume = pd.create_new_dataset(
            origin_dataset, api, args, resume, fields=fields,
            session_file=session_file, path=path, log=log)
    # If predicting
    if anomaly and args.score:
        args.test_dataset = anomaly['object']['dataset']
    if anomalies and (a.has_test(args) or (test_dataset and args.remote)):
        # test dataset can be defined by --test-split or --test-dataset or
        # --test-datasets
        if test_dataset is None:
            test_dataset = get_test_dataset(args)
        # Remote anomaly scores: scores are computed as batch anomaly scores
        # in bigml.com except when --no-batch flag is set on
        if args.remote and not args.no_batch:
            # create test source from file
            test_name = "%s - test" % args.name
            if args.test_source is None:
                test_properties = ps.test_source_processing(
                    api, args, resume, name=test_name,
                    session_file=session_file, path=path, log=log)
                (test_source, resume,
                 csv_properties, test_fields) = test_properties
            else:
                test_source_id = bigml.api.get_source_id(args.test_source)
                test_source = api.check_resource(test_source_id)
            if test_dataset is None:
                # create test dataset from test source
                dataset_args = set_basic_dataset_args(args, name=test_name)
                test_dataset, resume = pd.alternative_dataset_processing(
                    test_source, "test", dataset_args, api, args,
                    resume, session_file=session_file, path=path, log=log)
            else:
                test_dataset_id = bigml.api.get_dataset_id(test_dataset)
                test_dataset = api.check_resource(test_dataset_id)
            test_fields = pd.get_fields_structure(test_dataset,
                                                  csv_properties)
            batch_anomaly_score_args = set_batch_anomaly_score_args(
                args, fields=fields,
                dataset_fields=test_fields)

            remote_anomaly_score(anomaly, test_dataset,
                                 batch_anomaly_score_args, args,
                                 api, resume, prediction_file=output,
                                 session_file=session_file, path=path, log=log)

        else:
            anomaly_score(anomalies, fields, args, session_file=session_file)

    if fields and args.export_fields:
        fields.summary_csv(os.path.join(path, args.export_fields))

    u.print_generated_files(path, log_file=session_file,
                            verbosity=args.verbosity)
    if args.reports:
        clear_reports(path)
        if args.upload:
            upload_reports(args.reports, path)
