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

from bigmler.utils import (dated, get_url, log_message, plural, check_resource,
                           check_resource_error, log_created_resources,
                           is_shared)
from bigmler.reports import report
from bigmler.resourcesapi.common import set_basic_model_args, \
    configure_input_fields, update_sample_parameters_args, \
    update_json_args, wait_for_available_tasks


from bigmler.resourcesapi.common import FIELDS_QS


def set_association_args(args, name=None, fields=None,
                         association_fields=None):
    """Return association arguments dict

    """
    if name is None:
        name = args.name
    if association_fields is None:
        association_fields = args.association_fields_

    association_args = set_basic_model_args(args, name)

    if association_fields and fields is not None:
        input_fields = configure_input_fields(fields, association_fields)
        association_args.update(input_fields=input_fields)
    if args.association_k:
        association_args.update({"max_k": args.association_k})
    if args.search_strategy:
        association_args.update({"search_strategy": args.search_strategy})

    association_args = update_sample_parameters_args(association_args, args)

    if 'association' in args.json_args:
        update_json_args(association_args,
                         args.json_args.get('association'), fields)

    return association_args


def create_associations(datasets, association_ids, association_args,
                        args, api=None, path=None,
                        session_file=None, log=None):
    """Create remote associations

    """
    if api is None:
        api = bigml.api.BigML()

    associations = association_ids[:]
    existing_associations = len(associations)
    association_args_list = []
    datasets = datasets[existing_associations:]
    # if resuming and all associations were created,
    # there will be no datasets left
    if datasets:
        if isinstance(association_args, list):
            association_args_list = association_args

        # Only one association per command, at present
        number_of_associations = 1
        message = dated("Creating %s.\n" %
                        plural("association", number_of_associations))
        log_message(message, log_file=session_file,
                    console=args.verbosity)

        query_string = FIELDS_QS
        inprogress = []
        for i in range(0, number_of_associations):
            wait_for_available_tasks(inprogress,
                                     args.max_parallel_associations,
                                     api, "association")
            if association_args_list:
                association_args = association_args_list[i]

            association = api.create_association(
                datasets, association_args, retries=None)
            association_id = check_resource_error( \
                association, "Failed to create association: ")
            log_message("%s\n" % association_id, log_file=log)
            association_ids.append(association_id)
            inprogress.append(association_id)
            associations.append(association)
            log_created_resources( \
                "associations", path, association_id, mode='a')

        if args.verbosity:
            if bigml.api.get_status(association)['code'] != bigml.api.FINISHED:
                try:
                    association = check_resource( \
                        association, api.get_association,
                        query_string=query_string,
                        raise_on_error=True)
                except Exception as exception:
                    sys.exit("Failed to get a finished association: %s" %
                             str(exception))
                associations[0] = association
            message = dated("Association created: %s\n" %
                            get_url(association))
            log_message(message, log_file=session_file,
                        console=args.verbosity)
            if args.reports:
                report(args.reports, path, association)

    return associations, association_ids


def get_associations(association_ids, args, api=None, session_file=None):
    """Retrieves remote associations in its actual status

    """
    if api is None:
        api = bigml.api.BigML()

    association_id = ""
    associations = association_ids
    association_id = association_ids[0]
    message = dated("Retrieving %s. %s\n" %
                    (plural("association", len(association_ids)),
                     get_url(association_id)))
    log_message(message, log_file=session_file, console=args.verbosity)
    # only one association to predict at present
    try:
        query_string = FIELDS_QS
        association = check_resource(association_ids[0], api.get_association,
                                     query_string=query_string,
                                     raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a finished association: %s" % str(exception))
    associations[0] = association

    return associations, association_ids


def set_publish_association_args(args):
    """Set args to publish association

    """
    public_association = {}
    if args.public_association:
        public_association = {"private": False}
        if args.model_price:
            public_association.update(price=args.model_price)
        if args.cpp:
            public_association.update(credits_per_prediction=args.cpp)
    return public_association


def update_association(association, association_args, args,
                       api=None, path=None, session_file=None):
    """Updates association properties

    """
    if api is None:
        api = bigml.api.BigML()

    message = dated("Updating association. %s\n" %
                    get_url(association))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    association = api.update_association(association, association_args)
    check_resource_error(association, "Failed to update association: %s"
                         % association['resource'])
    association = check_resource(association,
                                 api.get_association, query_string=FIELDS_QS,
                                 raise_on_error=True)
    if is_shared(association):
        message = dated("Shared association link. %s\n" %
                        get_url(association, shared=True))
        log_message(message, log_file=session_file, console=args.verbosity)
        if args.reports:
            report(args.reports, path, association)

    return association
