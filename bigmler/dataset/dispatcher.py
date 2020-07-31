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

"""BigMLer - cluster subcommand processing dispatching

"""


import sys
import os

import bigml.api
from bigml.fields import Fields

import bigmler.utils as u
import bigmler.labels as l
import bigmler.processing.args as a
import bigmler.processing.sources as ps
import bigmler.processing.datasets as pd

from bigmler.defaults import DEFAULTS_FILE
from bigmler.reports import clear_reports, upload_reports
from bigmler.command import get_context
from bigmler.prediction import OTHER
from bigmler.dispatcher import SESSIONS_LOG, clear_log_files

COMMAND_LOG = ".bigmler_dataset"
DIRS_LOG = ".bigmler_dataset_dir_stack"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]
MINIMUM_MODEL = "full=false"
DEFAULT_OUTPUT = "dataset.csv"

SETTINGS = {
    "command_log": COMMAND_LOG,
    "sessions_log": SESSIONS_LOG,
    "dirs_log": DIRS_LOG,
    "default_output": DEFAULT_OUTPUT,
    "defaults_file": DEFAULTS_FILE}


def dataset_dispatcher(args=sys.argv[1:]):
    """Parses command line and calls the different processing functions

    """

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        clear_log_files(LOG_FILES)

    command_args, _, api, session_file, resume = get_context(args,
                                                             SETTINGS)

    # Selects the action to perform
    if (a.has_train(command_args)
            or command_args.export_fields is not None):
        output_args = a.get_output_args(api, command_args, resume)
        compute_output(**output_args)
    u.log_message("_" * 80 + "\n", log_file=session_file)


def get_metadata(resource, key, default_value):
    """Retrieves from the user_metadata key in the resource the
       given key using default_value as a default

    """
    if ('object' in resource and 'user_metadata' in resource['object'] and
            key in resource['object']['user_metadata']):
        return resource['object']['user_metadata'][key]
    return default_value


def check_args_coherence(args):
    """Checks the given options for coherence and completitude

    """
    # It is compulsory to have a description to publish either datasets or
    # models
    if (not args.description_ and
            (args.black_box or args.white_box or args.public_dataset)):
        sys.exit("You should provide a description to publish.")

    # When using --max-categories, it is compulsory to specify also the
    # objective_field
    if args.max_categories > 0 and args.objective_field is None:
        sys.exit("When --max-categories is used, you must also provide the"
                 " --objective field name or column number")

    # When using --new-fields, it is compulsory to specify also a dataset
    # id
    if args.new_fields and not args.dataset:
        sys.exit("To use --new-fields you must also provide a dataset id"
                 " to generate the new dataset from it.")


def get_objective_id(args, fields):
    """Returns the objective id set by the user or the default

    """
    if args.objective_field is not None:
        try:
            objective_id = u.get_objective_id(fields, args.objective_field)
            fields.update_objective_field(
                fields.field_column_number(objective_id), True)
        except (KeyError, ValueError) as exc:
            sys.exit(exc)
    else:
        return fields.field_id(fields.objective_field)
    return objective_id


def compute_output(api, args):
    """ Creates a dataset using the `training_set`.

    """


    source = None
    dataset = None
    fields = None
    other_label = OTHER
    multi_label_data = None
    multi_label_fields = []
    datasets = None

    # variables from command-line options
    resume = args.resume_
    output = args.output

    check_args_coherence(args)
    path = u.check_dir(output)

    session_file = "%s%s%s" % (path, os.sep, SESSIONS_LOG)
    csv_properties = {}
    # If logging is required set the file for logging
    log = None
    if args.log_file:
        u.check_dir(args.log_file)
        log = args.log_file
        # If --clear_logs the log files are cleared
        clear_log_files([log])

    # labels to be used in multi-label expansion
    labels = (None if args.labels is None else
              [label.strip() for label in
               args.labels.split(args.args_separator)])
    if labels is not None:
        labels = sorted([label for label in labels])

    # multi_label file must be preprocessed to obtain a new extended file
    if args.multi_label and args.training_set is not None:
        (args.training_set, multi_label_data) = ps.multi_label_expansion(
            args.training_set, args.train_header, args, path,
            labels=labels, session_file=session_file)
        args.train_header = True
        args.objective_field = multi_label_data["objective_name"]
        all_labels = l.get_all_labels(multi_label_data)
        if not labels:
            labels = all_labels
    else:
        all_labels = labels
    if args.objective_field:
        csv_properties.update({'objective_field': args.objective_field})
    if args.source_file:
        # source is retrieved from the contents of the given local JSON file
        source, csv_properties, fields = u.read_local_resource(
            args.source_file,
            csv_properties=csv_properties)
    else:
        # source is retrieved from the remote object
        source, resume, csv_properties, fields = ps.source_processing(
            api, args, resume,
            csv_properties=csv_properties, multi_label_data=multi_label_data,
            session_file=session_file, path=path, log=log)
    if source is not None:
        args.source = bigml.api.get_source_id(source)
    if args.multi_label and source:
        multi_label_data = l.get_multi_label_data(source)
        (args.objective_field,
         labels,
         all_labels,
         multi_label_fields) = l.multi_label_sync(args.objective_field,
                                                  labels,
                                                  multi_label_data,
                                                  fields,
                                                  multi_label_fields)
    if fields and args.export_fields:
        fields.summary_csv(os.path.join(path, args.export_fields))
    if args.dataset_file:
        # dataset is retrieved from the contents of the given local JSON file
        model_dataset, csv_properties, fields = u.read_local_resource(
            args.dataset_file,
            csv_properties=csv_properties)
        if not args.datasets:
            datasets = [model_dataset]
            dataset = model_dataset
        else:
            datasets = u.read_datasets(args.datasets)
    if not datasets:
        # dataset is retrieved from the remote object
        datasets, resume, csv_properties, fields = pd.dataset_processing(
            source, api, args, resume,
            fields=fields,
            csv_properties=csv_properties,
            multi_label_data=multi_label_data,
            session_file=session_file, path=path, log=log)

    if datasets:
        dataset = datasets[-1]
        if args.to_csv is not None:
            resume = pd.export_dataset(dataset, api, args, resume,
                                       session_file=session_file, path=path)

        # Now we have a dataset, let's check if there's an objective_field
        # given by the user and update it in the fields structure
        args.objective_id_ = get_objective_id(args, fields)

    # If test_split is used, split the dataset in a training and a test dataset
    # according to the given split
    if args.test_split > 0:
        dataset, _, resume = pd.split_processing(
            dataset, api, args, resume,
            multi_label_data=multi_label_data,
            session_file=session_file, path=path, log=log)
        datasets[0] = dataset

    # Check if the dataset has a categorical objective field and it
    # has a max_categories limit for categories
    if args.max_categories > 0 and len(datasets) == 1:
        if pd.check_max_categories(fields.fields[args.objective_id_]):
            distribution = pd.get_categories_distribution(dataset,
                                                          args.objective_id_)
            if distribution and len(distribution) > args.max_categories:
                categories = [element[0] for element in distribution]
                other_label = pd.create_other_label(categories, other_label)
                datasets, resume = pd.create_categories_datasets(
                    dataset, distribution, fields, args,
                    api, resume, session_file=session_file, path=path, log=log,
                    other_label=other_label)
        else:
            sys.exit("The provided objective field is not categorical nor "
                     "a full terms only text field. "
                     "Only these fields can be used with"
                     "  --max-categories")

    # If any of the transformations is applied,
    # generate a new dataset from the given list of datasets
    if args.new_dataset:
        dataset, resume = pd.create_new_dataset(
            datasets, api, args, resume, fields=fields,
            session_file=session_file, path=path, log=log)
        datasets = [dataset]

    # Check if the dataset has a generators file associated with it, and
    # generate a new dataset with the specified field structure. Also
    # if the --to-dataset flag is used to clone or sample the original dataset
    if args.new_fields or args.sample_rate != 1 or \
            (args.lisp_filter or args.json_filter) and not a.has_source(args):
        if fields is None:
            if isinstance(dataset, str):
                dataset = u.check_resource(dataset, api=api)
            fields = Fields(dataset, csv_properties)
        args.objective_id_ = get_objective_id(args, fields)
        args.objective_name_ = fields.field_name(args.objective_id_)
        dataset, resume = pd.create_new_dataset(
            dataset, api, args, resume, fields=fields,
            session_file=session_file, path=path, log=log)
        datasets[0] = dataset
        # rebuild fields structure for new ids and fields
        csv_properties.update({'objective_field': args.objective_name_,
                               'objective_field_present': True})
        fields = pd.get_fields_structure(dataset, csv_properties)
        args.objective_id_ = get_objective_id(args, fields)
    if args.multi_label and dataset and multi_label_data is None:
        multi_label_data = l.get_multi_label_data(dataset)
        (args.objective_field,
         labels,
         all_labels,
         multi_label_fields) = l.multi_label_sync(args.objective_field,
                                                  labels,
                                                  multi_label_data,
                                                  fields, multi_label_fields)

    if dataset:
        # retrieves max_categories data, if any
        args.max_categories = get_metadata(dataset, 'max_categories',
                                           args.max_categories)
        other_label = get_metadata(dataset, 'other_label',
                                   other_label)
    if fields and args.export_fields:
        fields.summary_csv(os.path.join(path, args.export_fields))

    u.print_generated_files(path, log_file=session_file,
                            verbosity=args.verbosity)
    if args.reports:
        clear_reports(path)
        if args.upload:
            upload_reports(args.reports, path)
