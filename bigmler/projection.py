# -*- coding: utf-8 -*-
#
# Copyright 2019-2020 BigML
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
"""Linear regression prediction auxiliary functions

"""



import sys

import bigml.api

from bigml.pca import PCA
from bigml.io import UnicodeWriter

import bigmler.utils as u
import bigmler.checkpoint as c

from bigmler.tst_reader import TstReader as TestReader
from bigmler.resourcesapi.batch_projections import create_batch_projection


def use_projection_headers(projection_headers, output, test_reader,
                           fields, args, pca_headers):
    """Uses header information from the test file in the projection output

       If --projection-header is set, adds a headers row to the projection
       file.
       If --projection-fields is used, retrieves the fields to include
       in the projections output

    """
    exclude = []

    headers = []

    input_headers = []

    if args.projection_fields:

        if test_reader.has_headers():
            input_headers = test_reader.raw_headers[:]
        else:
            # if no headers are found in the test file we assume it has the
            # same model input_field structure
            input_headers = [fields[field]['name'] for field in
                             fields.fields_columns]
        if args.projection_fields not in [None, "all"]:
            projection_fields = [field.strip() for field in
                                 args.projection_fields.split(',')]
            # Filter input_headers adding only those chosen by the user
            number_of_headers = len(input_headers)
            for index in range(0, number_of_headers):
                if not input_headers[index] in projection_fields:
                    exclude.append(index)
            exclude = sorted(list(set(exclude)), reverse=True)
            for index in exclude:
                del input_headers[index]
            input_headers.extend(headers)

    input_headers.extend(pca_headers)

    headers = input_headers
    if projection_headers:
        output.writerow(headers)
    return exclude


def write_projection(projection, output=sys.stdout,
                     input_data=None,
                     exclude=None):
    """Writes the final projection to the required output

       The format of the output depends on the `prediction_info` value.
       There's a brief format, that writes only the predicted value,
       and a full data format that writes first the input data
       used to predict followed by the prediction.

    """

    row = []
    # input data is added if --projection-fields is used
    if input_data is None:
        input_data = []
    row = input_data
    if exclude and input_data:
        for index in exclude:
            del row[index]
    row.extend(projection)
    try:
        output.writerow(row)
    except AttributeError:
        try:
            output.write(row)
        except AttributeError:
            raise AttributeError("You should provide a writeable object")


def _local_pca(pca, args):
    """Create the local PCA object

    """
    local_pca = PCA(pca, api=args.retrieve_api_)
    kwargs = {}
    if args.max_components:
        kwargs.update({"max_components": args.max_components})
    if args.variance_threshold:
        kwargs.update({"variance_threshold": args.variance_threshold})
    return local_pca, kwargs


def local_projection(local_pca, kwargs, test_reader, output, args,
                     exclude=None):
    """Get local pca and issue projection

    """
    for input_data in test_reader:
        input_data_dict = test_reader.dict(input_data, filtering=False)
        projection_info = local_pca.projection(
            input_data_dict, **kwargs)
        write_projection( \
            projection_info,
            output,
            input_data if args.projection_fields is not None else None,
            exclude)


def projection(pca, fields, args, session_file=None):
    """Computes the projection
    for each entry in the `test_set`.

    """
    test_set = args.test_set
    test_set_header = args.test_header
    output = args.projections
    test_reader = TestReader(test_set, test_set_header, fields, None,
                             test_separator=args.test_separator)
    with UnicodeWriter(output, lineterminator="\n") as output:
        local_pca, kwargs = _local_pca(pca, args)
        pca_headers = ["PC%s" % (i + 1) for i in \
            range(0, len(local_pca.projection({})))]
        # columns to exclude if input_data is added to the projections field
        exclude = use_projection_headers(
            args.projection_header, output, test_reader, fields, args,
            pca_headers)
        # Local projection: Projections are computed locally
        message = u.dated("Creating local projections.\n")
        u.log_message(message, log_file=session_file, console=args.verbosity)
        local_projection(local_pca, kwargs, test_reader,
                         output, args, exclude=exclude)
    test_reader.close()


def remote_projection(pca, test_dataset,
                      batch_projection_args, args,
                      api, resume, projection_file=None, session_file=None,
                      path=None, log=None):
    """Computes a projection for each entry in the `test_set`.

       Projections are computed remotely using the batch projection call.
    """

    pca_id = bigml.api.get_pca_id(pca)
    # if resuming, try to extract dataset form log files
    if resume:
        message = u.dated("Batch projection not found. Resuming.\n")
        resume, batch_projection = c.checkpoint(
            c.is_batch_projection_created, path, debug=args.debug,
            message=message, log_file=session_file, console=args.verbosity)
    if not resume:
        batch_projection = create_batch_projection(
            pca_id, test_dataset, batch_projection_args,
            args, api, session_file=session_file, path=path, log=log)
    if not args.no_csv:
        file_name = api.download_batch_projection(batch_projection,
                                                  projection_file)
        if file_name is None:
            sys.exit("Failed downloading CSV.")
    if args.to_dataset:
        batch_projection = bigml.api.check_resource(batch_projection, api=api)
        new_dataset = bigml.api.get_dataset_id(
            batch_projection['object']['output_dataset_resource'])
        if new_dataset is not None:
            message = u.dated("Batch projection dataset created: %s\n"
                              % u.get_url(new_dataset))
            u.log_message(message, log_file=session_file,
                          console=args.verbosity)
            u.log_created_resources("batch_projection_dataset",
                                    path, new_dataset, mode='a')
