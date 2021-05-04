# -*- coding: utf-8 -*-
#
# Copyright 2020-2021 BigML
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
                           check_resource_error, log_created_resources)
from bigmler.reports import report

from bigmler.resourcesapi.common import set_basic_batch_args, map_fields, \
    update_json_args

from bigmler.resourcesapi.common import FULL_FORMAT


def set_batch_topic_distribution_args( \
    args, fields=None, dataset_fields=None):
    """Return batch topic distribution args dict

    """
    batch_topic_distribution_args = set_basic_batch_args(args, args.name)

    if args.fields_map_ and fields is not None:
        if dataset_fields is None:
            dataset_fields = fields
        batch_topic_distribution_args.update({
            "fields_map": map_fields(args.fields_map_,
                                     fields, dataset_fields)})

    if args.prediction_info == FULL_FORMAT:
        batch_topic_distribution_args.update(all_fields=True)
    if args.prediction_fields:
        batch_topic_distribution_args.update(all_fields=False)
        prediction_fields = []
        for field in args.prediction_fields.split(args.args_separator):
            field = field.strip()
            if not field in dataset_fields.fields:
                try:
                    field = dataset_fields.field_id(field)
                except Exception as exc:
                    sys.exit(exc)
            prediction_fields.append(field)
        batch_topic_distribution_args.update(output_fields=prediction_fields)
    if 'batch_topic_distribution' in args.json_args:
        update_json_args(
            batch_topic_distribution_args, args.json_args.get( \
                'batch_topic_distribution'), fields)

    return batch_topic_distribution_args


def create_batch_topic_distribution(topic_model, test_dataset,
                                    batch_topic_distribution_args, args,
                                    api=None, session_file=None,
                                    path=None, log=None):
    """Creates remote batch topic distribution

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Creating batch topic distribution.\n")
    log_message(message, log_file=session_file, console=args.verbosity)
    batch_topic_distribution = api.create_batch_topic_distribution( \
        topic_model, test_dataset, batch_topic_distribution_args, retries=None)
    log_created_resources( \
        "batch_topic_distribution", path,
        bigml.api.get_batch_topic_distribution_id(batch_topic_distribution),
        mode='a')
    batch_topic_distribution_id = check_resource_error(
        batch_topic_distribution,
        "Failed to create batch topic distribution: ")
    try:
        batch_topic_distribution = check_resource( \
            batch_topic_distribution, api.get_batch_topic_distribution,
            raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a finished batch topic distribution: %s"
                 % str(exception))
    message = dated("Batch topic distribution created: %s\n"
                    % get_url(batch_topic_distribution))
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % batch_topic_distribution_id, log_file=log)
    if args.reports:
        report(args.reports, path, batch_topic_distribution)
    return batch_topic_distribution
