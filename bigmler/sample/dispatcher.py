# -*- coding: utf-8 -*-
#
# Copyright 2015-2017 BigML
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

"""BigMLer - sample subcommand processing dispatching

"""
from __future__ import absolute_import

import sys
import os
import shutil

import bigmler.utils as u
import bigmler.resources as r
import bigmler.pre_model_steps as pms
import bigmler.processing.args as a
import bigmler.processing.samples as psa

from bigmler.defaults import DEFAULTS_FILE
from bigmler.command import get_stored_command
from bigmler.dispatcher import (SESSIONS_LOG, command_handling,
                                clear_log_files)
from bigmler.sampleoutput import sample_file
from bigmler.reports import clear_reports, upload_reports

COMMAND_LOG = u".bigmler_sample"
DIRS_LOG = u".bigmler_sample_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]
MINIMUM_MODEL = "full=false"
DEFAULT_OUTPUT = u"sample.csv"


def has_sample(args):
    """Returns if some kind of sample id is given in args.

    """
    return args.sample or args.samples or args.sample_tag


def sample_dispatcher(args=sys.argv[1:]):
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
        command_args, session_file, output_dir = get_stored_command(
            args, command_args.debug, command_log=COMMAND_LOG,
            dirs_log=DIRS_LOG, sessions_log=SESSIONS_LOG)
        command_args.predictions = os.path.join(output_dir,
                                                DEFAULT_OUTPUT)
    else:
        if command_args.output_dir is None:
            command_args.output_dir = a.NOW
        command_args.predictions = os.path.join(command_args.output_dir,
                                                DEFAULT_OUTPUT)
        if len(os.path.dirname(command_args.predictions).strip()) == 0:
            command_args.predictions = os.path.join(command_args.output_dir,
                                                    command_args.predictions)
        directory = u.check_dir(command_args.predictions)
        session_file = os.path.join(directory, SESSIONS_LOG)
        u.log_message(command.command + "\n", log_file=session_file)
        try:
            shutil.copy(DEFAULTS_FILE, os.path.join(directory, DEFAULTS_FILE))
        except IOError:
            pass
        u.sys_log_message(u"%s\n" % os.path.abspath(directory),
                          log_file=DIRS_LOG)

    # Creates the corresponding api instance
    api = a.get_api_instance(command_args, u.check_dir(session_file))

    # Selects the action to perform
    if a.has_train(command_args) or has_sample(command_args):
        output_args = a.get_output_args(api, command_args, resume)
        a.transform_args(command_args, command.flags, api)
        compute_output(**output_args)
    u.log_message("_" * 80 + "\n", log_file=session_file)


def compute_output(api, args):
    """ Creates a sample based on a `train_set`, source or dataset.

    """

    samples = None
    # variables from command-line options
    resume = args.resume_
    sample_ids = args.sample_ids_
    output = args.predictions
    # there's only one sample to be generated at present
    args.max_parallel_clusters = 1
    # sample cannot be published yet.
    args.public_sample = False

    # It is compulsory to have a description to publish either datasets or
    # clusters
    if (not args.description_ and (args.public_sample or
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

    # basic pre-sample step: creating or retrieving the source related info
    source, resume, csv_properties, fields = pms.get_source_info(
        api, args, resume, csv_properties, session_file, path, log)
    # basic pre-sample step: creating or retrieving the dataset related info
    dataset_properties = pms.get_dataset_info(
        api, args, resume, source,
        csv_properties, fields, session_file, path, log)
    (_, datasets, _, resume,
     csv_properties, fields) = dataset_properties
    if args.sample_file:
        # sample is retrieved from the contents of the given local JSON file
        sample, csv_properties, fields = u.read_local_resource(
            args.sample_file,
            csv_properties=csv_properties)
        samples = [sample]
        sample_ids = [sample['resource']]
    else:
        # sample is retrieved from the remote object
        samples, sample_ids, resume = psa.samples_processing(
            datasets, samples, sample_ids, api, args, resume,
            session_file=session_file, path=path, log=log)
        if samples:
            sample = samples[0]

    # We update the sample's public state if needed
    if sample:
        if isinstance(sample, basestring):
            # build the query string from the sample options
            sample = u.check_resource(sample, api.get_sample)
        samples[0] = sample
        if (args.public_sample or
                (args.shared_flag and r.shared_changed(args.shared, sample))):
            sample_args = {}
            if args.shared_flag and r.shared_changed(args.shared, sample):
                sample_args.update(shared=args.shared)
            if args.public_sample:
                sample_args.update(r.set_publish_sample_args(args))
            if sample_args:
                sample = r.update_sample(sample, sample_args, args,
                                         api=api, path=path,
                                         session_file=session_file)
                samples[0] = sample

    # We get the fields of the sample if we haven't got
    # them yet and need them
    if sample and psa.needs_sample_fields(args):
        fields = psa.get_sample_fields(sample, csv_properties, args)

    if fields and args.export_fields:
        fields.summary_csv(os.path.join(path, args.export_fields))

    sample_file(samples[0], fields, args, api, path=path,
                session_file=session_file)

    u.print_generated_files(path, log_file=session_file,
                            verbosity=args.verbosity)
    if args.reports:
        clear_reports(path)
        if args.upload:
            upload_reports(args.reports, path)
