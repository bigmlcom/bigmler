# -*- coding: utf-8 -*-
#
# Copyright 2016-2020 BigML
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

"""BigMLer - topic model subcommand processing dispatching

"""


import sys
import os

import bigml.api

import bigmler.utils as u
import bigmler.resourcesapi.common as r
import bigmler.resourcesapi.topic_models as rtm
import bigmler.resourcesapi.batch_topic_distributions as rtd
import bigmler.pre_model_steps as pms
import bigmler.processing.args as a
import bigmler.processing.sources as ps
import bigmler.processing.datasets as pd
import bigmler.processing.topicmodels as pt

from bigmler.resourcesapi.datasets import set_basic_dataset_args
from bigmler.defaults import DEFAULTS_FILE
from bigmler.reports import clear_reports, upload_reports
from bigmler.topicdistribution import (topic_distribution,
                                       remote_topic_distribution)
from bigmler.command import get_context
from bigmler.dispatcher import SESSIONS_LOG, clear_log_files, get_test_dataset

COMMAND_LOG = ".bigmler_topic_model"
DIRS_LOG = ".bigmler_topic_model_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]
MINIMUM_MODEL = "full=false"
DEFAULT_OUTPUT = "topic_distributions.csv"

SETTINGS = {
    "command_log": COMMAND_LOG,
    "sessions_log": SESSIONS_LOG,
    "dirs_log": DIRS_LOG,
    "default_output": DEFAULT_OUTPUT,
    "defaults_file": DEFAULTS_FILE}


def topic_model_dispatcher(args=sys.argv[1:]):
    """Parses command line and calls the different processing functions

    """

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        clear_log_files(LOG_FILES)

    command_args, _, api, session_file, resume = get_context(args, SETTINGS)

    # Selects the action to perform
    if a.has_train(command_args) or a.has_test(command_args):
        output_args = a.get_output_args(api, command_args, resume)
        compute_output(**output_args)
    u.log_message("_" * 80 + "\n", log_file=session_file)


def compute_output(api, args):
    """ Creates one or more models using the `training_set` or uses the ids
    of previously created BigML models to make predictions for the `test_set`.

    """

    topic_model = None
    topic_models = None
    # no multi-label support at present

    # variables from command-line options
    resume = args.resume_
    topic_model_ids = args.topic_model_ids_
    output = args.predictions
    # there's only one topic model resource to be generated at present
    args.max_parallel_topic_models = 1
    # topic models cannot be published yet.
    args.public_topic_model = False

    # It is compulsory to have a description to publish either datasets or
    # topic models
    if (not args.description_ and (args.public_topic_model or
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
    (_, datasets, test_dataset,
     resume, csv_properties, fields) = dataset_properties
    if args.topic_model_file:
        # topic model is retrieved from the contents of the given local JSON
        # file
        topic_model, csv_properties, fields = u.read_local_resource(
            args.topic_model_file,
            csv_properties=csv_properties)
        topic_models = [topic_model]
        topic_model_ids = [topic_model['resource']]
    else:
        # topic model is retrieved from the remote object
        topic_models, topic_model_ids, resume = pt.topic_model_processing(
            datasets, topic_models, topic_model_ids, api, args, resume,
            fields=fields,
            session_file=session_file, path=path, log=log)
        if topic_models:
            topic_model = topic_models[0]

    # We update the topic model's public state if needed
    if topic_model:
        if isinstance(topic_model, str):
            if not a.has_test(args):
                query_string = MINIMUM_MODEL
            else:
                query_string = ''
            topic_model = u.check_resource(topic_model, api.topic_model,
                                           query_string=query_string)
        topic_models[0] = topic_model
        if (args.public_topic_model or
                (args.shared_flag and
                 r.shared_changed(args.shared, topic_model))):
            topic_model_args = {}
            if args.shared_flag and \
                    r.shared_changed(args.shared, topic_model):
                topic_model_args.update(shared=args.shared)
            if args.public_topic_model:
                topic_model_args.update(rtm.set_publish_topic_model_args(args))
            if topic_model_args:
                topic_model = rtm.update_topic_model( \
                    topic_model, topic_model_args, args,
                    api=api, path=path,
                    session_file=session_file)
                topic_models[0] = topic_model

    # We get the fields of the topic model if we haven't got
    # them yet and need them
    if topic_model and args.test_set:
        csv_properties.update({'objective_field_present': False,
                               'objective_field': None})
        fields = pt.get_topic_model_fields(topic_model, csv_properties, args)

    # If predicting
    if topic_models and (a.has_test(args) or (test_dataset and args.remote)):
        if test_dataset is None:
            test_dataset = get_test_dataset(args)

        # Remote topic distributions:topic distributions are computed as
        # batch topic distributions
        # in bigml.com except when --no-batch flag is set.
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
            batch_topic_distribution_args = \
                rtd.set_batch_topic_distribution_args( \
                args, fields=fields, \
                dataset_fields=test_fields)

            remote_topic_distribution( \
                topic_model, test_dataset, batch_topic_distribution_args,
                args, api, resume, prediction_file=output,
                session_file=session_file, path=path, log=log)
        else:
            topic_distribution(topic_models, fields, args,
                               session_file=session_file)

    u.print_generated_files(path, log_file=session_file,
                            verbosity=args.verbosity)
    if args.reports:
        clear_reports(path)
        if args.upload:
            upload_reports(args.reports, path)
