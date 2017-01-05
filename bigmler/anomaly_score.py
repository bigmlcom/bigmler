# -*- coding: utf-8 -*-
#
# Copyright 2014-2017 BigML
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
"""Anomaly score auxiliary functions

"""
from __future__ import absolute_import

import sys

import bigml.api

from bigml.anomaly import Anomaly
from bigml.io import UnicodeWriter


import bigmler.utils as u
import bigmler.checkpoint as c

from bigmler.tst_reader import TstReader as TestReader
from bigmler.resources import NORMAL_FORMAT, FULL_FORMAT
from bigmler.resources import create_batch_anomaly_score

# symbol used in failing anomaly score predictions
NO_ANOMALY_SCORE = "NaN"


def use_prediction_headers(prediction_headers, output, test_reader,
                           fields, args):
    """Uses header information from the test file in the prediction output

       If --prediction-header is set, adds a headers row to the anomaly score
       prediction file.
       If --prediction-fields is used, retrieves the fields to exclude
       from the test input in the --prediction-info full format, that includes
       them all by default.

    """
    exclude = []
    headers = ["anomaly score"]

    if (args.prediction_info == FULL_FORMAT or
            args.prediction_fields is not None):
        # Try to retrieve headers from the test file
        if test_reader.has_headers():
            input_headers = test_reader.raw_headers
        else:
            # if no headers are found in the test file we assume it has the
            # same model input_field structure removing the objective field
            input_headers = [fields[field]['name'] for field in
                             fields.fields_columns]

        if args.prediction_fields is not None:
            prediction_fields = map(str.strip,
                                    args.prediction_fields.split(','))
            # Filter input_headers adding only those chosen by the user
            number_of_headers = len(input_headers)
            for index in range(0, number_of_headers):
                if not input_headers[index] in prediction_fields:
                    exclude.append(index)
        exclude = sorted(list(set(exclude)), reverse=True)
        for index in exclude:
            del input_headers[index]
        input_headers.extend(headers)
        headers = input_headers
    if prediction_headers:
        output.writerow(headers)
    return exclude


def write_anomaly_score(anomaly_score_resource, output=sys.stdout,
                        prediction_info=NORMAL_FORMAT, input_data=None,
                        exclude=None):
    """Writes the final anomaly score prediction to the required output

       The format of the output depends on the `prediction_info` value.
       There's a brief format, that writes only the predicted value,
       and a full data format that writes first the input data
       used to predict followed by the anomaly score prediction.

    """

    row = []
    # input data is added if prediction format is BRIEF (no confidence) or FULL
    if prediction_info != NORMAL_FORMAT:
        if input_data is None:
            input_data = []
        row = input_data
        if exclude:
            for index in exclude:
                del row[index]
    row.append(anomaly_score_resource)
    try:
        output.writerow(row)
    except AttributeError:
        try:
            output.write(row)
        except AttributeError:
            raise AttributeError("You should provide a writeable object")


def anomaly_score_to_row(anomaly_score_resource):
    """Returns a csv row to store main anomaly score info in csv files.

    """
    return [anomaly_score_resource['object']['core']]


def local_anomaly_score(anomalies, test_reader, output, args,
                        exclude=None):
    """Get local anomaly detector and issue anomaly score prediction

    """
    # Only one anomaly detector at present
    local_anomaly = Anomaly(anomalies[0], api=args.retrieve_api_)
    test_set_header = test_reader.has_headers()
    for input_data in test_reader:
        input_data_dict = test_reader.dict(input_data, filtering=False)
        try:
            anomaly_score_info = {'score': local_anomaly.anomaly_score(
                input_data_dict, by_name=test_set_header)}
        except Exception:
            anomaly_score_info = {'score': NO_ANOMALY_SCORE}
        write_anomaly_score(anomaly_score_info['score'], output,
                            args.prediction_info, input_data, exclude)


def anomaly_score(anomalies, fields, args, session_file=None):
    """Computes an anomaly score for each entry in the `test_set`.

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
            args.prediction_header, output, test_reader, fields, args)

        # Local anomaly scores: Anomaly scores are computed locally using
        # the local anomaly detector method
        message = u.dated("Creating local anomaly scores.\n")
        u.log_message(message, log_file=session_file, console=args.verbosity)
        local_anomaly_score(anomalies, test_reader,
                            output, args, exclude=exclude)
    test_reader.close()


def remote_anomaly_score(anomaly, test_dataset, batch_anomaly_score_args, args,
                         api, resume, prediction_file=None, session_file=None,
                         path=None, log=None):
    """Computes an anomaly score for each entry in the `test_set`.

       Predictions are computed remotely using the batch anomaly score call.
    """

    anomaly_id = bigml.api.get_anomaly_id(anomaly)
    # if resuming, try to extract dataset form log files
    if resume:
        message = u.dated("Batch anomaly score not found. Resuming.\n")
        resume, batch_anomaly_score = c.checkpoint(
            c.is_batch_anomaly_score_created, path, debug=args.debug,
            message=message, log_file=session_file, console=args.verbosity)

    if not resume:
        batch_anomaly_score = create_batch_anomaly_score(
            anomaly_id, test_dataset, batch_anomaly_score_args,
            args, api, session_file=session_file, path=path, log=log)
    if not args.no_csv:
        file_name = api.download_batch_anomaly_score(batch_anomaly_score,
                                                     prediction_file)
        if file_name is None:
            sys.exit("Failed downloading CSV.")

    if args.to_dataset:
        batch_anomaly_score = bigml.api.check_resource(batch_anomaly_score,
                                                       api=api)
        new_dataset = bigml.api.get_dataset_id(
            batch_anomaly_score['object']['output_dataset_resource'])
        if new_dataset is not None:
            message = u.dated("Batch anomaly score dataset created: %s\n"
                              % u.get_url(new_dataset))
            u.log_message(message, log_file=session_file,
                          console=args.verbosity)
            u.log_created_resources("batch_anomaly_score_dataset",
                                    path, new_dataset, mode='a')
