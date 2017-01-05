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
"""Centroid auxiliary functions

"""
from __future__ import absolute_import


import sys

import bigml.api

import bigmler.utils as u
import bigmler.checkpoint as c


from bigml.cluster import Cluster
from bigml.io import UnicodeWriter

from bigmler.tst_reader import TstReader as TestReader
from bigmler.resources import NORMAL_FORMAT, FULL_FORMAT
from bigmler.resources import create_batch_centroid

# symbol used in failing centroid predictions
NO_CENTROID = "-"


def use_prediction_headers(prediction_headers, output, test_reader,
                           fields, args):
    """Uses header information from the test file in the prediction output

       If --prediction-header is set, adds a headers row to the centroid
       prediction file.
       If --prediction-fields is used, retrieves the fields to exclude
       from the test input in the --prediction-info full format, that includes
       them all by default.

    """
    exclude = []
    headers = ["centroid name"]

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


def write_centroid(centroid_resource, output=sys.stdout,
                   prediction_info=NORMAL_FORMAT, input_data=None,
                   exclude=None):
    """Writes the final centroid prediction to the required output

       The format of the output depends on the `prediction_info` value.
       There's a brief format, that writes only the predicted value,
       and a full data format that writes first the input data
       used to predict followed by the centroid prediction.

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
    row.append(centroid_resource)
    try:
        output.writerow(row)
    except AttributeError:
        try:
            output.write(row)
        except AttributeError:
            raise AttributeError("You should provide a writeable object")


def centroid_to_row(centroid_resource):
    """Returns a csv row to store main centroid info in csv files.

    """
    return [centroid_resource['object']['centroid_name']]


def local_centroid(clusters, test_reader, output, args,
                   exclude=None):
    """Get local cluster and issue centroid prediction

    """
    # Only one cluster at present
    local_cluster = Cluster(clusters[0], api=args.retrieve_api_)
    test_set_header = test_reader.has_headers()
    for input_data in test_reader:
        input_data_dict = test_reader.dict(input_data, filtering=False)
        try:
            centroid_info = local_cluster.centroid(
                input_data_dict, by_name=test_set_header)
        except Exception:
            centroid_info = {'centroid_name': NO_CENTROID}
        write_centroid(centroid_info['centroid_name'], output,
                       args.prediction_info, input_data, exclude)


def centroid(clusters, fields, args, session_file=None):
    """Computes a centroid for each entry in the `test_set`.

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

        # Local centroids: Centroids are computed locally using clusters'
        # centroids distances
        message = u.dated("Creating local centroids.\n")
        u.log_message(message, log_file=session_file, console=args.verbosity)
        local_centroid(clusters, test_reader, output, args, exclude=exclude)
    test_reader.close()

def remote_centroid(cluster, test_dataset, batch_centroid_args, args,
                    api, resume, prediction_file=None, session_file=None,
                    path=None, log=None):
    """Computes a centroid for each entry in the `test_set`.

       Predictions are computed remotely using the batch centroid call.
    """

    cluster_id = bigml.api.get_cluster_id(cluster)
    # if resuming, try to extract dataset form log files
    if resume:
        message = u.dated("Batch centroid not found. Resuming.\n")
        resume, batch_centroid = c.checkpoint(
            c.is_batch_centroid_created, path, debug=args.debug,
            message=message, log_file=session_file, console=args.verbosity)
    if not resume:
        batch_centroid = create_batch_centroid(
            cluster_id, test_dataset, batch_centroid_args,
            args, api, session_file=session_file, path=path, log=log)
    if not args.no_csv:
        file_name = api.download_batch_centroid(batch_centroid,
                                                prediction_file)
        if file_name is None:
            sys.exit("Failed downloading CSV.")
    if args.to_dataset:
        batch_centroid = bigml.api.check_resource(batch_centroid, api=api)
        new_dataset = bigml.api.get_dataset_id(
            batch_centroid['object']['output_dataset_resource'])
        if new_dataset is not None:
            message = u.dated("Batch centroid dataset created: %s\n"
                              % u.get_url(new_dataset))
            u.log_message(message, log_file=session_file,
                          console=args.verbosity)
            u.log_created_resources("batch_centroid_dataset",
                                    path, new_dataset, mode='a')
