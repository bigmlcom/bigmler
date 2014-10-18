# -*- coding: utf-8 -*-
#
# Copyright 2014 BigML
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
from __future__ import absolute_import

import sys
import os

import bigml.api
import bigmler.utils as u
import bigmler.resources as r
import bigmler.processing.args as a
import bigmler.processing.sources as ps
import bigmler.processing.datasets as pd
import bigmler.processing.anomalies as pa

from bigmler.defaults import DEFAULTS_FILE
#from bigmler.centroid import centroid, remote_centroid
from bigmler.anomaly_score import anomaly_score, remote_anomaly_score
from bigmler.reports import clear_reports, upload_reports
from bigmler.command import Command, StoredCommand
from bigmler.dispatcher import (SESSIONS_LOG, command_handling,
                                clear_log_files,
                                has_test, has_train)

COMMAND_LOG = u".bigmler_anomaly"
DIRS_LOG = u".bigmler_anomaly_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]
MINIMUM_MODEL = "full=false"
DEFAULT_OUTPUT = u"anomaly_scores.csv"


def anomaly_dispatcher(args=sys.argv[1:]):
    """Parses command line and calls the different processing functions

    """

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        clear_log_files(LOG_FILES)

    command = command_handling(args, COMMAND_LOG)

    # Parses command line arguments.
    command_args = a.parse_and_check(command)
    resume = command_args.resume
    if command_args.resume:
        # Keep the debug option if set
        debug = command_args.debug
        # Restore the args of the call to resume from the command log file
        stored_command = StoredCommand(args, COMMAND_LOG, DIRS_LOG)
        command = Command(None, stored_command=stored_command)
        # Logs the issued command and the resumed command
        session_file = os.path.join(stored_command.output_dir, SESSIONS_LOG)
        stored_command.log_command(session_file=session_file)
        # Parses resumed arguments.
        command_args = a.parse_and_check(command)
        if command_args.predictions is None:
            command_args.predictions = os.path.join(stored_command.output_dir,
                                                    DEFAULT_OUTPUT)
    else:
        if command_args.output_dir is None:
            command_args.output_dir = a.NOW
        if command_args.predictions is None:
            command_args.predictions = os.path.join(command_args.output_dir,
                                                    DEFAULT_OUTPUT)
        if len(os.path.dirname(command_args.predictions).strip()) == 0:
            command_args.predictions = os.path.join(command_args.output_dir,
                                                    command_args.predictions)
        directory = u.check_dir(command_args.predictions)
        session_file = os.path.join(directory, SESSIONS_LOG)
        u.log_message(command.command + "\n", log_file=session_file)
        try:
            defaults_file = open(DEFAULTS_FILE, 'r')
            contents = defaults_file.read()
            defaults_file.close()
            defaults_copy = open(os.path.join(directory, DEFAULTS_FILE),
                                 'w', 0)
            defaults_copy.write(contents)
            defaults_copy.close()
        except IOError:
            pass
        u.sys_log_message(u"%s\n" % os.path.abspath(directory),
                          log_file=DIRS_LOG)

    # Creates the corresponding api instance
    if resume and debug:
        command_args.debug = True
    api = a.get_api_instance(command_args, u.check_dir(session_file))

    # Selects the action to perform
    if (has_train(command_args) or has_test(command_args)):
        output_args = a.get_output_args(api, command_args, resume)
        a.transform_args(command_args, command.flags, api,
                         command.user_defaults)
        compute_output(**output_args)
    u.log_message("_" * 80 + "\n", log_file=session_file)


def compute_output(api, args):
    """ Creates one or more models using the `training_set` or uses the ids
    of previously created BigML models to make predictions for the `test_set`.

    """
    source = None
    dataset = None
    anomaly = None
    anomalies = None
    fields = None
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
    session_file = u"%s%s%s" % (path, os.sep, SESSIONS_LOG)
    csv_properties = {}
    # If logging is required set the file for logging
    log = None
    if args.log_file:
        u.check_dir(args.log_file)
        log = args.log_file
        # If --clear_logs the log files are cleared
        clear_log_files([log])

    source, resume, csv_properties, fields = ps.source_processing(
        api, args, resume,
        csv_properties=csv_properties,
        session_file=session_file, path=path, log=log)

    datasets, resume, csv_properties, fields = pd.dataset_processing(
        source, api, args, resume,
        fields=fields,
        csv_properties=csv_properties,
        session_file=session_file, path=path, log=log)
    if datasets:
        dataset = datasets[0]
        if args.to_csv is not None:
            resume = pd.export_dataset(dataset, api, args, resume,
                                       session_file=session_file, path=path)

    # If test_split is used, split the dataset in a training and a test dataset
    # according to the given split
    if args.test_split > 0:
        dataset, test_dataset, resume = pd.split_processing(
            dataset, api, args, resume,
            session_file=session_file, path=path, log=log)
        datasets[0] = dataset

    # If multi-dataset flag is on, generate a new dataset from the given
    # list of datasets
    if args.multi_dataset:
        dataset, resume = pd.create_new_dataset(
            datasets, api, args, resume, fields=fields,
            session_file=session_file, path=path, log=log)
        datasets = [dataset]

    # Check if the dataset has a generators file associated with it, and
    # generate a new dataset with the specified field structure
    if args.new_fields:
        dataset, resume = pd.create_new_dataset(
            dataset, api, args, resume, fields=fields,
            session_file=session_file, path=path, log=log)
        datasets[0] = dataset

    anomalies, anomaly_ids, resume = pa.anomalies_processing(
        datasets, anomalies, anomaly_ids, api, args, resume, fields=fields,
        session_file=session_file, path=path, log=log)
    if anomalies:
        anomaly = anomalies[0]

    # We update the anomaly's public state if needed
    if anomaly:
        if isinstance(anomaly, basestring):
            if not has_test(args):
                query_string = MINIMUM_MODEL
            else:
                query_string = ''
            anomaly = u.check_resource(anomaly, query_string=query_string,
                                       api=api)
        anomalies[0] = anomaly
        if (args.public_anomaly or
                (args.shared_flag and r.shared_changed(args.shared, anomaly))):
            anomaly_args = {}
            if args.shared_flag and r.shared_changed(args.shared, anomaly):
                anomaly_args.update(shared=args.shared)
            if args.public_anomaly:
                anomaly_args.update(r.set_publish_anomaly_args(args))
            if anomaly_args:
                anomaly = r.update_anomaly(anomaly, anomaly_args, args,
                                           api=api, path=path,
                                           session_file=session_file)
                anomalies[0] = anomaly

    # We get the fields of the anomaly detector if we haven't got
    # them yet and need them
    if anomaly and args.test_set:
        fields = pa.get_anomaly_fields(anomaly, csv_properties, args)

    # If predicting
    if anomalies and has_test(args):
        test_dataset = None

        # Remote anomaly scores: scores are computed as batch anomaly scores
        # in bigml.com except when --no-batch flag is set on
        if args.remote and not args.no_batch:
            # create test source from file
            test_name = "%s - test" % args.name
            if args.test_source is None:
                (test_source,
                 resume,
                 csv_properties,
                 test_fields) = ps.test_source_processing(
                    api, args, resume, name=test_name,
                    session_file=session_file, path=path, log=log)
            else:
                test_source_id = bigml.api.get_source_id(args.test_source)
                test_source = api.check_resource(test_source_id,
                                                 api.get_source)
            if args.test_dataset is None:
                # create test dataset from test source
                dataset_args = r.set_basic_dataset_args(args, name=test_name)
                test_dataset, resume = pd.alternative_dataset_processing(
                    test_source, "test", dataset_args, api, args,
                    resume, session_file=session_file, path=path, log=log)
            else:
                test_dataset_id = bigml.api.get_dataset_id(args.test_dataset)
                test_dataset = api.check_resource(test_dataset_id,
                                                  api.get_dataset)
            test_fields = pd.get_fields_structure(test_dataset,
                                                  csv_properties)
            batch_anomaly_score_args = r.set_batch_anomaly_score_args(
                args, fields=fields,
                dataset_fields=test_fields)

            remote_anomaly_score(anomaly, test_dataset,
                                 batch_anomaly_score_args, args,
                                 api, resume, prediction_file=output,
                                 session_file=session_file, path=path, log=log)

        else:
            anomaly_score(anomalies, fields, args, session_file=session_file)

    u.print_generated_files(path, log_file=session_file,
                            verbosity=args.verbosity)
    if args.reports:
        clear_reports(path)
        if args.upload:
            upload_reports(args.reports, path)
