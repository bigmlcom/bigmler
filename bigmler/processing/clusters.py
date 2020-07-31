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

"""BigMLer - Resources processing: creation, update and retrieval of clusters

"""


from bigml.fields import Fields, DEFAULT_MISSING_TOKENS

import bigmler.utils as u
import bigmler.resourcesapi.clusters as r
import bigmler.checkpoint as c


def has_clusters(args):
    """Returns whether some kind of cluster

    """
    return args.cluster or args.clusters or args.cluster_tag


def clusters_processing(datasets, clusters, cluster_ids,
                        api, args, resume, fields=None,
                        session_file=None, path=None,
                        log=None):
    """Creates or retrieves clusters from the input data

    """

    # If we have a dataset but not a model, we create the model if the no_model
    # flag hasn't been set up.
    if datasets and not (has_clusters(args) or args.no_cluster):
        cluster_ids = []
        clusters = []

        # Only 1 cluster per bigmler command at present
        number_of_clusters = 1
        if resume:
            resume, cluster_ids = c.checkpoint(
                c.are_clusters_created, path, number_of_clusters,
                debug=args.debug)
            if not resume:
                message = u.dated("Found %s clusters out of %s. Resuming.\n"
                                  % (len(cluster_ids),
                                     number_of_clusters))
                u.log_message(message, log_file=session_file,
                              console=args.verbosity)

            clusters = cluster_ids
            number_of_clusters -= len(cluster_ids)

        cluster_args = r.set_cluster_args(args,
                                          fields=fields,
                                          cluster_fields=args.cluster_fields_)
        clusters, cluster_ids = r.create_clusters(datasets, clusters,
                                                  cluster_args, args, api,
                                                  path, session_file, log)
    # If a cluster is provided, we use it.
    elif args.cluster:
        cluster_ids = [args.cluster]
        clusters = cluster_ids[:]

    elif args.clusters or args.cluster_tag:
        clusters = cluster_ids[:]

    # If we are going to predict we must retrieve the clusters
    if cluster_ids and args.test_set:
        clusters, cluster_ids = r.get_clusters(clusters, args, api,
                                               session_file)

    return clusters, cluster_ids, resume


def get_cluster_fields(cluster, csv_properties, args):
    """Retrieves fields info from cluster resource

    """
    if not csv_properties:
        csv_properties = {}
    csv_properties.update(verbose=True)
    if args.user_locale is None:
        args.user_locale = cluster['object'].get('locale', None)
    csv_properties.update(data_locale=args.user_locale)
    csv_properties.update(missing_tokens=DEFAULT_MISSING_TOKENS)
    return Fields(cluster['object']['clusters']['fields'], **csv_properties)
