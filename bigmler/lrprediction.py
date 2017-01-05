# -*- coding: utf-8 -*-
#
# Copyright 2016-2017 BigML
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
"""Logistic regression prediction auxiliary functions

"""
from __future__ import absolute_import


import sys

import bigml.api

from bigml.logistic import LogisticRegression
from bigml.io import UnicodeWriter

import bigmler.utils as u
import bigmler.checkpoint as c

from bigmler.tst_reader import TstReader as TestReader
from bigmler.resources import NORMAL_FORMAT, FULL_FORMAT
from bigmler.resources import create_batch_prediction
from bigmler.prediction import use_prediction_headers


def write_prediction(prediction, output=sys.stdout,
                     prediction_info=NORMAL_FORMAT, input_data=None,
                     exclude=None):
    """Writes the final prediction to the required output

       The format of the output depends on the `prediction_info` value.
       There's a brief format, that writes only the predicted value,
       and a full data format that writes first the input data
       used to predict followed by the prediction.

    """

    row = []
    # input data is added if prediction format is BRIEF (no probability) or
    # FULL
    if prediction_info != NORMAL_FORMAT:
        if input_data is None:
            input_data = []
        row = input_data
        if exclude:
            for index in exclude:
                del row[index]
    row.append(prediction.get('prediction'))
    if prediction_info in [NORMAL_FORMAT, FULL_FORMAT]:
        row.append(prediction.get('probability'))
    try:
        output.writerow(row)
    except AttributeError:
        try:
            output.write(row)
        except AttributeError:
            raise AttributeError("You should provide a writeable object")


def local_prediction(logistic_regressions, test_reader, output, args,
                     exclude=None):
    """Get local logistic_regression and issue prediction

    """
    # Only one logistic_regression at present
    local_logistic = LogisticRegression(logistic_regressions[0],
                                        api=args.retrieve_api_)
    test_set_header = test_reader.has_headers()
    for input_data in test_reader:
        input_data_dict = test_reader.dict(input_data, filtering=False)
        prediction_info = local_logistic.predict(
            input_data_dict, by_name=test_set_header)
        write_prediction(prediction_info, output,
                         args.prediction_info, input_data, exclude)


def lr_prediction(logistic_regressions, fields, args, session_file=None):
    """Computes a logistic regression prediction
    for each entry in the `test_set`.

    """
    test_set = args.test_set
    test_set_header = args.test_header
    output = args.predictions
    test_reader = TestReader(test_set, test_set_header, fields,
                             None,
                             test_separator=args.test_separator)
    with UnicodeWriter(output, lineterminator="\n") as output:
        # columns to exclude if input_data is added to the prediction field
        exclude = use_prediction_headers(
            args.prediction_header, output, test_reader, fields, args,
            args.objective_field, quality="probability")

        # Local predictions: Predictions are computed locally
        message = u.dated("Creating local predictions.\n")
        u.log_message(message, log_file=session_file, console=args.verbosity)
        local_prediction(logistic_regressions, test_reader,
                         output, args, exclude=exclude)
    test_reader.close()


def remote_lr_prediction(logistic_regression, test_dataset,
                         batch_prediction_args, args,
                         api, resume, prediction_file=None, session_file=None,
                         path=None, log=None):
    """Computes a prediction for each entry in the `test_set`.

       Predictions are computed remotely using the batch prediction call.
    """

    logistic_regression_id = bigml.api.get_logistic_regression_id( \
        logistic_regression)
    # if resuming, try to extract dataset form log files
    if resume:
        message = u.dated("Batch prediction not found. Resuming.\n")
        resume, batch_prediction = c.checkpoint(
            c.is_batch_prediction_created, path, debug=args.debug,
            message=message, log_file=session_file, console=args.verbosity)
    if not resume:
        batch_prediction = create_batch_prediction(
            logistic_regression_id, test_dataset, batch_prediction_args,
            args, api, session_file=session_file, path=path, log=log)
    if not args.no_csv:
        file_name = api.download_batch_prediction(batch_prediction,
                                                  prediction_file)
        if file_name is None:
            sys.exit("Failed downloading CSV.")
    if args.to_dataset:
        batch_prediction = bigml.api.check_resource(batch_prediction, api=api)
        new_dataset = bigml.api.get_dataset_id(
            batch_prediction['object']['output_dataset_resource'])
        if new_dataset is not None:
            message = u.dated("Batch prediction dataset created: %s\n"
                              % u.get_url(new_dataset))
            u.log_message(message, log_file=session_file,
                          console=args.verbosity)
            u.log_created_resources("batch_prediction_dataset",
                                    path, new_dataset, mode='a')
