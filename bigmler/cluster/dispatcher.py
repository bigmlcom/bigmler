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

"""BigMLer - cluster subcommand processing dispatching

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
import bigmler.processing.clusters as pc

from bigmler.defaults import DEFAULTS_FILE
from bigmler.centroid import centroid, remote_centroid
from bigmler.reports import clear_reports, upload_reports
from bigmler.command import Command, StoredCommand
from bigmler.dispatcher import (SESSIONS_LOG, command_handling,
                                clear_log_files,
                                has_test, has_train)

COMMAND_LOG = ".bigmler_cluster"
DIRS_LOG = ".bigmler_cluster_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]
MINIMUM_MODEL = "full=false"
DEFAULT_OUTPUT = "centroids.csv"


def cluster_dispatcher(args=sys.argv[1:]):
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
        with open(DIRS_LOG, "a", 0) as directory_log:
            directory_log.write("%s\n" % os.path.abspath(directory))

    # Creates the corresponding api instance
    if resume and debug:
        command_args.debug = True
    api = a.get_api_instance(command_args, u.check_dir(session_file))

    # Selects the action to perform
    if (has_train(command_args) or has_test(command_args)
            or command_args.cluster_datasets is not None):
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
    cluster = None
    clusters = None
    fields = None
    # no multi-label support at present

    # variables from command-line options
    resume = args.resume_
    cluster_ids = args.cluster_ids_
    output = args.predictions
    # there's only one cluster to be generated at present
    args.max_parallel_clusters = 1
    # clusters cannot be published yet.
    args.public_cluster = False

    # It is compulsory to have a description to publish either datasets or
    # clusters
    if (not args.description_ and (args.public_cluster or
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

    clusters, cluster_ids, resume = pc.clusters_processing(
        datasets, clusters, cluster_ids, api, args, resume, fields=fields,
        session_file=session_file, path=path, log=log)
    if clusters:
        cluster = clusters[0]

    # We update the cluster's public state if needed
    if cluster:
        if isinstance(cluster, basestring):
            if args.cluster_datasets is None and not has_test(args):
                query_string = MINIMUM_MODEL
            else:
                query_string = ''
            cluster = u.check_resource(cluster, api.get_cluster,
                                       query_string=query_string)
        clusters[0] = cluster
        if (args.public_cluster or
                (args.shared_flag and r.shared_changed(args.shared, cluster))):
            cluster_args = {}
            if args.shared_flag and r.shared_changed(args.shared, cluster):
                cluster_args.update(shared=args.shared)
            if args.public_cluster:
                cluster_args.update(r.set_publish_cluster_args(args))
            if cluster_args:
                cluster = r.update_cluster(cluster, cluster_args, args,
                                           api=api, path=path,
                                           session_file=session_file)
                clusters[0] = cluster

    # We get the fields of the cluster if we haven't got
    # them yet and need them
    if cluster and args.test_set:
        fields = pc.get_cluster_fields(cluster, csv_properties, args)

    # If predicting
    if clusters and has_test(args):
        test_dataset = None

        # Remote centroids: centroids are computed as batch centroids
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
            batch_centroid_args = r.set_batch_centroid_args(
                args, fields=fields,
                dataset_fields=test_fields)

            remote_centroid(cluster, test_dataset, batch_centroid_args, args,
                            api, resume, prediction_file=output,
                            session_file=session_file, path=path, log=log)

        else:
            centroid(clusters, fields, args, session_file=session_file)

    if cluster and args.cluster_datasets is not None:
        centroids_info = cluster['object']['clusters']['clusters']
        centroids = {centroid['name']: centroid['id']
                          for centroid in centroids_info}
        datasets = cluster['object']['cluster_datasets']
        if args.cluster_datasets == '':
            centroid_ids = centroids.values()
        else:
            centroid_ids = [centroids[cluster_name] for cluster_name in
                            args.cluster_datasets_
                            if datasets[centroids[cluster_name]] == '']
        
        for centroid_id in centroid_ids:
            dataset_args = {'centroid': centroid_id}
            r.create_dataset(cluster, dataset_args, args, api=api, path=path,
                             session_file=session_file, log=log,
                             dataset_type='cluster')

    # Workaround to restore windows console cp850 encoding to print the tree
    if sys.platform == "win32" and sys.stdout.isatty():
        import locale
        data_locale = locale.getlocale()
        if not data_locale[0] is None:
            locale.setlocale(locale.LC_ALL, (data_locale[0], "850"))
        message = (u"\nGenerated files:\n\n" +
                   unicode(u.print_tree(path, u" "), "utf-8") + u"\n")
    else:
        message = (u"\nGenerated files:\n\n" +
                   u.print_tree(path, u" ") + u"\n")
    u.log_message(message, log_file=session_file, console=args.verbosity)
    if args.reports:
        clear_reports(path)
        if args.upload:
            upload_reports(args.reports, path)
