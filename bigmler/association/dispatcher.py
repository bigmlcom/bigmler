# -*- coding: utf-8 -*-
#
# Copyright 2015-2020 BigML
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

"""BigMLer - association subcommand processing dispatching

"""


import sys
import os


import bigmler.utils as u
import bigmler.resourcesapi.common as r
import bigmler.resourcesapi.associations as ras
import bigmler.pre_model_steps as pms
import bigmler.processing.args as a
import bigmler.processing.associations as pa

from bigmler.defaults import DEFAULTS_FILE
from bigmler.reports import clear_reports, upload_reports
from bigmler.command import get_context
from bigmler.dispatcher import SESSIONS_LOG, clear_log_files, get_test_dataset

COMMAND_LOG = ".bigmler_association"
DIRS_LOG = ".bigmler_association_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]
MINIMUM_MODEL = "full=false"
DEFAULT_OUTPUT = "association_sets.csv"

SETTINGS = {
    "command_log": COMMAND_LOG,
    "sessions_log": SESSIONS_LOG,
    "dirs_log": DIRS_LOG,
    "default_output": DEFAULT_OUTPUT,
    "defaults_file": DEFAULTS_FILE}


def association_dispatcher(args=sys.argv[1:]):
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

    association = None
    associations = None
    # no multi-label support at present

    # variables from command-line options
    resume = args.resume_
    association_ids = args.association_ids_
    output = args.predictions
    # there's only one association resource to be generated at present
    args.max_parallel_associations = 1
    # associations cannot be published yet.
    args.public_association = False

    # It is compulsory to have a description to publish either datasets or
    # associations
    if (not args.description_ and (args.public_association or
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
    if args.association_file:
        # association is retrieved from the contents of the given local JSON
        # file
        association, csv_properties, fields = u.read_local_resource(
            args.association_file,
            csv_properties=csv_properties)
        associations = [association]
        association_ids = [association['resource']]
    else:
        # association is retrieved from the remote object
        associations, association_ids, resume = pa.associations_processing(
            datasets, associations, association_ids, api, args, resume,
            fields=fields,
            session_file=session_file, path=path, log=log)
        if associations:
            association = associations[0]

    # We update the association's public state if needed
    if association:
        if isinstance(association, str):
            if not a.has_test(args):
                query_string = MINIMUM_MODEL
            else:
                query_string = ''
            association = u.check_resource(association, api.get_association,
                                           query_string=query_string)
        associations[0] = association
        if (args.public_association or
                (args.shared_flag and
                 r.shared_changed(args.shared, association))):
            association_args = {}
            if args.shared_flag and \
                    r.shared_changed(args.shared, association):
                association_args.update(shared=args.shared)
            if args.public_association:
                association_args.update(ras.set_publish_association_args(args))
            if association_args:
                association = ras.update_association( \
                    association, association_args, args,
                    api=api, path=path,
                    session_file=session_file)
                associations[0] = association

    # We get the fields of the association if we haven't got
    # them yet and need them
    if association and args.test_set:
        fields = pa.get_association_fields(association, csv_properties, args)

    # If predicting
    if associations and (a.has_test(args) or (test_dataset and args.remote)):
        if test_dataset is None:
            test_dataset = get_test_dataset(args)

        # Remote association sets: association sets are computed as
        # batch association sets
        # in bigml.com except when --no-batch flag is set. They are currently
        # not supported yet
        if args.remote and not args.no_batch:
            sys.exit("Batch association sets are currently not supported.")
        else:
            sys.exit("Local prediction of association sets is currently"
                     " not supported.")
    u.print_generated_files(path, log_file=session_file,
                            verbosity=args.verbosity)
    if args.reports:
        clear_reports(path)
        if args.upload:
            upload_reports(args.reports, path)
