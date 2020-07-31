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

"""BigMLer - cluster subcommand processing dispatching

"""


import sys
import os

import bigml.api
import bigmler.utils as u
import bigmler.resourcesapi.common as r
import bigmler.resourcesapi.clusters as rcl
import bigmler.resourcesapi.batch_centroids as rbc
import bigmler.pre_model_steps as pms
import bigmler.processing.args as a
import bigmler.processing.clusters as pc
import bigmler.processing.sources as ps
import bigmler.processing.datasets as pd

from bigmler.resourcesapi.datasets import create_dataset, \
    set_basic_dataset_args
from bigmler.resourcesapi.models import create_model
from bigmler.defaults import DEFAULTS_FILE
from bigmler.centroid import centroid, remote_centroid
from bigmler.reports import clear_reports, upload_reports
from bigmler.command import get_context
from bigmler.dispatcher import SESSIONS_LOG, clear_log_files, get_test_dataset

COMMAND_LOG = ".bigmler_cluster"
DIRS_LOG = ".bigmler_cluster_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]
MINIMUM_MODEL = "full=false"
DEFAULT_OUTPUT = "centroids.csv"

SETTINGS = {
    "command_log": COMMAND_LOG,
    "sessions_log": SESSIONS_LOG,
    "dirs_log": DIRS_LOG,
    "default_output": DEFAULT_OUTPUT,
    "defaults_file": DEFAULTS_FILE}


def cluster_dispatcher(args=sys.argv[1:]):
    """Parses command line and calls the different processing functions

    """

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        clear_log_files(LOG_FILES)

    command_args, _, api, session_file, resume = get_context(args, SETTINGS)

    # Selects the action to perform
    if (a.has_train(command_args) or a.has_test(command_args)
            or command_args.cluster_datasets is not None
            or command_args.export_fields is not None):
        output_args = a.get_output_args(api, command_args, resume)
        compute_output(**output_args)
    u.log_message("_" * 80 + "\n", log_file=session_file)


def compute_output(api, args):
    """ Creates one or more models using the `training_set` or uses the ids
    of previously created BigML models to make predictions for the `test_set`.

    """

    cluster = None
    clusters = None
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

    # basic pre-model step: creating or retrieving the source related info
    source, resume, csv_properties, fields = pms.get_source_info(
        api, args, resume, csv_properties, session_file, path, log)
    # basic pre-model step: creating or retrieving the dataset related info
    dataset_properties = pms.get_dataset_info(
        api, args, resume, source,
        csv_properties, fields, session_file, path, log)
    (_, datasets, test_dataset,
     resume, csv_properties, fields) = dataset_properties
    if args.cluster_file:
        # cluster is retrieved from the contents of the given local JSON file
        cluster, csv_properties, fields = u.read_local_resource(
            args.cluster_file,
            csv_properties=csv_properties)
        clusters = [cluster]
        cluster_ids = [cluster['resource']]
    else:
        # cluster is retrieved from the remote object
        clusters, cluster_ids, resume = pc.clusters_processing(
            datasets, clusters, cluster_ids, api, args, resume, fields=fields,
            session_file=session_file, path=path, log=log)
        if clusters:
            cluster = clusters[0]

    # We update the cluster's public state if needed
    if cluster:
        if isinstance(cluster, str):
            if args.cluster_datasets is None and not a.has_test(args):
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
                cluster_args.update(rcl.set_publish_cluster_args(args))
            if cluster_args:
                cluster = rcl.update_cluster(cluster, cluster_args, args,
                                             api=api, path=path,
                                             session_file=session_file)
                clusters[0] = cluster

    # We get the fields of the cluster if we haven't got
    # them yet and need them
    if cluster and (args.test_set or args.export_fields):
        if isinstance(cluster, dict):
            cluster = cluster['resource']
            cluster = u.check_resource(cluster, api.get_cluster,
                                       query_string=r.ALL_FIELDS_QS)
        fields = pc.get_cluster_fields(cluster, csv_properties, args)

    # If predicting
    if clusters and (a.has_test(args) or (test_dataset and args.remote)):
        if test_dataset is None:
            test_dataset = get_test_dataset(args)

        # Remote centroids: centroids are computed as batch centroids
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
            batch_centroid_args = rbc.set_batch_centroid_args(
                args, fields=fields,
                dataset_fields=test_fields)

            remote_centroid(cluster, test_dataset, batch_centroid_args, args,
                            api, resume, prediction_file=output,
                            session_file=session_file, path=path, log=log)

        else:
            centroid(clusters, fields, args, session_file=session_file)

    if cluster and args.cluster_datasets is not None:
        cluster = api.check_resource(cluster)
        centroids_info = cluster['object']['clusters']['clusters']
        centroids = {centroid['name']: centroid['id']
                     for centroid in centroids_info}
        cluster_datasets = cluster['object']['cluster_datasets']
        if args.cluster_datasets == '':
            centroid_ids = list(centroids.values())
        else:
            centroid_ids = [centroids[cluster_name] for cluster_name in
                            args.cluster_datasets_
                            if cluster_datasets.get(centroids[cluster_name],
                                                    '') == '']

        for centroid_id in centroid_ids:
            dataset_args = {'centroid': centroid_id}
            create_dataset(cluster, dataset_args, args, api=api, path=path,
                           session_file=session_file, log=log,
                           dataset_type='cluster')

    if cluster and args.cluster_models is not None:
        cluster = api.check_resource(cluster)
        centroids_info = cluster['object']['clusters']['clusters']
        centroids = {centroid['name']: centroid['id']
                     for centroid in centroids_info}
        models = cluster['object']['cluster_models']
        if args.cluster_models == '':
            centroid_ids = list(centroids.values())
        else:
            centroid_ids = [centroids[cluster_name] for cluster_name in
                            args.cluster_models_
                            if models.get(centroids[cluster_name], '') == '']

        for centroid_id in centroid_ids:
            model_args = {'centroid': centroid_id}
            create_model(cluster, model_args, args, api=api, path=path,
                         session_file=session_file, log=log,
                         model_type='cluster')

    if fields and args.export_fields:
        fields.summary_csv(os.path.join(path, args.export_fields))

    u.print_generated_files(path, log_file=session_file,
                            verbosity=args.verbosity)
    if args.reports:
        clear_reports(path)
        if args.upload:
            upload_reports(args.reports, path)
