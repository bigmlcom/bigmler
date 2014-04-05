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

"""BigMLer - Resources processing: creation, update and retrieval of datasets

"""
from __future__ import absolute_import

import sys
import re

import bigml.api
import bigmler.utils as u
import bigmler.resources as r
import bigmler.checkpoint as c

from bigml.fields import Fields
from bigml.predicate import TM_FULL_TERM

from bigmler.prediction import OTHER
from bigmler.processing.models import has_models


MAX_CATEGORIES_RE = re.compile("max_categories: (\d+)")


def has_datasets(args):
    """Returns if some kind of dataset id is given in args.

    """
    return args.dataset or args.datasets or args.dataset_tag


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
    return field['optype'] == 'categorical' or (field['optype'] == 'text' and
        field['term_analysis']['token_mode'] == TM_FULL_TERM)


def get_categories_distribution(dataset, objective_id):
    """Returns the categories distribution in a categorical dataset

    """
    try:
        dataset_info = dataset.get('object', [])
        if dataset_info['objective_field']['optype'] == 'categorical':
            if 'distribution' in dataset_info:
                distribution = dataset_info['distribution']
            elif ('objective_summary' in dataset_info):
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


def get_new_objective(fields, objective, dataset):
    """Checks if the objective given by the user in the --objective flag
       differs from the one in the dataset. Returns the new objective or None
       if they are the same.

    """
    if objective is None:
        return None
    objective_id = fields.field_id(objective)
    if fields.objective_field == fields.field_column_number(objective_id):
        return None
    return objective


def dataset_processing(source, training_set, test_set, fields, objective_field,
                       api, args, resume,  name=None, description=None,
                       dataset_fields=None, multi_label_data=None,
                       csv_properties=None,
                       session_file=None, path=None, log=None):
    """Creating or retrieving dataset from input arguments

    """
    datasets = []
    dataset = None
    if (training_set or args.source or (args.evaluate and test_set)):
        # if resuming, try to extract args.dataset form log files
        if resume:
            message = u.dated("Dataset not found. Resuming.\n")
            resume, args.dataset = c.checkpoint(
                c.is_dataset_created, path, debug=args.debug, message=message,
                log_file=session_file, console=args.verbosity)

    # If we have a source but no dataset or model has been provided, we
    # create a new dataset if the no_dataset option isn't set up. Also
    # if evaluate is set and test_set has been provided.
    if ((source and not has_datasets(args) and not has_models(args)
         and not args.no_dataset) or
            (args.evaluate and args.test_set and not args.dataset)):
        dataset_args = r.set_dataset_args(name, description, args, fields,
                                          dataset_fields,
                                          objective_field=objective_field,
                                          multi_label_data=multi_label_data)
        dataset = r.create_dataset(source, dataset_args, args.verbosity, api,
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

        new_objective = get_new_objective(fields, args.objective_field,
                                          dataset)

        if (new_objective is not None or args.dataset_attributes):
            dataset_args = r.set_dataset_args(name, description, args, fields,
                                              dataset_fields, objective_field)
            dataset = r.update_dataset(dataset, dataset_args, args.verbosity,
                                       api=api, session_file=session_file)
            dataset = r.get_dataset(dataset, api, args.verbosity, session_file)
            csv_properties.update(objective_field=objective_field,
                                  objective_field_present=True)
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
            dataset_or_source, dataset_args, args.verbosity, api, path,
            session_file, log, suffix)
        if alternative_dataset:
            alternative_dataset = r.get_dataset(
                alternative_dataset, api, args.verbosity, session_file)
    return alternative_dataset, resume


def split_processing(dataset, api, args, resume, name=None, description=None,
                     multi_label_data=None, session_file=None,
                     path=None, log=None):
    """Splits a dataset into train and test datasets

    """
    train_dataset = None
    test_dataset = None
    sample_rate = 1 - args.test_split
    dataset_alternative_args = r.set_dataset_split_args(
        "%s - train (%s %%)" % (name,
        int(sample_rate * 100)), description, args,
        sample_rate, out_of_bag=False, multi_label_data=multi_label_data)
    train_dataset, resume = alternative_dataset_processing(
        dataset, "train", dataset_alternative_args, api, args,
        resume, session_file=session_file, path=path, log=log)
    dataset_alternative_args = r.set_dataset_split_args(
        "%s - test (%s %%)" % (name,
        int(args.test_split * 100)), description, args,
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
            dataset_args = {
                "all_but": [fields.objective_field],
                "new_fields": [
                    {"name": fields.field_name(fields.objective_field),
                     "field": category_generator,
                     "label": "max_categories: %s" % args.max_categories}]}
            new_dataset = r.create_dataset(
                dataset, dataset_args, args.verbosity, api=api, path=path,
                session_file=session_file, log=log, dataset_type="parts")
            new_dataset = bigml.api.check_resource(new_dataset,
                                                   api.get_dataset)
            user_metadata = {"user_metadata": 
                {"max_categories": args.max_categories,
                 "other_label": other_label}}
            new_dataset = api.update_dataset(new_dataset, user_metadata)
            datasets.append(new_dataset)
    return datasets, resume


def create_new_dataset(datasets, api, args, resume, name=None,
                       description=None, fields=None,
                       dataset_fields=None, objective_field=None,
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
        if args.multi_dataset:
            dataset_args = r.set_dataset_args(name, description, args,
                                              fields, dataset_fields,
                                              objective_field=objective_field)
            if args.multi_dataset_json:
                dataset_args.update(args.multi_dataset_json)
        else:
            dataset_args = {}
            dataset_args.update(args.dataset_json_generators)
            dataset_args.update(r.set_dataset_args(
                name, description, args, fields, dataset_fields,
                objective_field=objective_field))
        new_dataset = r.create_dataset(origin_resource, dataset_args,
                                       args.verbosity,
                                       api=api, path=path,
                                       session_file=session_file,
                                       log=log, dataset_type=suffix)
    else:
        new_dataset = datasets[0]
    return new_dataset, resume
