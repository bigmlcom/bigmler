# -*- coding: utf-8 -*-
#
# Copyright 2014-2023 BigML
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


import os
import csv
from zipfile import ZipFile, ZIP_DEFLATED

import bigml.api

from bigml.fields import Fields
from bigml.util import bigml_locale

import bigmler.utils as u
import bigmler.resourcesapi.sources as r
import bigmler.checkpoint as c
import bigmler.processing.projects as pp
import bigmler.processing.annotations as an

from bigmler.processing.args import has_train, NOW
from bigmler.train_reader import TrainReader


def needs_source_update(args):
    """Checks whether the arguments passed need to be change at update time

    """
    return (args.field_attributes_ or args.types_ or args.user_locale
            or args.json_args.get('source') or args.import_fields or
            (hasattr(args, "add_sources") and args.add_sources_) or
            (hasattr(args, "sources") and args.sources_ is not None) or
            (hasattr(args, "sources_in") and args.sources_in is not None) or
            (hasattr(args, "remove_sources") and args.remove_sources_) or
            (hasattr(args, "delete_sources") and args.delete_sources_) or
            (hasattr(args, "close") and args.close is not None) or
            (hasattr(args, "row_components") and args.row_components) or
            (hasattr(args, "row_indices") and args.row_indices) or
            (hasattr(args, "row_values") and args.row_values))


def extract_source_name(path):
    """Tries to extract a name from the path to the data file"""
    try:
        path = path.replace(os.sep, "/")
        return path.split("/")[-1]
    except Exception:
        return "BigMLer_%s" % NOW


def test_source_processing(api, args, resume,
                           name=None, csv_properties=None,
                           session_file=None, path=None, log=None):
    """Creating or retrieving a test data source from input arguments

    """
    test_source = None
    fields = None
    if csv_properties is None:
        csv_properties = {}
    if args.test_set and args.remote:
        # If resuming, try to extract args.source form log files
        if resume:
            message = u.dated("Test source not found. Resuming.\n")
            resume, args.test_source = c.checkpoint(
                c.is_source_created, path, suffix="_test", debug=args.debug,
                message=message, log_file=session_file, console=args.verbosity)

        if not resume:
            # in case the test_set contains a directory full of images
            args.test_set, args = images_data_set(args.test_set,
                                                  args, session_file)
            if args.test_set and args.name is None:
                args.name = extract_source_name(args.test_set)
            source_args = r.set_source_args(args, name=name,
                                            data_set_header=args.test_header)
            test_source = r.create_source(args.test_set, source_args, args,
                                          api, path, session_file, log,
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
            if 'locale' in source_parser:
                csv_properties['data_locale'] = source_parser['locale']
                if (args.user_locale is not None and
                        bigml_locale(args.user_locale) ==
                        source_parser['locale']):
                    args.user_locale = None

        fields = Fields(test_source['object']['fields'], **csv_properties)

        if (args.field_attributes_ or args.types_ or args.user_locale
                or args.json_args.get('source')):
            # avoid updating project_id in source
            project_id, args.project_id = args.project_id, None
            test_source_args = r.set_source_args(args, fields=fields)
            test_source = r.update_source(test_source, test_source_args, args,
                                          api, session_file)
            args.project_id = project_id
            fields = Fields(test_source['object']['fields'], **csv_properties)

    return test_source, resume, csv_properties, fields


def images_data_set(data_set, args, session_file):
    """Adding images information when the data_set contains the images
    directory.

    """
    try:
        args.images_dir = None
        args.images_file = None
        if os.path.isdir(data_set):
            # When data_set is a directory, we assume it will contain images
            args.images_dir = data_set
        elif args.annotations_file:
            args.images_file = data_set

        if args.annotations_language is not None:
            data_set = an.bigml_coco_file(args, session_file)
        elif os.path.isdir(data_set) or args.images_file is not None:
            data_set = an.bigml_metadata(args)
    except TypeError:
        pass
    return data_set, args


def source_processing(api, args, resume,
                      csv_properties=None,
                      multi_label_data=None,
                      session_file=None, path=None, log=None):
    """Creating or retrieving a data source from input arguments

    """
    source = None
    fields = None
    if args.sources_in:
        args.sources_ = u.read_sources(args.sources)

    if (args.training_set or (
            hasattr(args, "evaluate") and args.evaluate and args.test_set)):
        # If resuming, try to extract args.source form log files

        if resume:
            message = u.dated("Source not found. Resuming.\n")
            resume, args.source = c.checkpoint(
                c.is_source_created, path, debug=args.debug, message=message,
                log_file=session_file, console=args.verbosity)

    # If neither a previous source, dataset or model are provided.
    # we create a new one. Also if --evaluate and test data are provided
    # we create a new dataset to test with.
    data_set, data_set_header = r.data_to_source(args)
    if data_set is not None:
        if args.name is None:
            args.name = extract_source_name(data_set)
        # Check if there's a created project for it
        args.project_id = pp.project_processing(
            api, args, resume, session_file=session_file, path=path, log=log)

        # If --annotations-language is used, the data_set can be a directory
        # that contains both images and annotation files that need to be
        # preprocessed
        data_set, args = images_data_set(data_set, args, session_file)
        source_args = r.set_source_args(
            args, multi_label_data=multi_label_data,
            data_set_header=data_set_header)
        source = r.create_source(
            data_set, source_args, args, api, path, session_file, log)

    # If a source is provided either through the command line or in resume
    # steps, we use it.
    elif args.source:
        source = bigml.api.get_source_id(args.source)
    elif args.sources_ is not None and not has_train(args):
        # if no data or source ID is provided and a list of sources
        # (which might even be empty e.g. --sources "")
        # is given, it creates a composite
        source_args = r.set_source_args(
            args, multi_label_data=multi_label_data,
            data_set_header=data_set_header)
        source = r.create_source(
            data_set, source_args, args, api, path, session_file, log)

    # If we already have source, we check that is finished , extract the
    # fields, and update them if needed.
    if source:
        source = r.get_source(source, api, args.verbosity, session_file)
        if 'source_parser' in source['object']:
            source_parser = source['object']['source_parser']
            if 'missing_tokens' in source_parser:
                csv_properties['missing_tokens'] = (
                    source_parser['missing_tokens'])
            if 'locale' in source_parser:
                csv_properties['data_locale'] = source_parser['locale']
                # No changes if user locale is the one in the source.
                if (args.user_locale is not None and
                        bigml_locale(args.user_locale) ==
                        source_parser['locale']):
                    args.user_locale = None
        fields = Fields(source['object'].get('fields', {}),
                        **csv_properties)
        if needs_source_update(args) or (data_set is None and args.images_file
                and args.annotations_file):
            if source["object"].get("closed", False):
                # need to clone the source to edit it
                source = r.clone_source(source, args, api, path,
                                        session_file, log)
            # avoid updating project_id in source
            project_id, args.project_id = args.project_id, None
            source_args = r.set_source_args(args, fields=fields, update=True)
            source = r.update_source(source, source_args, args, api,
                                     session_file)
            args.project_id = project_id
            fields = Fields(source['object'].get('fields', {}),
                            **csv_properties)

    return source, resume, csv_properties, fields


def multi_label_expansion(training_set, training_set_header,
                          args, output_path,
                          labels=None, session_file=None, input_flag=False):
    """Splitting the labels in a multi-label objective field to create
       a source with column per label

    """
    objective_field = args.objective_field
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
    with open(output_file, u.open_mode('w')) as output_handler:
        output = csv.writer(output_handler, lineterminator="\n")
        output.writerow(new_headers)
        # read to write new source file with column per label
        input_reader.reset()
        if training_set_header:
            input_reader.get_next()
        while True:
            try:
                row = input_reader.get_next(extended=True)
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

    input_reader.close()
    return (output_file, input_reader.get_multi_label_data())
