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

from bigmler.resourcesapi.common import set_basic_args, \
    configure_input_fields, update_sample_parameters_args, \
    update_json_args, wait_for_available_tasks

from bigmler.resourcesapi.common import SEED, FIELDS_QS, \
    ALL_FIELDS_QS


def set_pca_args(args, name=None, fields=None,
                 pca_fields=None):
    """Return pca arguments dict

    """
    if name is None:
        name = args.name
    if pca_fields is None:
        pca_fields = args.pca_fields_

    pca_args = set_basic_args(args, name)
    pca_args.update({
        "seed": SEED if args.seed is None else args.seed,
        "pca_seed": SEED if args.seed is None else args.seed
    })

    pca_args.update({"sample_rate": args.sample_rate})
    pca_args = update_sample_parameters_args( \
        pca_args, args)
    if fields is not None:
        input_fields = list(fields.fields.keys())
    if pca_fields and fields is not None:
        input_fields = configure_input_fields(fields, pca_fields)
    if args.exclude_objective:
        input_fields = [field for field in input_fields \
            if field not in args.exclude_fields]
    pca_args.update(input_fields=input_fields)

    if 'pca' in args.json_args:
        update_json_args(pca_args,
                         args.json_args.get('pca'),
                         fields)
    return pca_args


def create_pca(datasets, pca, pca_args,
               args, api=None, path=None,
               session_file=None, log=None):
    """Create remote pcas

    """
    if api is None:
        api = bigml.api.BigML()

    pcas = []
    pca_ids = []
    if pca is not None:
        pcas = [pca]
        pca_ids = [pca]
    existing_pcas = len(pcas)
    pca_args_list = []
    datasets = datasets[existing_pcas:]
    # if resuming and all pcas were created, there will
    # be no datasets left
    if datasets:
        if isinstance(pca_args, list):
            pca_args_list = pca_args

        # Only one pca per command, at present
        number_of_pcas = 1
        message = dated("Creating %s.\n" %
                        plural("pca", number_of_pcas))
        log_message(message, log_file=session_file,
                    console=args.verbosity)

        query_string = FIELDS_QS
        inprogress = []
        for i in range(0, number_of_pcas):
            wait_for_available_tasks(inprogress,
                                     args.max_parallel_pcas,
                                     api, "pca")
            if pca_args_list:
                pca_args = pca_args_list[i]

            pca = api.create_pca(datasets,
                                 pca_args,
                                 retries=None)
            pca_id = check_resource_error( \
                pca,
                "Failed to create pca: ")
            log_message("%s\n" % pca_id, log_file=log)
            pca_ids.append(pca_id)
            inprogress.append(pca_id)
            pcas.append(pca)
            log_created_resources("pcas", path, pca_id,
                                  mode='a')

        if args.verbosity:
            if bigml.api.get_status(pca)['code'] != bigml.api.FINISHED:
                try:
                    pca = check_resource( \
                        pca, api.get_pca,
                        query_string=query_string,
                        raise_on_error=True)
                except Exception as exception:
                    sys.exit("Failed to get a finished pca: %s" %
                             str(exception))
                pcas[0] = pca
            message = dated("PCA created: %s\n" %
                            get_url(pca))
            log_message(message, log_file=session_file,
                        console=args.verbosity)
            if args.reports:
                report(args.reports, path, pca)

    return pca


def get_pca(pca,
            args, api=None, session_file=None):
    """Retrieves remote pca in its actual status

    """
    if api is None:
        api = bigml.api.BigML()

    message = dated("Retrieving PCA. %s\n" %
                    get_url(pca))
    log_message(message, log_file=session_file, console=args.verbosity)
    # only one PCA at present
    try:
        # we need the whole fields structure when exporting fields
        query_string = FIELDS_QS if not args.export_fields else ALL_FIELDS_QS
        pca = check_resource(pca,
                             api.get_pca,
                             query_string=query_string,
                             raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a finished pca: %s" % \
            str(exception))

    return pca


def set_publish_pca_args(args):
    """Set args to publish pca

    """
    public_pca = {}
    if args.public_pca:
        public_pca = {"private": False}
        if args.model_price:
            public_pca.update(price=args.model_price)
        if args.cpp:
            public_pca.update(credits_per_prediction=args.cpp)
    return public_pca


def update_pca(pca, pca_args,
               args, api=None, path=None, session_file=None):
    """Updates pca properties

    """
    if api is None:
        api = bigml.api.BigML()

    message = dated("Updating PCA. %s\n" %
                    get_url(pca))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    pca = api.update_pca(pca, pca_args)
    check_resource_error(pca,
                         "Failed to update PCA: %s"
                         % pca['resource'])
    pca = check_resource(pca,
                         api.get_pca,
                         query_string=FIELDS_QS,
                         raise_on_error=True)
    if is_shared(pca):
        message = dated("Shared PCA link. %s\n" %
                        get_url(pca, shared=True))
        log_message(message, log_file=session_file, console=args.verbosity)
        if args.reports:
            report(args.reports, path, pca)

    return pca
