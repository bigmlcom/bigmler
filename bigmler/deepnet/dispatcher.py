# -*- coding: utf-8 -*-
#
# Copyright 2014-2025 BigML
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

"""BigMLer - deepnet subcommand processing dispatching

"""


import sys
import os

import bigml.api
import bigmler.utils as u
import bigmler.resourcesapi.common as r
import bigmler.pre_model_steps as pms
import bigmler.processing.args as a
import bigmler.processing.deepnets as pdn
import bigmler.processing.sources as ps
import bigmler.processing.datasets as pd

from bigmler.resourcesapi.datasets import set_basic_dataset_args
from bigmler.resourcesapi.models import set_publish_model_args
from bigmler.resourcesapi.deepnets import update_deepnet
from bigmler.resourcesapi.batch_predictions import set_batch_prediction_args
from bigmler.defaults import DEFAULTS_FILE
from bigmler.dnprediction import dn_prediction, remote_dn_prediction
from bigmler.reports import clear_reports, upload_reports
from bigmler.command import get_context
from bigmler.evaluation import evaluate
from bigmler.dispatcher import SESSIONS_LOG, clear_log_files, \
    get_test_dataset, get_objective_id

COMMAND_LOG = ".bigmler_deepnet"
DIRS_LOG = ".bigmler_deepnet_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]
MINIMUM_MODEL = "full=false"
DEFAULT_OUTPUT = "predictions.csv"

SETTINGS = {
    "command_log": COMMAND_LOG,
    "sessions_log": SESSIONS_LOG,
    "dirs_log": DIRS_LOG,
    "default_output": DEFAULT_OUTPUT,
    "defaults_file": DEFAULTS_FILE}


#pylint: disable=locally-disabled,dangerous-default-value
def deepnet_dispatcher(args=sys.argv[1:]):
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
    if (a.has_train(command_args) or a.has_test(command_args)
            or command_args.export_fields):
        compute_output(api, command_args)
    u.log_message("_" * 80 + "\n", log_file=session_file)


def compute_output(api, args):
    """ Creates one or more models using the `training_set` or uses the ids
    of previously created BigML models to make predictions for the `test_set`.

    """

    deepnet = None
    deepnets = None

    # variables from command-line options
    resume = args.resume_
    deepnet_ids = args.deepnet_ids_
    output = args.predictions
    # there's only one deepnet to be generated at present
    args.max_parallel_deepnets = 1
    # deepnets cannot be published yet.
    args.public_deepnet = False

    # It is compulsory to have a description to publish either datasets or
    # deepnet
    if (not args.description_ and (args.public_deepnet or
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
    if args.deepnet_file:
        # deepnet is retrieved from the contents of the given local
        # JSON file
        deepnet, csv_properties, fields = u.read_local_resource(
            args.deepnet_file,
            csv_properties=csv_properties)
        deepnets = [deepnet]
        deepnet_ids = [deepnet['resource']]
    else:
        # deepnet is retrieved from the remote object
        deepnets, deepnet_ids, resume = \
            pdn.deepnets_processing( \
            datasets, deepnets, deepnet_ids, \
            api, args, resume, fields=fields, \
            session_file=session_file, path=path, log=log)
        if deepnets:
            deepnet = deepnets[0]

    # We update the deepnet's public state if needed
    if deepnet:
        if isinstance(deepnet, str) or \
                api.status(deepnet) != bigml.api.FINISHED:
            if not a.has_test(args):
                query_string = MINIMUM_MODEL
            elif args.export_fields:
                query_string = r.ALL_FIELDS_QS
            else:
                query_string = ''
            deepnet = u.check_resource(deepnet,
                                       api.get_deepnet,
                                       query_string=query_string)
        deepnets[0] = deepnet
        if (args.public_deepnet or
                (args.shared_flag and r.shared_changed(args.shared,
                                                       deepnet))):
            deepnet_args = {}
            if args.shared_flag and r.shared_changed(args.shared,
                                                     deepnet):
                deepnet_args.update(shared=args.shared)
            if args.public_deepnet:
                deepnet_args.update( \
                    set_publish_model_args(args))
            if deepnet_args:
                deepnet = update_deepnet( \
                    deepnet, deepnet_args, args,
                    api=api, path=path, \
                    session_file=session_file)
                deepnet[0] = deepnet

    # We get the fields of the deepnet if we haven't got
    # them yet and need them
    if deepnet and (args.test_set or args.export_fields):
        fields = pdn.get_deepnet_fields( \
            deepnet, csv_properties, args)

    if fields and args.export_fields:
        fields.summary_csv(os.path.join(path, args.export_fields))

    # If predicting
    if deepnets and (a.has_test(args) or \
            (test_dataset and args.remote)):
        if test_dataset is None:
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
            batch_prediction_args = set_batch_prediction_args(
                args, fields=fields,
                dataset_fields=test_fields)

            remote_dn_prediction(deepnet, test_dataset, \
                batch_prediction_args, args, \
                api, resume, prediction_file=output, \
                session_file=session_file, path=path, log=log)

        else:
            dn_prediction(deepnets, fields, args,
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
            resume = evaluate(deepnets, args.test_dataset_ids, api,
                              args, resume,
                              fields=fields, dataset_fields=test_fields,
                              session_file=session_file, path=path,
                              log=log,
                              objective_field=args.objective_field)
        else:
            dataset = datasets[0]
            if args.test_split > 0 or args.has_test_datasets_:
                dataset = test_dataset
            dataset = u.check_resource(dataset, api=api,
                                       query_string=r.ALL_FIELDS_QS)
            dataset_fields = pd.get_fields_structure(dataset, None)
            resume = evaluate(deepnets, [dataset], api,
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
