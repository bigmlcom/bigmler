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
                           is_shared,
                           check_resource_error, log_created_resources)
from bigmler.reports import report

from bigmler.resourcesapi.common import set_basic_args, \
    update_json_args, wait_for_available_tasks

from bigmler.resourcesapi.common import FIELDS_QS, \
    ALL_FIELDS_QS


def set_fusion_args(args, name=None, fields=None):
    """Return fusion arguments dict

    """
    if name is None:
        name = args.name

    fusion_args = set_basic_args(args, name)

    if 'fusion' in args.json_args:
        update_json_args(fusion_args,
                         args.json_args.get('fusion'),
                         fields)
    return fusion_args


def create_fusion(models, fusion, fusion_args,
                  args, api=None, path=None,
                  session_file=None, log=None):
    """Create remote fusion

    """
    if api is None:
        api = bigml.api.BigML()

    fusions = []
    fusion_ids = []
    if fusion is not None:
        fusions = [fusion]
        fusion_ids = [fusion]
    # if resuming and all fusions were created
    if models:

        # Only one fusion per command, at present
        message = dated("Creating fusion.\n")
        log_message(message, log_file=session_file,
                    console=args.verbosity)

        query_string = FIELDS_QS
        inprogress = []
        wait_for_available_tasks(inprogress,
                                 args.max_parallel_fusions,
                                 api, "fusion")

        fusion = api.create_fusion(models,
                                   fusion_args,
                                   retries=None)
        fusion_id = check_resource_error( \
            fusion,
            "Failed to create fusion: ")
        log_message("%s\n" % fusion_id, log_file=log)
        fusion_ids.append(fusion_id)
        inprogress.append(fusion_id)
        fusions.append(fusion)
        log_created_resources("fusions", path, fusion_id,
                              mode='a')

        if args.verbosity:
            if bigml.api.get_status(fusion)['code'] != bigml.api.FINISHED:
                try:
                    fusion = check_resource( \
                        fusion, api.get_fusion,
                        query_string=query_string,
                        raise_on_error=True)
                except Exception as exception:
                    sys.exit("Failed to get a finished fusion: %s" %
                             str(exception))
                fusions[0] = fusion
            message = dated("Fusion created: %s\n" %
                            get_url(fusion))
            log_message(message, log_file=session_file,
                        console=args.verbosity)
            if args.reports:
                report(args.reports, path, fusion)

    return fusion


def get_fusion(fusion,
               args, api=None, session_file=None):
    """Retrieves remote fusion in its actual status

    """
    if api is None:
        api = bigml.api.BigML()

    message = dated("Retrieving Fusion. %s\n" %
                    get_url(fusion))
    log_message(message, log_file=session_file, console=args.verbosity)
    # only one fusion at present
    try:
        # we need the whole fields structure when exporting fields
        fusion = check_resource(fusion,
                                api.get_fusion,
                                query_string=ALL_FIELDS_QS,
                                raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a finished fusion: %s" % \
            str(exception))

    return fusion


def set_publish_fusion_args(args):
    """Set args to publish fusion

    """
    public_fusion = {}
    if args.public_fusion:
        public_fusion = {"private": False}
        if args.model_price:
            public_fusion.update(price=args.model_price)
        if args.cpp:
            public_fusion.update(credits_per_prediction=args.cpp)
    return public_fusion


def update_fusion(fusion, fusion_args, args,
                  api=None, path=None, session_file=None):
    """Updates fusion properties

    """
    if api is None:
        api = bigml.api.BigML()

    message = dated("Updating Fusion. %s\n" %
                    get_url(fusion))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    fusion = api.update_fusion(fusion, fusion_args)
    check_resource_error(fusion,
                         "Failed to update Fusion: %s"
                         % fusion['resource'])
    fusion = check_resource(fusion,
                            api.get_fusion,
                            query_string=FIELDS_QS,
                            raise_on_error=True)
    if is_shared(fusion):
        message = dated("Shared Fusion link. %s\n" %
                        get_url(fusion, shared=True))
        log_message(message, log_file=session_file, console=args.verbosity)
        if args.reports:
            report(args.reports, path, fusion)

    return fusion
