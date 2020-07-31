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

from bigmler.resourcesapi.common import SEED, \
    FIELDS_QS, ALL_FIELDS_QS
from bigmler.resourcesapi.common import set_basic_model_args, \
    configure_input_fields, update_sample_parameters_args, update_json_args, \
    wait_for_available_tasks

def set_anomaly_args(args, name=None, fields=None, anomaly_fields=None):
    """Return anomaly arguments dict

    """
    if name is None:
        name = args.name
    if anomaly_fields is None:
        anomaly_fields = args.anomaly_fields_

    anomaly_args = set_basic_model_args(args, name)
    anomaly_args.update({
        "seed": SEED if args.seed is None else args.seed,
        "anomaly_seed": (SEED if args.anomaly_seed is None
                         else args.anomaly_seed)
    })

    if anomaly_fields and fields is not None:
        input_fields = configure_input_fields(fields, anomaly_fields)
        anomaly_args.update(input_fields=input_fields)

    if args.top_n > 0:
        anomaly_args.update(top_n=args.top_n)
    if args.forest_size > 0:
        anomaly_args.update(forest_size=args.forest_size)

    anomaly_args = update_sample_parameters_args(anomaly_args, args)

    if 'anomaly' in args.json_args:
        update_json_args(anomaly_args, args.json_args.get('anomaly'), fields)

    return anomaly_args


def set_publish_anomaly_args(args):
    """Set args to publish anomaly

    """
    public_anomaly = {}
    if args.public_anomaly:
        public_anomaly = {"private": False}
        if args.model_price:
            public_anomaly.update(price=args.model_price)
        if args.cpp:
            public_anomaly.update(credits_per_prediction=args.cpp)
    return public_anomaly


def create_anomalies(datasets, anomaly_ids, anomaly_args,
                     args, api=None, path=None,
                     session_file=None, log=None):
    """Create remote anomalies

    """
    if api is None:
        api = bigml.api.BigML()

    anomalies = anomaly_ids[:]
    existing_anomalies = len(anomalies)
    anomaly_args_list = []
    datasets = datasets[existing_anomalies:]
    # if resuming and all anomalies were created,
    # there will be no datasets left
    if datasets:
        if isinstance(anomaly_args, list):
            anomaly_args_list = anomaly_args

        # Only one anomaly per command, at present
        number_of_anomalies = 1
        message = dated("Creating %s.\n" %
                        plural("anomaly detector", number_of_anomalies))
        log_message(message, log_file=session_file,
                    console=args.verbosity)

        query_string = FIELDS_QS
        inprogress = []
        for i in range(0, number_of_anomalies):
            wait_for_available_tasks(inprogress, args.max_parallel_anomalies,
                                     api, "anomaly")
            if anomaly_args_list:
                anomaly_args = anomaly_args_list[i]

            anomaly = api.create_anomaly(datasets, anomaly_args, retries=None)
            anomaly_id = check_resource_error(anomaly,
                                              "Failed to create anomaly: ")
            log_message("%s\n" % anomaly_id, log_file=log)
            anomaly_ids.append(anomaly_id)
            inprogress.append(anomaly_id)
            anomalies.append(anomaly)
            log_created_resources("anomalies", path, anomaly_id, mode='a')

        if args.verbosity:
            if bigml.api.get_status(anomaly)['code'] != bigml.api.FINISHED:
                try:
                    anomaly = check_resource(anomaly, api.get_anomaly,
                                             query_string=query_string,
                                             raise_on_error=True)
                except Exception as exception:
                    sys.exit("Failed to get a finished anomaly: %s" %
                             str(exception))
                anomalies[0] = anomaly
            message = dated("Anomaly created: %s\n" %
                            get_url(anomaly))
            log_message(message, log_file=session_file,
                        console=args.verbosity)
            if args.reports:
                report(args.reports, path, anomaly)

    return anomalies, anomaly_ids


def get_anomalies(anomaly_ids, args, api=None, session_file=None):
    """Retrieves remote anomalies in its actual status

    """
    if api is None:
        api = bigml.api.BigML()
    anomaly_id = ""
    anomalies = anomaly_ids
    anomaly_id = anomaly_ids[0]
    message = dated("Retrieving %s. %s\n" %
                    (plural("anomaly detector", len(anomaly_ids)),
                     get_url(anomaly_id)))
    log_message(message, log_file=session_file, console=args.verbosity)
    # only one anomaly to predict at present
    try:
        # we need the whole fields structure when exporting fields
        query_string = FIELDS_QS if not args.export_fields else ALL_FIELDS_QS
        anomaly = check_resource(anomaly_ids[0], api.get_anomaly,
                                 query_string=query_string,
                                 raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a finished anomaly: %s" % str(exception))
    anomalies[0] = anomaly

    return anomalies, anomaly_ids


def update_anomaly(anomaly, anomaly_args, args,
                   api=None, path=None, session_file=None):
    """Updates anomaly properties

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Updating anomaly detector. %s\n" %
                    get_url(anomaly))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    anomaly = api.update_anomaly(anomaly, anomaly_args)
    check_resource_error(anomaly, "Failed to update anomaly: %s"
                         % anomaly['resource'])
    anomaly = check_resource(anomaly, api.get_anomaly,
                             query_string=FIELDS_QS,
                             raise_on_error=True)
    if is_shared(anomaly):
        message = dated("Shared anomaly link. %s\n" %
                        get_url(anomaly, shared=True))
        log_message(message, log_file=session_file, console=args.verbosity)
        if args.reports:
            report(args.reports, path, anomaly)

    return anomaly
