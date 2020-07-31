# -*- coding: utf-8 -*-
#
# Copyright 2019-2020 BigML
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

"""BigMLer - Fusion subcommand processing dispatching

"""


import sys
import os

import bigml.api
import bigmler.utils as u
import bigmler.resourcesapi.common as r
import bigmler.resourcesapi.fusions as rfus
import bigmler.processing.args as a
import bigmler.processing.sources as ps
import bigmler.processing.datasets as pd
import bigmler.processing.fusion as pf

from bigmler.resourcesapi.datasets import set_basic_dataset_args
from bigmler.resourcesapi.batch_predictions import set_batch_prediction_args
from bigmler.defaults import DEFAULTS_FILE
from bigmler.sl_prediction import prediction, remote_prediction
from bigmler.reports import clear_reports, upload_reports
from bigmler.command import get_context
from bigmler.evaluation import evaluate
from bigmler.dispatcher import (SESSIONS_LOG,
                                clear_log_files, get_test_dataset)

COMMAND_LOG = ".bigmler_fusion"
DIRS_LOG = ".bigmler_fusion_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]
MINIMUM_MODEL = "full=false"
DEFAULT_OUTPUT = "predictions.csv"

SETTINGS = {
    "command_log": COMMAND_LOG,
    "sessions_log": SESSIONS_LOG,
    "dirs_log": DIRS_LOG,
    "default_output": DEFAULT_OUTPUT,
    "defaults_file": DEFAULTS_FILE}


def fusion_dispatcher(args=sys.argv[1:]):
    """Parses command line and calls the different processing functions

    """

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        clear_log_files(LOG_FILES)

    settings = {}
    settings.update(SETTINGS)
    if '--evaluate' in args:
        settings.update({"default_output": "evaluation"})

    command_args, _, api, session_file, _ = get_context(args, settings)

    # Selects the action to perform
    if a.has_value(command_args, "fusion_models_") or a.has_test(command_args):
        compute_output(api, command_args)
    u.log_message("_" * 80 + "\n", log_file=session_file)


def compute_output(api, args):
    """ Creates a fusion using the `models` list or uses the ids
    of a previously created BigML fusion to make predictions for the `test_set`.

    """

    fusion = None

    # variables from command-line options
    resume = args.resume_
    fusion_ids = args.fusion_ids_
    output = args.predictions
    # there's only one fusion to be generated at present
    args.max_parallel_fusions = 1
    # fusion cannot be published yet.
    args.public_fusion = False

    # It is compulsory to have a description to publish either datasets or
    # fusions
    if (not args.description_ and args.public_fusion):
        sys.exit("You should provide a description to publish.")

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

    if args.fusion_file:
        # fusion regression is retrieved from the contents of the given local
        # JSON file
        fusion, csv_properties, fields = u.read_local_resource(
            args.fusion_file,
            csv_properties=csv_properties)
        fusion_ids = [fusion]
    else:
        # fusion is retrieved from the remote object or created
        fusion, resume = \
            pf.fusion_processing( \
            fusion, fusion_ids, \
            api, args, resume, \
            session_file=session_file, path=path, log=log)

    # We update the fusion public state if needed
    if fusion:
        if isinstance(fusion, str):
            if not a.has_test(args):
                query_string = MINIMUM_MODEL
            elif args.export_fields:
                query_string = r.ALL_FIELDS_QS
            else:
                query_string = ''
            fusion = u.check_resource(fusion,
                                      api.get_fusion,
                                      query_string=query_string)
        if (args.public_fusion or
                (args.shared_flag and r.shared_changed(args.shared,
                                                       fusion))):
            fusion_args = {}
            if args.shared_flag and r.shared_changed(args.shared,
                                                     fusion):
                fusion_args.update(shared=args.shared)
            if args.public_fusion:
                fusion_args.update( \
                    rfus.set_publish_fusion_args(args))
            if fusion_args:
                fusion = rfus.update_fusion( \
                    fusion, fusion_args, args,
                    api=api, path=path, \
                    session_file=session_file)

    # We get the fields of the fusion if we haven't got
    # them yet and need them
    if fusion and (args.test_set or args.evaluate):
        fields = pf.get_fusion_fields( \
            fusion, csv_properties, args)


    # If predicting
    if fusion and (a.has_test(args) or \
            args.remote):
        test_dataset = get_test_dataset(args)

        # Remote predictions: predictions are computed as batch predictions
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

            csv_properties.update(objective_field=None,
                                  objective_field_present=False)
            test_fields = pd.get_fields_structure(test_dataset,
                                                  csv_properties)
            if not args.evaluate:
                batch_prediction_args = set_batch_prediction_args(
                    args, fields=fields,
                    dataset_fields=test_fields)

                remote_prediction(fusion, test_dataset, \
                    batch_prediction_args, args, \
                    api, resume, prediction_file=output, \
                    session_file=session_file, path=path, log=log)

        else:
            prediction([fusion], fields, args,
                       session_file=session_file)


    # If evaluate flag is on, create remote evaluation and save results in
    # json and human-readable format.
    if args.evaluate:
        # When we resume evaluation and models were already completed, we
        # should use the datasets array as test datasets
        args.max_parallel_evaluations = 1 # only one evaluation at present
        args.cross_validation_rate = 0 # no cross-validation
        args.number_of_evaluations = 1 # only one evaluation
        if args.has_test_datasets_:
            test_dataset = get_test_dataset(args)
            dataset = test_dataset
            dataset = u.check_resource(dataset, api=api,
                                       query_string=r.ALL_FIELDS_QS)
            dataset_fields = pd.get_fields_structure(dataset, None)
            resume = evaluate([fusion], [dataset], api,
                              args, resume,
                              fields=fields, dataset_fields=dataset_fields,
                              session_file=session_file, path=path,
                              log=log,
                              objective_field=args.objective_field)


    u.print_generated_files(path, log_file=session_file,
                            verbosity=args.verbosity)
    if args.reports:
        clear_reports(path)
        if args.upload:
            upload_reports(args.reports, path)
