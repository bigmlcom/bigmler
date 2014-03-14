# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012-2014 BigML
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

"""BigMLer - Resources processing: creation, update and retrieval of sources

"""
from __future__ import absolute_import

import os
import csv
from zipfile import ZipFile, ZIP_DEFLATED

import bigml.api
import bigmler.utils as u
import bigmler.resources as r
import bigmler.checkpoint as c

from bigml.fields import Fields

from bigmler.train_reader import TrainReader

MONTECARLO_FACTOR = 200


def test_source_processing(test_set, test_set_header, api, args, resume,
                           name=None, description=None, csv_properties=None,
                           field_attributes=None, types=None,
                           session_file=None, path=None, log=None):
    """Creating or retrieving a test data source from input arguments

    """
    test_source = None
    fields = None
    if csv_properties is None:
        csv_properties = {}
    if (args.test_set and args.remote):
        # If resuming, try to extract args.source form log files
        if resume:
            message = u.dated("Test source not found. Resuming.\n")
            resume, args.test_source = c.checkpoint(
                c.is_source_created, path, suffix="_test", debug=args.debug,
                message=message, log_file=session_file, console=args.verbosity)

        if not resume:
            source_args = r.set_source_args(test_set_header, name, description,
                                            args)
            test_source = r.create_source(test_set, source_args, args, api,
                                          path, session_file, log,
                                          source_type="test")

    # If a source is provided either through the command line or in resume
    # steps, we use it.
    elif args.test_source:
        test_source = bigml.api.get_source_id(args.test_source)

    # If we already have source, we check that is finished, extract the
    # fields, and update them if needed.
    if test_source:
        test_source = r.get_source(test_source, api, args.verbosity,
                                   session_file)
        if 'source_parser' in test_source['object']:
            source_parser = test_source['object']['source_parser']
            if 'missing_tokens' in source_parser:
                csv_properties['missing_tokens'] = (
                    source_parser['missing_tokens'])
            if 'data_locale' in source_parser:
                csv_properties['data_locale'] = source_parser['locale']

        fields = Fields(test_source['object']['fields'], **csv_properties)
        if field_attributes:
            test_source = r.update_source_fields(test_source, field_attributes,
                                                 fields, api, args.verbosity,
                                                 session_file)
        if types:
            test_source = r.update_source_fields(test_source, types, fields,
                                                 api, args.verbosity,
                                                 session_file)
        if field_attributes or types:
            fields = Fields(test_source['object']['fields'], **csv_properties)

    return test_source, resume, csv_properties, fields


def source_processing(training_set, test_set, training_set_header,
                      test_set_header, api, args, resume,
                      name=None, description=None,
                      csv_properties=None, field_attributes=None, types=None,
                      multi_label_data=None,
                      session_file=None, path=None, log=None):
    """Creating or retrieving a data source from input arguments

    """
    source = None
    fields = None
    if (training_set or (args.evaluate and test_set)):
        # If resuming, try to extract args.source form log files

        if resume:
            message = u.dated("Source not found. Resuming.\n")
            resume, args.source = c.checkpoint(
                c.is_source_created, path, debug=args.debug, message=message,
                log_file=session_file, console=args.verbosity)

    # If neither a previous source, dataset or model are provided.
    # we create a new one. Also if --evaluate and test data are provided
    # we create a new dataset to test with.
    data_set, data_set_header = r.data_to_source(training_set, test_set,
                                                 training_set_header,
                                                 test_set_header, args)
    if data_set is not None:
        source_args = r.set_source_args(data_set_header, name, description,
                                        args,
                                        multi_label_data=multi_label_data)
        source = r.create_source(data_set, source_args, args, api,
                                 path, session_file, log)

    # If a source is provided either through the command line or in resume
    # steps, we use it.
    elif args.source:
        source = bigml.api.get_source_id(args.source)

    # If we already have source, we check that is finished, extract the
    # fields, and update them if needed.
    if source:
        source = r.get_source(source, api, args.verbosity, session_file)
        if 'source_parser' in source['object']:
            source_parser = source['object']['source_parser']
            if 'missing_tokens' in source_parser:
                csv_properties['missing_tokens'] = (
                    source_parser['missing_tokens'])
            if 'data_locale' in source_parser:
                csv_properties['data_locale'] = source_parser['locale']

        fields = Fields(source['object']['fields'], **csv_properties)
        if field_attributes:
            source = r.update_source_fields(source, field_attributes, fields,
                                            api, args.verbosity,
                                            session_file)
        if types:
            source = r.update_source_fields(source, types, fields, api,
                                            args.verbosity, session_file)
        if field_attributes or types:
            fields = Fields(source['object']['fields'], **csv_properties)

    return source, resume, csv_properties, fields


def multi_label_expansion(training_set, training_set_header, objective_field,
                          args, output_path,
                          labels=None, session_file=None, input_flag=False):
    """Splitting the labels in a multi-label objective field to create
       a source with column per label

    """
    input_reader = TrainReader(training_set, training_set_header,
                               objective_field, multi_label=True,
                               labels=labels,
                               label_separator=args.label_separator,
                               training_separator=args.training_separator,
                               multi_label_fields=args.multi_label_fields_list,
                               label_aggregates=args.label_aggregates_list,
                               objective=not input_flag)
    # read file to get all the different labels if no --labels flag is given
    # or use labels given in --labels and generate the new field names
    new_headers = input_reader.get_label_headers()

    try:
        file_name = os.path.basename(training_set)
    except AttributeError:
        file_name = "test_set.csv" if input_flag else "training_set.csv"
    output_file = "%s%sextended_%s" % (output_path, os.sep, file_name)
    message = u.dated("Transforming to extended source.\n")
    u.log_message(message, log_file=session_file,
                  console=args.verbosity)
    with open(output_file, 'w', 0) as output_handler:
        output = csv.writer(output_handler, lineterminator="\n")
        output.writerow(new_headers)
        # read to write new source file with column per label
        input_reader.reset()
        if training_set_header:
            input_reader.next()
        while True:
            try:
                row = input_reader.next(extended=True)
                output.writerow(row)
            except StopIteration:
                break

    # training sources are zipped to minimize upload time and resources
    if not input_flag:
        output_file_zip = "%s%sextended_%s.zip" % (output_path,
                                                   os.sep, file_name)
        with ZipFile(output_file_zip, 'w', ZIP_DEFLATED) as output_zipped_file:
            output_zipped_file.write(output_file, file_name)
        output_file = output_file_zip
        objective_field = input_reader.headers[input_reader.objective_column]

    return (output_file, input_reader.get_multi_label_data())
