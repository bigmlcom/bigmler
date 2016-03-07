# -*- coding: utf-8 -*-
#
# Copyright 2014-2016 BigML
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

"""BigMLer - Resources processing: creation, update and retrieval of anomaly
   detectors

"""
from __future__ import absolute_import

import bigmler.utils as u
import bigmler.resources as r
import bigmler.checkpoint as c

from bigml.fields import Fields, DEFAULT_MISSING_TOKENS

def has_anomalies(args):
    """Returns whether some kind of anomaly detector is given

    """
    return args.anomaly or args.anomalies or args.anomaly_tag


def anomalies_processing(datasets, anomalies, anomaly_ids,
                         api, args, resume, fields=None,
                         session_file=None, path=None,
                         log=None):
    """Creates or retrieves anomalies from the command data

    """

    # If we have a dataset but not a model, we create the model if the no_model
    # flag hasn't been set up.
    if datasets and not (has_anomalies(args) or args.no_anomaly):
        anomaly_ids = []
        anomalies = []

        # Only 1 anomaly detector per bigmler command at present
        number_of_anomalies = 1
        if resume:
            resume, anomaly_ids = c.checkpoint(
                c.are_anomalies_created, path, number_of_anomalies,
                debug=args.debug)
            if not resume:
                message = u.dated("Found %s anomaly detectors out of %s."
                                  " Resuming.\n"
                                  % (len(anomaly_ids),
                                     number_of_anomalies))
                u.log_message(message, log_file=session_file,
                              console=args.verbosity)

            anomalies = anomaly_ids
            number_of_anomalies -= len(anomaly_ids)

        anomaly_args = r.set_anomaly_args(args,
                                          fields=fields,
                                          anomaly_fields=args.anomaly_fields_)
        anomalies, anomaly_ids = r.create_anomalies(datasets, anomalies,
                                                    anomaly_args, args, api,
                                                    path, session_file, log)

    # If an anomaly detector is provided, we use it.
    elif args.anomaly:
        anomaly_ids = [args.anomaly]
        anomalies = anomaly_ids[:]

    elif args.anomalies or args.anomaly_tag:
        anomalies = anomaly_ids[:]

    # If we are going to predict we must retrieve the anomalies
    if anomaly_ids and args.test_set:
        anomalies, anomaly_ids = r.get_anomalies(anomalies, args, api,
                                                 session_file)

    return anomalies, anomaly_ids, resume


def get_anomaly_fields(anomaly, csv_properties, args):
    """Retrieves fields info from anomaly resource

    """
    if not csv_properties:
        csv_properties = {}
    csv_properties.update(verbose=True)
    if args.user_locale is None:
        args.user_locale = anomaly['object'].get('locale', None)
    csv_properties.update(data_locale=args.user_locale)
    csv_properties.update(missing_tokens=DEFAULT_MISSING_TOKENS)
    return Fields(anomaly['object']['model']['fields'], **csv_properties)
