# -*- coding: utf-8 -*-
#
# Copyright 2016-2020 BigML
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
"""Topic distribution auxiliary functions

"""



import sys

import bigml.api

from bigml.topicmodel import TopicModel
from bigml.io import UnicodeWriter

import bigmler.utils as u
import bigmler.checkpoint as c

from bigmler.tst_reader import TstReader as TestReader
from bigmler.resourcesapi.common import NORMAL_FORMAT, FULL_FORMAT
from bigmler.resourcesapi.batch_topic_distributions import \
    create_batch_topic_distribution

# symbol used in failing topic distribution
NO_DISTRIBUTION = "-"


def use_prediction_headers(test_reader, fields, args):
    """Uses header information from the test file in the prediction output

       If --prediction-fields is used, retrieves the fields to exclude
       from the test input in the --prediction-info full format, that includes
       them all by default.

    """
    exclude = []
    headers = []

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
            prediction_fields = list(map(str.strip,
                                    args.prediction_fields.split(',')))
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
    return exclude, headers


def write_topic_distribution(topic_distribution_resource, output=sys.stdout,
                             prediction_info=NORMAL_FORMAT, input_data=None,
                             exclude=None):
    """Writes the final topic distribution prediction to the required output

       The format of the output depends on the `prediction_info` value.
       There's a brief format, that writes only the predicted value,
       and a full data format that writes first the input data
       used to predict followed by the topic distribution.

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
    topic_probabilities = [topic['probability'] \
        for topic in topic_distribution_resource]
    row.extend(topic_probabilities)
    try:
        output.writerow(row)
    except AttributeError:
        try:
            output.write(row)
        except AttributeError:
            raise AttributeError("You should provide a writeable object")


def topic_distribution_to_row(topic_distribution_resource):
    """Returns a csv row to store main topic distribution info in csv files.

    """
    return [topic_distribution_resource['object']['topic_distribution']]


def local_topic_distribution(topic_models, test_reader, output, args,
                             exclude=None, headers=None):
    """Get local topic model and issue topic distribution prediction

    """
    # Only one topic model at present
    local_topic_model = TopicModel(topic_models[0], api=args.retrieve_api_)
    if args.prediction_header:
        headers.extend([topic['name'] for topic in local_topic_model.topics])
        output.writerow(headers)
    for input_data in test_reader:
        input_data_dict = test_reader.dict(input_data, filtering=False)
        try:
            topic_distribution_info = local_topic_model.distribution(
                input_data_dict)
        except Exception:
            topic_distribution_info = []
        write_topic_distribution(topic_distribution_info,
                                 output,
                                 args.prediction_info, input_data, exclude)


def topic_distribution(topic_models, fields, args, session_file=None):
    """Computes a topic distribution for each entry in the `test_set`.

    """
    test_set = args.test_set
    test_set_header = args.test_header
    output = args.predictions
    test_reader = TestReader(test_set, test_set_header, fields,
                             None,
                             test_separator=args.test_separator)
    with UnicodeWriter(output, lineterminator="\n") as output:
        # columns to exclude if input_data is added to the prediction field
        exclude, headers = use_prediction_headers(
            test_reader, fields, args)

        # Local topic distributions: Topic distributions are computed
        # locally using topic models'
        # method
        message = u.dated("Creating local topic distributions.\n")
        u.log_message(message, log_file=session_file, console=args.verbosity)
        local_topic_distribution(topic_models, test_reader, output,
                                 args, exclude=exclude, headers=headers)
    test_reader.close()

def remote_topic_distribution( \
    topic_model, test_dataset, batch_topic_distribution_args, args, \
    api, resume, prediction_file=None, session_file=None, \
    path=None, log=None):
    """Computes a topic distributioin for each entry in the `test_set`.

    Predictions are computed remotely using the batch topic distribution call.
    """

    topic_model_id = bigml.api.get_topic_model_id(topic_model)
    # if resuming, try to extract dataset form log files
    if resume:
        message = u.dated("Batch topic distribution not found. Resuming.\n")
        resume, batch_topic_distribution = c.checkpoint(
            c.is_batch_topic_distribution_created, path, debug=args.debug,
            message=message, log_file=session_file, console=args.verbosity)
    if not resume:
        batch_topic_distribution = create_batch_topic_distribution(
            topic_model_id, test_dataset, batch_topic_distribution_args,
            args, api, session_file=session_file, path=path, log=log)
    if not args.no_csv:
        file_name = api.download_batch_topic_distribution( \
            batch_topic_distribution,
            prediction_file)
        if file_name is None:
            sys.exit("Failed downloading CSV.")
    if args.to_dataset:
        batch_topic_distribution = bigml.api.check_resource( \
            batch_topic_distribution, api=api)
        new_dataset = bigml.api.get_dataset_id(
            batch_topic_distribution['object']['output_dataset_resource'])
        if new_dataset is not None:
            message = u.dated("Batch topic distribution dataset created: %s\n"
                              % u.get_url(new_dataset))
            u.log_message(message, log_file=session_file,
                          console=args.verbosity)
            u.log_created_resources("batch_topic_distribution_dataset",
                                    path, new_dataset, mode='a')
