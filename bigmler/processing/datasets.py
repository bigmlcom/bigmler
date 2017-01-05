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

"""BigMLer - Resources processing: creation, update and retrieval of datasets

"""
from __future__ import absolute_import

import sys
import re
import os

import bigml.api

from bigml.fields import Fields
from bigml.predicate import TM_FULL_TERM

import bigmler.utils as u
import bigmler.resources as r
import bigmler.checkpoint as c

from bigmler.prediction import OTHER


MAX_CATEGORIES_RE = re.compile(r'max_categories: (\d+)')


def create_other_label(categories, label):
    """Creates a label that is not amongst the categories list

    """
    if not label in categories:
        return label
    return create_other_label(categories, "*%s*" % label)


def check_max_categories(field):
    """Checks if a field can be split by --max-categories.

       Only categorical or full terms only text are allowed.

    """
    return field['optype'] == 'categorical' or (
        field['optype'] == 'text' and
        field['term_analysis']['token_mode'] == TM_FULL_TERM)


def get_categories_distribution(dataset, objective_id):
    """Returns the categories distribution in a categorical dataset

    """
    try:
        dataset_info = dataset.get('object', [])
        if dataset_info['objective_field']['optype'] == 'categorical':
            if 'distribution' in dataset_info:
                distribution = dataset_info['distribution']
            elif 'objective_summary' in dataset_info:
                summary = dataset_info['objective_summary']
                if 'categories' in summary:
                    distribution = summary['categories']
            else:
                summary = dataset_info['fields'][objective_id]['summary']
                if 'categories' in summary:
                    distribution = summary['categories']
            return distribution
        elif dataset_info['objective_field']['optype'] == 'text':
            summary = dataset_info['fields'][objective_id]['summary']
            if 'tag_cloud' in summary:
                distribution = summary['tag_cloud']
            return distribution
        else:
            return []
    except KeyError:
        return []


def get_fields_structure(resource, csv_properties):
    """Builds a Fields object from the fields information in the resource

    """
    if not csv_properties and 'locale' in resource['object']:
        csv_properties = {
            'data_locale': resource['object']['locale']}
    fields = Fields(resource['object']['fields'], **csv_properties)
    return fields


def get_new_objective(fields, objective):
    """Checks if the objective given by the user in the --objective flag
       differs from the one in the dataset. Returns the new objective or None
       if they are the same.

    """
    if objective is None:
        return None
    try:
        objective_id = fields.field_id(objective)
    except ValueError, exc:
        sys.exit(exc)
    if fields.objective_field == fields.field_column_number(objective_id):
        return None
    return objective


def csv_name(user_filename, path, dataset):
    """Building CSV exported dataset filename from the user-given value

    """
    if user_filename == '':
        dataset_id = bigml.api.get_dataset_id(dataset)
        if dataset_id:
            return os.path.join(path,
                                "%s.csv" % dataset_id.replace("/", "_"))
    return os.path.join(path, user_filename)


def check_dataset_update(args, dataset):
    """Checks if the dataset information must be updated.

    """
    return (args.dataset_attributes or
            args.import_fields or
            (args.shared_flag and r.shared_changed(args.shared, dataset)) or
            (((hasattr(args, 'max_categories') and args.max_categories > 0) or
              (hasattr(args, 'multi_label') and args.multi_label)) and
             args.objective_field))


def dataset_processing(source, api, args, resume,
                       fields=None,
                       csv_properties=None,
                       multi_label_data=None,
                       session_file=None, path=None, log=None):
    """Creating or retrieving dataset from input arguments

    """
    datasets = []
    dataset = None
    if (args.training_set or args.source or (
            hasattr(args, "evaluate") and args.evaluate and args.test_set)):
        # if resuming, try to extract args.dataset form log files
        if resume:
            message = u.dated("Dataset not found. Resuming.\n")
            resume, args.dataset = c.checkpoint(
                c.is_dataset_created, path, debug=args.debug, message=message,
                log_file=session_file, console=args.verbosity)

    # If we have a source but no dataset or model has been provided, we
    # create a new dataset if the no_dataset option isn't set up. Also
    # if evaluate is set and test_set has been provided.
    if ((source and not args.has_datasets_ and not args.has_models_
         and not args.no_dataset) or
            (hasattr(args, "evaluate") and args.evaluate and
             args.test_set and not args.dataset)):
        dataset_args = r.set_dataset_args(args, fields,
                                          multi_label_data=multi_label_data)
        dataset = r.create_dataset(source, dataset_args, args, api,
                                   path, session_file, log)

    # If a dataset is provided, let's retrieve it.
    elif args.dataset:
        dataset = bigml.api.get_dataset_id(args.dataset)

    # If set of datasets is provided, let's check their ids.
    elif args.dataset_ids:
        for i in range(0, len(args.dataset_ids)):
            datasets.append(bigml.api.get_dataset_id(args.dataset_ids[i]))
        dataset = datasets[0]

    # If we already have a dataset, we check the status and get the fields if
    # we hadn't them yet.
    if dataset:
        dataset = r.get_dataset(dataset, api, args.verbosity, session_file)

        if ('object' in dataset and 'objective_field' in dataset['object'] and
                'column_number' in dataset['object']['objective_field']):
            dataset_objective = dataset[
                'object']['objective_field']['column_number']
            csv_properties.update(objective_field=dataset_objective,
                                  objective_field_present=True)

        fields = get_fields_structure(dataset, csv_properties)

        if args.public_dataset:
            r.publish_dataset(dataset, args, api, session_file)

        if hasattr(args, 'objective_field'):
            new_objective = get_new_objective(fields, args.objective_field)
        else:
            new_objective = None
        updated = False
        # We'll update the dataset if
        #  the flag --dataset_attributes is used
        #  the --multi-label flag is used and there's an --objective-field
        #  the --max-categories flag is used and there's an --objective-field
        #  the --impor-fields flag is used
        if check_dataset_update(args, dataset):
            dataset_args = r.set_dataset_args(args, fields)
            if args.shared_flag and r.shared_changed(args.shared, dataset):
                dataset_args.update(shared=args.shared)
            dataset = r.update_dataset(dataset, dataset_args, args,
                                       api=api, path=path,
                                       session_file=session_file)
            dataset = r.get_dataset(dataset, api, args.verbosity, session_file)
            updated = True
        if new_objective is not None:
            csv_properties.update(objective_field=args.objective_field,
                                  objective_field_present=True)
            updated = True
        if updated:
            fields = Fields(dataset['object']['fields'], **csv_properties)
        if not datasets:
            datasets = [dataset]
        else:
            datasets[0] = dataset
    return datasets, resume, csv_properties, fields


def alternative_dataset_processing(dataset_or_source, suffix, dataset_args,
                                   api, args, resume,
                                   session_file=None, path=None, log=None):
    """Creates a dataset. Used in splits to generate train and test datasets

    """
    alternative_dataset = None
    # if resuming, try to extract dataset form log files
    if resume:
        message = u.dated("Dataset not found. Resuming.\n")
        resume, alternative_dataset = c.checkpoint(
            c.is_dataset_created, path, "_%s" % suffix, debug=args.debug,
            message=message, log_file=session_file, console=args.verbosity)

    if alternative_dataset is None:
        alternative_dataset = r.create_dataset(
            dataset_or_source, dataset_args, args, api, path,
            session_file, log, suffix)
        if alternative_dataset:
            alternative_dataset = r.get_dataset(
                alternative_dataset, api, args.verbosity, session_file)
    return alternative_dataset, resume


def split_processing(dataset, api, args, resume,
                     multi_label_data=None, session_file=None,
                     path=None, log=None):
    """Splits a dataset into train and test datasets

    """
    train_dataset = None
    test_dataset = None
    sample_rate = 1 - args.test_split
    dataset_alternative_args = r.set_dataset_split_args(
        "%s - train (%s %%)" % (
            args.name, int(sample_rate * 100)),
        args.description_, args, sample_rate,
        out_of_bag=False,
        multi_label_data=multi_label_data)
    train_dataset, resume = alternative_dataset_processing(
        dataset, "train", dataset_alternative_args, api, args,
        resume, session_file=session_file, path=path, log=log)
    dataset_alternative_args = r.set_dataset_split_args(
        "%s - test (%s %%)" % (
            args.name, int(args.test_split * 100)),
        args.description_, args,
        sample_rate, out_of_bag=True, multi_label_data=multi_label_data)
    test_dataset, resume = alternative_dataset_processing(
        dataset, "test", dataset_alternative_args, api, args,
        resume, session_file=session_file, path=path, log=log)

    return train_dataset, test_dataset, resume


def create_categories_datasets(dataset, distribution,
                               fields, args, api, resume,
                               session_file=None, path=None, log=None,
                               other_label=OTHER):
    """Generates a new dataset using a subset of categories of the original one

    """

    if args.max_categories < 1:
        sys.exit("--max-categories can only be a positive number.")
    datasets = []
    categories_splits = [distribution[i: i + args.max_categories] for i
                         in range(0, len(distribution), args.max_categories)]
    number_of_datasets = len(categories_splits)

    if resume:
        resume, datasets = c.checkpoint(
            c.are_datasets_created, path, number_of_datasets,
            debug=args.debug)
        if not resume:
            message = u.dated("Found %s datasets out of %s. Resuming.\n"
                              % (len(datasets),
                                 number_of_datasets))
            u.log_message(message, log_file=session_file,
                          console=args.verbosity)
    if not resume:
        for i in range(len(datasets), number_of_datasets):
            split = categories_splits[i]
            category_selector = "(if (or"
            for element in split:
                category = element[0]
                category_selector += " (= v \"%s\")" % category
            category_selector += ") v \"%s\")" % other_label
            category_generator = "(let (v (f %s)) %s)" % (
                fields.objective_field, category_selector)
            try:
                dataset_args = {
                    "all_but": [fields.objective_field],
                    "new_fields": [
                        {"name": fields.field_name(fields.objective_field),
                         "field": category_generator,
                         "label": "max_categories: %s" % args.max_categories}],
                    "user_metadata":
                    {"max_categories": args.max_categories,
                     "other_label": other_label}}
            except ValueError, exc:
                sys.exit(exc)
            new_dataset = r.create_dataset(
                dataset, dataset_args, args, api=api, path=path,
                session_file=session_file, log=log, dataset_type="parts")
            new_dataset = bigml.api.check_resource(new_dataset,
                                                   api.get_dataset)
            datasets.append(new_dataset)
    return datasets, resume


def create_new_dataset(datasets, api, args, resume, fields=None,
                       session_file=None, path=None, log=None):
    """Generates a new dataset using the generators given in a generators file
       or a multi-dataset from a list of datasets

    """
    origin_resource = datasets
    if not isinstance(datasets, basestring) and args.multi_dataset:
        suffix = "multi"
    else:
        datasets = []
        suffix = "gen"
    number_of_datasets = 1
    if resume:
        resume, datasets = c.checkpoint(
            c.are_datasets_created, path, number_of_datasets,
            debug=args.debug, suffix=suffix)
        if not resume:
            message = u.dated("Found %s datasets out of %s. Resuming.\n"
                              % (len(datasets),
                                 number_of_datasets))
            u.log_message(message, log_file=session_file,
                          console=args.verbosity)
    if not resume:
        dataset_args = r.set_dataset_args(args, fields)
        if args.multi_dataset and args.multi_dataset_json:
            dataset_args.update(args.multi_dataset_json)
        elif hasattr(args, 'anomalies_dataset') and args.anomalies_dataset:
            dataset_args.update({'lisp_filter': args.anomaly_filter_})
        elif hasattr(args, 'lisp_filter') and args.lisp_filter:
            dataset_args.update({'lisp_filter': args.lisp_filter})
        elif hasattr(args, 'json_filter') and args.json_filter:
            dataset_args.update({'json_filter': args.json_filter})
        else:
            dataset_args.update(args.dataset_json_generators)
        new_dataset = r.create_dataset(origin_resource, dataset_args,
                                       args,
                                       api=api, path=path,
                                       session_file=session_file,
                                       log=log, dataset_type=suffix)
    else:
        new_dataset = datasets[0]
    return new_dataset, resume


def export_dataset(dataset, api, args, resume,
                   session_file=None, path=None):
    """Exports the dataset to a CSV file given by the user or a filename
       based on the dataset id by default.

    """
    filename = csv_name(args.to_csv, path, dataset)
    if resume:
        resume = c.checkpoint(
            c.is_dataset_exported, filename,
            debug=args.debug)
        if not resume:
            message = u.dated("No dataset exported. Resuming.\n")
            u.log_message(message, log_file=session_file,
                          console=args.verbosity)
    else:
        message = u.dated("Exporting dataset to CSV file: %s\n" % filename)
        u.log_message(message, log_file=session_file,
                      console=args.verbosity)

    if not resume:
        file_name = api.download_dataset(dataset, filename=filename)
        if file_name is None:
            sys.exit("Failed downloading CSV.")
    return resume
