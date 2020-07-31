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
                           check_resource_error, log_created_resources)
from bigmler.reports import report

from bigmler.resourcesapi.common import set_basic_batch_args, map_fields, \
    update_json_args


def set_batch_projection_args( \
    args, fields=None, dataset_fields=None):
    """Return batch projection args dict

    """
    batch_projection_args = set_basic_batch_args(args, args.name)

    if args.fields_map_ and fields is not None:
        if dataset_fields is None:
            dataset_fields = fields
        batch_projection_args.update({
            "fields_map": map_fields(args.fields_map_,
                                     fields, dataset_fields)})


    batch_projection_args.update(all_fields=False)

    if args.projection_fields:
        batch_projection_args.update(all_fields=True)
        projection_fields = []
        if args.projection_fields != "all":
            batch_projection_args.update(all_fields=True)
            for field in args.projection_fields.split(args.args_separator):
                field = field.strip()
                if not field in dataset_fields.fields:
                    try:
                        field = dataset_fields.field_id(field)
                    except ValueError as exc:
                        sys.exit(exc)
                projection_fields.append(field)
            batch_projection_args.update(output_fields=projection_fields)
    if 'batch_projection' in args.json_args:
        update_json_args(
            batch_projection_args, args.json_args.get( \
                'batch_projection'), fields)

    return batch_projection_args


def create_batch_projection(pca, test_dataset,
                            batch_projection_args, args,
                            api=None, session_file=None,
                            path=None, log=None):
    """Creates remote batch projection

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Creating batch projection.\n")
    log_message(message, log_file=session_file, console=args.verbosity)
    batch_projection = api.create_batch_projection( \
        pca, test_dataset, batch_projection_args, retries=None)
    log_created_resources( \
        "batch_projection", path,
        bigml.api.get_batch_projection_id(batch_projection), mode='a')
    batch_projection_id = check_resource_error(
        batch_projection,
        "Failed to create batch projection: ")
    try:
        batch_projection = check_resource( \
            batch_projection, api.get_batch_projection,
            raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a finished batch projection: %s"
                 % str(exception))
    message = dated("Batch projection created: %s\n"
                    % get_url(batch_projection))
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % batch_projection_id, log_file=log)
    if args.reports:
        report(args.reports, path, batch_projection)
    return batch_projection
