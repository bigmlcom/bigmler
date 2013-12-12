# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012, 2013 BigML
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

"""BigMLer - Resources processing: creation, update and retrieval

"""
from __future__ import absolute_import

import sys
import os
import csv
import copy

import bigml.api
import bigmler.utils as u
import bigmler.resources as r
import bigmler.checkpoint as c
import bigmler.labels as l

from bigml.fields import Fields

from bigmler.train_reader import TrainReader
from bigmler.prediction import OTHER


MISSING_TOKENS = ['', 'N/A', 'n/a', 'NULL', 'null', '-', '#DIV/0', '#REF!',
                  '#NAME?', 'NIL', 'nil', 'NA', 'na', '#VALUE!', '#NULL!',
                  'NaN', '#N/A', '#NUM!', '?']
MONTECARLO_FACTOR = 200


def has_models(args):
    """Returns if some kind of model or ensemble is given in args.

    """
    return (args.model or args.ensemble or args.ensembles
            or args.models or args.model_tag or args.ensemble_tag)


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
        else:
            return []
    except KeyError:
        return []


def check_categorical(field):
    """Checks if a field is categorical

    """
    return field['optype'] == 'categorical'


def test_source_processing(test_set, test_set_header, api, args, resume,
                           name=None, description=None, csv_properties=None,
                           field_attributes=None, types=None,
                           session_file=None, path=None, log=None):
    """Creating or retrieving a test data source from input arguments

    """
    test_source = None
    fields = None
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
                                        args)
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


def dataset_processing(source, training_set, test_set, fields, objective_field,
                       api, args, resume,  name=None, description=None,
                       dataset_fields=None, csv_properties=None,
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
                                          dataset_fields)
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
        if not csv_properties and 'locale' in dataset['object']:
            csv_properties = {
                'data_locale': dataset['object']['locale']}
        fields = Fields(dataset['object']['fields'], **csv_properties)
        if args.public_dataset:
            r.publish_dataset(dataset, args, api, session_file)
        if args.objective_field:
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
                                   name=None, description=None,
                                   out_of_bag=False,
                                   sample_rate=1, session_file=None,
                                   path=None, log=None):
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
                     session_file=None, path=None, log=None):
    """Splits a dataset into train and test datasets

    """
    train_dataset = None
    test_dataset = None
    sample_rate = 1 - args.test_split
    dataset_alternative_args = r.set_dataset_split_args(
        name, description, args,
        sample_rate, out_of_bag=False)
    train_dataset, resume = alternative_dataset_processing(
        dataset, "train", dataset_alternative_args, api, args,
        resume, name="%s - train (%s %%)" % (name,
        int(sample_rate * 100)), description=description,
        session_file=session_file, path=path, log=log)
    dataset_alternative_args = r.set_dataset_split_args(
        name, description, args,
        sample_rate, out_of_bag=True)
    test_dataset, resume = alternative_dataset_processing(
        dataset, "test", dataset_alternative_args, api, args,
        resume, name="%s - test (%s %%)" % (name,
        int(args.test_split * 100)), description=description,
        session_file=session_file, path=path, log=log)

    return train_dataset, test_dataset, resume


def ensemble_processing(dataset, objective_field, fields, api, args, resume,
                        name=None, description=None, model_fields=None,
                        session_file=None,
                        path=None, log=None):
    """Creates an ensemble of models from the input data

    """
    ensembles = []
    number_of_ensembles = 1
    if resume:
        message = u.dated("Ensemble not found. Resuming.\n")
        resume, ensembles = c.checkpoint(
            c.are_ensembles_created, path, number_of_ensembles,
            debug=args.debug,
            message=message, log_file=session_file, console=args.verbosity)
    try:
        ensemble = ensembles[0]
    except IndexError:
        ensemble = None

    if ensemble is None:
        ensemble_args = r.set_ensemble_args(name, description, args,
                                            model_fields, objective_field,
                                            fields)
        ensembles, ensemble_ids, models, model_ids = r.create_ensembles(
            dataset, ensembles, ensemble_args, args, api=api, path=path,
            session_file=session_file, log=log)
    return ensembles, ensemble_ids, models, model_ids, resume


def model_per_label(labels, all_labels, datasets, fields,
                    objective_field, api, args, resume, name=None,
                    description=None, model_fields=None,
                    session_file=None, path=None, log=None):
    """Creates a model per label for multi-label datasets

    """
    model_ids = []
    models = []
    args.number_of_models = len(labels)
    if resume:
        resume, model_ids = c.checkpoint(
            c.are_models_created, path, args.number_of_models,
            debug=args.debug)
        if not resume:
            message = u.dated("Found %s models out of %s."
                              " Resuming.\n"
                              % (len(model_ids),
                                 args.number_of_models))
            u.log_message(message, log_file=session_file,
                          console=args.verbosity)

        models = model_ids
    args.number_of_models = len(labels) - len(model_ids)
    model_args_list = r.set_label_model_args(
        name, description, args,
        labels, all_labels, fields, model_fields, objective_field)

    # create models changing the input_field to select
    # only one label at a time
    models, model_ids = r.create_models(
        datasets, models, model_args_list, args, api,
        path, session_file, log)
    args.number_of_models = 1
    return models, model_ids, resume


def ensemble_per_label(labels, all_labels, dataset, fields,
                       objective_field, api, args, resume, name=None,
                       description=None, model_fields=None,
                       session_file=None, path=None, log=None):
    """Creates an ensemble per label for multi-label datasets

    """

    ensemble_ids = []
    ensembles = []
    model_ids = []
    models = []
    number_of_ensembles = len(labels)
    if resume:
        resume, ensemble_ids = c.checkpoint(
            c.are_ensembles_created, path, number_of_ensembles,
            debug=args.debug)
        ensembles = ensemble_ids
        if not resume:
            message = u.dated("Found %s ensembles out of %s."
                              " Resuming.\n"
                              % (len(ensemble_ids),
                                 number_of_ensembles))
            u.log_message(message, log_file=session_file,
                          console=args.verbosity)
            # erase models' info that will be rebuilt
            u.log_created_resources("models", path, None,
                                    open_mode='w')
    number_of_ensembles = len(labels) - len(ensemble_ids)
    ensemble_args_list = r.set_label_ensemble_args(
        name, description, args,
        labels, all_labels, number_of_ensembles,
        fields, model_fields, objective_field)

    # create ensembles changing the input_field to select
    # only one label at a time
    (ensembles, ensemble_ids,
     models, model_ids) = r.create_ensembles(
         dataset, ensemble_ids, ensemble_args_list, args,
         number_of_ensembles, api,
         path, session_file, log)
    return ensembles, ensemble_ids, models, model_ids, resume


def models_processing(datasets, models, model_ids, objective_field, fields,
                      api, args, resume,
                      name=None, description=None, model_fields=None,
                      session_file=None, path=None,
                      log=None, labels=None, all_labels=None):
    """Creates or retrieves models from the input data

    """
    log_models = False
    ensemble_ids = []

    # If we have a dataset but not a model, we create the model if the no_model
    # flag hasn't been set up.
    if datasets and not (has_models(args) or args.no_model):
        dataset = datasets[0]
        model_ids = []
        models = []
        if args.multi_label:
            # Create one model per column choosing only the label column
            if args.training_set is None:
                all_labels, labels = l.retrieve_labels(fields.fields, labels)
            # If --number-of-models is not set or is 1, create one model per
            # label. Otherwise, create one ensemble per label with the required
            # number of models
            if args.number_of_models < 2:
                models, model_ids, resume = model_per_label(
                    labels, all_labels, datasets, fields,
                    objective_field, api, args, resume, name, description,
                    model_fields, session_file, path, log)
            else:
                (ensembles, ensemble_ids,
                 models, model_ids, resume) = ensemble_per_label(
                     labels, all_labels, dataset, fields,
                     objective_field, api, args, resume, name, description,
                     model_fields, session_file, path, log)

        elif args.number_of_models > 1:
            ensembles = []
            # Ensemble of models
            (ensembles, ensemble_ids,
             models, model_ids, resume) = ensemble_processing(
                 dataset, objective_field, fields, api, args, resume,
                 name=name, description=description, model_fields=model_fields,
                 session_file=session_file, path=path, log=log)
            ensemble = ensembles[0]
            args.ensemble = bigml.api.get_ensemble_id(ensemble)
            log_models = True

        else:
            # Set of partial datasets created setting args.max_categories
            if len(datasets) > 1:
                args.number_of_models = len(datasets)
            # Cross-validation case: we create 2 * n models to be validated
            # holding out an n% of data
            if args.cross_validation_rate > 0:
                if args.number_of_evaluations > 0:
                    args.number_of_models = args.number_of_evaluations
                else:
                    args.number_of_models = int(MONTECARLO_FACTOR *
                                                args.cross_validation_rate)
            if resume:
                resume, model_ids = c.checkpoint(
                    c.are_models_created, path, args.number_of_models,
                    debug=args.debug)
                if not resume:
                    message = u.dated("Found %s models out of %s. Resuming.\n"
                                      % (len(model_ids),
                                         args.number_of_models))
                    u.log_message(message, log_file=session_file,
                                  console=args.verbosity)

                models = model_ids
                args.number_of_models -= len(model_ids)

            model_args = r.set_model_args(name, description, args,
                                          objective_field, fields,
                                          model_fields)
            models, model_ids = r.create_models(datasets, models,
                                                model_args, args, api,
                                                path, session_file, log)
    # If a model is provided, we use it.
    elif args.model:
        model_ids = [args.model]
        models = model_ids[:]

    elif args.models or args.model_tag:
        models = model_ids[:]

    if args.ensemble:
        ensemble = r.get_ensemble(args.ensemble, api, args.verbosity,
                                  session_file)
        ensemble_ids = [ensemble]
        model_ids = ensemble['object']['models']
        if log_models and args.number_of_models > 1:
            for model_id in model_ids:
                u.log_created_resources("models", path, model_id,
                                        open_mode='a')

        models = model_ids[:]

    if args.ensembles or args.ensemble_tag:
        model_ids = []
        ensemble_ids = []
        # Parses ensemble/ids if provided.
        if args.ensemble_tag:
            ensemble_ids = (ensemble_ids +
                            u.list_ids(api.list_ensembles,
                                       "tags__in=%s" % args.ensemble_tag))
        else:
            ensemble_ids = u.read_resources(args.ensembles)
        for ensemble_id in ensemble_ids:
            ensemble = r.get_ensemble(ensemble_id, api)
            if args.ensemble is None:
                args.ensemble = ensemble_id
            model_ids.extend(ensemble['object']['models'])
        models = model_ids[:]

    # If we are going to predict we must retrieve the models
    if model_ids and args.test_set and not args.evaluate:
        models, model_ids = r.get_models(models, args, api, session_file)

    return models, model_ids, ensemble_ids, resume


def get_model_fields(model, csv_properties, args, single_model=True):
    """Retrieves fields info from model resource

    """
    if not csv_properties:
        csv_properties = {}
    csv_properties.update(verbose=True)
    if args.user_locale is None:
        args.user_locale = model['object'].get('locale', None)
    csv_properties.update(data_locale=args.user_locale)
    if single_model and 'model_fields' in model['object']['model']:
        model_fields = model['object']['model']['model_fields'].keys()
        csv_properties.update(include=model_fields)
    else:
        csv_properties.update(include=None)
    if 'missing_tokens' in model['object']['model']:
        missing_tokens = model['object']['model']['missing_tokens']
    else:
        missing_tokens = MISSING_TOKENS
    csv_properties.update(missing_tokens=missing_tokens)
    # if the model belongs to a multi-label set of models, the real objective
    # field is never amongst the set of fields of each individual model, so
    # we must add it.
    fields_dict = copy.deepcopy(model['object']['model']['fields'])
    objective_field = model['object']['objective_fields']
    if isinstance(objective_field, list):
        objective_field = objective_field[0]
    if args.multi_label:
        # Changes fields_dict objective field attributes to the real
        # multi-label objective
        set_multi_label_objective(fields_dict, objective_field)
    csv_properties.update(objective_field=objective_field)

    fields = Fields(fields_dict, **csv_properties)

    return fields, objective_field


def multi_label_expansion(training_set, training_set_header, objective_field,
                          args, output_path, field_attributes=None,
                          labels=None, session_file=None):
    """Splitting the labels in a multi-label objective field to create
       a source with column per label

    """
    # find out column number corresponding to the objective field
    training_reader = TrainReader(training_set, training_set_header,
                                  objective_field, multi_label=True,
                                  labels=labels,
                                  label_separator=args.label_separator,
                                  training_separator=args.training_separator)
    # read file to get all the different labels if no --labels flag is given
    # or use labels given in --labels and generate the new field names
    new_headers = training_reader.get_headers(objective_field=False)
    new_field_names = [l.get_label_field(training_reader.objective_name, label)
                       for label in training_reader.labels]
    new_headers.extend(new_field_names)
    new_headers.append(training_reader.objective_name)
    new_headers = [header.encode("utf-8") for header in new_headers]
    try:
        file_name = os.path.basename(training_set)
    except AttributeError:
        file_name = "training_set.csv"
    output_file = "%s%sextended_%s" % (output_path, os.sep, file_name)
    message = u.dated("Transforming to extended source.\n")
    u.log_message(message, log_file=session_file,
                  console=args.verbosity)
    with open(output_file, 'w', 0) as output_handler:
        output = csv.writer(output_handler, lineterminator="\n")
        output.writerow(new_headers)
        # read to write new source file with column per label
        training_reader.reset()
        if training_set_header:
            training_reader.next()
        while True:
            try:
                row = training_reader.next(extended=True)
                output.writerow(row)
            except StopIteration:
                break
    objective_field = training_reader.headers[training_reader.objective_column]
    if field_attributes is None:
        field_attributes = {}
    for label_column, label in training_reader.labels_columns():
        field_attributes.update({label_column: {
            "label": "%s%s" % (l.MULTI_LABEL_LABEL, label)}})
    # Setting field label to mark objective and label fields and objective
    # field (just in case it was not set previously and other derived fields
    # are added in the source construction process after the real last field).
    return (output_file, training_reader.labels, field_attributes,
            training_reader.objective_name)


def set_multi_label_objective(fields_dict, objective):
    """Changes the field information for the objective field
       in the fields_dict dictionnary to the real objective attributes for
       multi-label models.

    """
    target_field = fields_dict[objective]
    if target_field['label'].startswith(l.MULTI_LABEL_LABEL):
        label = target_field['label'][len(l.MULTI_LABEL_LABEL):]
        objective_name = target_field['name']
        suffix_length = len(label) + 3
        try:
            objective_name = objective_name[0: -suffix_length]
            target_field['name'] = objective_name
            target_field['label'] = 'multi-label objective'
        except IndexError:
            sys.exit("It seems that the label of multi-labelled fields has"
                     " been altered. You should not change the labels of"
                     " generated fields.")
    else:
        sys.exit("It seems that the label of multi-labelled fields has been"
                 " altered. You should not change the labels of generated"
                 " fields.")


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

    for i in range(len(datasets), number_of_datasets):
        split = categories_splits[i]
        category_selector = "(if (or"
        for element in split:
            category = element[0]
            category_selector += " (= v \"%s\")" % category
        category_selector += ") v \"%s\")" % other_label
        category_generator = "(let (v (f %s)) %s)" % (fields.objective_field,
                                                      category_selector)
        dataset_args = {
            "all_but": [fields.objective_field],
            "new_fields": [
                {"name": fields.field_name(fields.objective_field),
                 "field": category_generator}]}
        new_dataset = r.create_dataset(dataset, dataset_args, args.verbosity,
                                       api=api, path=path,
                                       session_file=session_file,
                                       log=log, dataset_type="parts")
        datasets.append(new_dataset)
    return datasets, resume
