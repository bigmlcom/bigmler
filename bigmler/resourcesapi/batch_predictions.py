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

from bigmler.resourcesapi.common import FULL_FORMAT, NORMAL_FORMAT, \
    THRESHOLD_CODE



def set_batch_prediction_args(args, fields=None,
                              dataset_fields=None):
    """Return batch prediction args dict

    """
    batch_prediction_args = set_basic_batch_args(args, args.name)

    if hasattr(args, 'method') and args.method:
        batch_prediction_args.update({"combiner": args.method})
        if args.method == THRESHOLD_CODE:
            threshold = {}
            if hasattr(args, 'threshold') and args.threshold is not None:
                threshold.update(k=args.threshold)
            if hasattr(args, 'threshold_class') \
                    and args.threshold_class is not None:
                threshold.update({"class": args.threshold_class})
            batch_prediction_args.update(threshold=threshold)
    if args.fields_map_ and fields is not None:
        if dataset_fields is None:
            dataset_fields = fields
        batch_prediction_args.update({
            "fields_map": map_fields(args.fields_map_,
                                     fields, dataset_fields)})

    if args.prediction_info in [NORMAL_FORMAT, FULL_FORMAT]:
        if (hasattr(args, 'boosting') and args.boosting) or \
                (hasattr(args, 'probability') and args.probability):
            batch_prediction_args.update(probability=True)
        else:
            batch_prediction_args.update(confidence=True)

    if args.prediction_info == FULL_FORMAT:
        batch_prediction_args.update(all_fields=True)
        if hasattr(args, 'prediction_name') and args.prediction_name:
            batch_prediction_args.update(prediction_name=args.prediction_name)
    if args.prediction_fields:
        batch_prediction_args.update(all_fields=False)
        prediction_fields = []
        for field in args.prediction_fields.split(args.args_separator):
            field = field.strip()
            if not field in dataset_fields.fields:
                try:
                    field = dataset_fields.field_id(field)
                except ValueError as exc:
                    sys.exit(exc)
            prediction_fields.append(field)
        batch_prediction_args.update(output_fields=prediction_fields)
    if hasattr(args, 'missing_strategy') and args.missing_strategy:
        batch_prediction_args.update(missing_strategy=args.missing_strategy)
    if hasattr(args, "operating_point_") and args.operating_point_:
        batch_prediction_args.update(operating_point=args.operating_point_)
        if args.operating_point_.get("kind") == "probability":
            batch_prediction_args.update({"probability": True,
                                          "confidence": False})

    if 'batch_prediction' in args.json_args:
        update_json_args(
            batch_prediction_args,
            args.json_args.get('batch_prediction'),
            fields)
    return batch_prediction_args


def create_batch_prediction(model_or_ensemble, test_dataset,
                            batch_prediction_args, args,
                            api=None, session_file=None,
                            path=None, log=None):
    """Creates remote batch_prediction

    """
    if api is None:
        api = bigml.api.BigML()

    message = dated("Creating batch prediction.\n")
    log_message(message, log_file=session_file, console=args.verbosity)
    batch_prediction = api.create_batch_prediction(model_or_ensemble,
                                                   test_dataset,
                                                   batch_prediction_args,
                                                   retries=None)
    log_created_resources("batch_prediction", path,
                          bigml.api.get_batch_prediction_id(batch_prediction),
                          mode='a')
    batch_prediction_id = check_resource_error(
        batch_prediction, "Failed to create batch prediction: ")
    try:
        batch_prediction = check_resource(batch_prediction,
                                          api.get_batch_prediction,
                                          raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a finished batch prediction: %s"
                 % str(exception))
    message = dated("Batch prediction created: %s\n"
                    % get_url(batch_prediction))
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % batch_prediction_id, log_file=log)
    if args.reports:
        report(args.reports, path, batch_prediction)
    return batch_prediction
