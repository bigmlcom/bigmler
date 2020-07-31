# -*- coding: utf-8 -*-
#
# Copyright 2020 BigML
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
"""Resources management functions

"""


import sys

import bigml.api

from bigmler.utils import (dated, get_url, log_message, check_resource,
                           plural, is_shared,
                           check_resource_error, log_created_resources)
from bigmler.reports import report

from bigmler.resourcesapi.common import set_basic_model_args, \
    configure_input_fields, update_sample_parameters_args, \
    update_json_args, wait_for_available_tasks

from bigmler.resourcesapi.common import SEED, FIELDS_QS, \
    ALL_FIELDS_QS


def set_cluster_args(args, name=None, fields=None,
                     cluster_fields=None):
    """Return cluster arguments dict

    """
    if name is None:
        name = args.name
    if cluster_fields is None:
        cluster_fields = args.cluster_fields_

    cluster_args = set_basic_model_args(args, name)
    cluster_args.update({
        "seed": SEED if args.seed is None else args.seed,
        "cluster_seed": (SEED if args.cluster_seed is None
                         else args.cluster_seed)
    })

    if args.cluster_models is not None:
        cluster_args.update({"model_clusters": True})
    if args.cluster_k:
        cluster_args.update({"k": args.cluster_k})
    if cluster_fields and fields is not None:
        input_fields = configure_input_fields(fields, cluster_fields)
        cluster_args.update(input_fields=input_fields)
    if args.summary_fields is not None:
        cluster_args.update({"summary_fields": args.summary_fields_})

    cluster_args = update_sample_parameters_args(cluster_args, args)

    if 'cluster' in args.json_args:
        update_json_args(cluster_args, args.json_args.get('cluster'), fields)

    return cluster_args


def create_clusters(datasets, cluster_ids, cluster_args,
                    args, api=None, path=None,
                    session_file=None, log=None):
    """Create remote clusters

    """
    if api is None:
        api = bigml.api.BigML()

    clusters = cluster_ids[:]
    existing_clusters = len(clusters)
    cluster_args_list = []
    datasets = datasets[existing_clusters:]
    # if resuming and all clusters were created, there will be no datasets left
    if datasets:
        if isinstance(cluster_args, list):
            cluster_args_list = cluster_args

        # Only one cluster per command, at present
        number_of_clusters = 1
        message = dated("Creating %s.\n" %
                        plural("cluster", number_of_clusters))
        log_message(message, log_file=session_file,
                    console=args.verbosity)

        query_string = FIELDS_QS
        inprogress = []
        for i in range(0, number_of_clusters):
            wait_for_available_tasks(inprogress, args.max_parallel_clusters,
                                     api, "cluster")
            if cluster_args_list:
                cluster_args = cluster_args_list[i]

            cluster = api.create_cluster(datasets, cluster_args, retries=None)
            cluster_id = check_resource_error(cluster,
                                              "Failed to create cluster: ")
            log_message("%s\n" % cluster_id, log_file=log)
            cluster_ids.append(cluster_id)
            inprogress.append(cluster_id)
            clusters.append(cluster)
            log_created_resources("clusters", path, cluster_id, mode='a')

        if args.verbosity:
            if bigml.api.get_status(cluster)['code'] != bigml.api.FINISHED:
                try:
                    cluster = check_resource(cluster, api.get_cluster,
                                             query_string=query_string,
                                             raise_on_error=True)
                except Exception as exception:
                    sys.exit("Failed to get a finished cluster: %s" %
                             str(exception))
                clusters[0] = cluster
            message = dated("Cluster created: %s\n" %
                            get_url(cluster))
            log_message(message, log_file=session_file,
                        console=args.verbosity)
            if args.reports:
                report(args.reports, path, cluster)

    return clusters, cluster_ids


def get_clusters(cluster_ids, args, api=None, session_file=None):
    """Retrieves remote clusters in its actual status

    """
    if api is None:
        api = bigml.api.BigML()
    cluster_id = ""
    clusters = cluster_ids
    cluster_id = cluster_ids[0]
    message = dated("Retrieving %s. %s\n" %
                    (plural("cluster", len(cluster_ids)),
                     get_url(cluster_id)))
    log_message(message, log_file=session_file, console=args.verbosity)
    # only one cluster to predict at present
    try:
        # we need the whole fields structure when exporting fields
        query_string = FIELDS_QS if not args.export_fields else ALL_FIELDS_QS
        cluster = check_resource(cluster_ids[0], api.get_cluster,
                                 query_string=query_string,
                                 raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a finished cluster: %s" % str(exception))
    clusters[0] = cluster

    return clusters, cluster_ids


def set_publish_cluster_args(args):
    """Set args to publish cluster

    """
    public_cluster = {}
    if args.public_cluster:
        public_cluster = {"private": False}
        if args.model_price:
            public_cluster.update(price=args.model_price)
        if args.cpp:
            public_cluster.update(credits_per_prediction=args.cpp)
    return public_cluster


def update_cluster(cluster, cluster_args, args,
                   api=None, path=None, session_file=None):
    """Updates cluster properties

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Updating cluster. %s\n" %
                    get_url(cluster))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    cluster = api.update_cluster(cluster, cluster_args)
    check_resource_error(cluster, "Failed to update cluster: %s"
                         % cluster['resource'])
    cluster = check_resource(cluster, api.get_cluster, query_string=FIELDS_QS,
                             raise_on_error=True)
    if is_shared(cluster):
        message = dated("Shared cluster link. %s\n" %
                        get_url(cluster, shared=True))
        log_message(message, log_file=session_file, console=args.verbosity)
        if args.reports:
            report(args.reports, path, cluster)

    return cluster
