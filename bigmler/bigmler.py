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

"""BigMLer - A Higher Level API to BigML's API

# Basic usage
python bigmler.py \
    --train data/iris.csv \
    --test data/test_iris.csv
    --no-test-header

# Create an 10-model ensemble using bagging
python bigmler.py
    --train train.csv \
    --output submission.csv \
    --objective 0 \
    --types types.txt \
    --name 'Iris Ensemble' \
    --number_of_models 10 \
    --sample_rate 0.75 \
    --replacement \
    --tag my_ensemble

# Make predictions using models tagged with my_ensemble
python bigmler.py \
    --model_tag my_ensemble \
    --test test.csv
    --no-test-header

"""
from __future__ import absolute_import

import sys
import os
import re
import shlex
import datetime
import StringIO
import csv
import copy

import bigml.api
import bigmler.utils as u
import bigmler.resources as r
import bigmler.checkpoint as c
import bigmler.labels as l

from bigml.fields import Fields
from bigml.multivote import COMBINATION_WEIGHTS, COMBINER_MAP, PLURALITY
from bigml.model import Model

from bigmler.evaluation import evaluate, cross_validate
from bigmler.options import create_parser
from bigmler.defaults import get_user_defaults
from bigmler.defaults import DEFAULTS_FILE
from bigmler.prediction import predict, combine_votes
from bigmler.prediction import MAX_MODELS, FULL_FORMAT
from bigmler.train_reader import TrainReader


# Date and time in format SunNov0412_120510 to name and tag resources
NOW = datetime.datetime.now().strftime("%a%b%d%y_%H%M%S")
COMMAND_LOG = ".bigmler"
DIRS_LOG = ".bigmler_dir_stack"
SESSIONS_LOG = "bigmler_sessions"
LOG_FILES = [COMMAND_LOG, DIRS_LOG, u.NEW_DIRS_LOG]
MISSING_TOKENS = ['', 'N/A', 'n/a', 'NULL', 'null', '-', '#DIV/0', '#REF!',
                  '#NAME?', 'NIL', 'nil', 'NA', 'na', '#VALUE!', '#NULL!',
                  'NaN', '#N/A', '#NUM!', '?']
MONTECARLO_FACTOR = 200


def has_models(args):
    """Returns if some kind of model or ensemble is given in args.

    """
    return (args.model or args.ensemble or args.ensembles
            or args.models or args.model_tag or args.ensemble_tag)


def non_compatible(args, option):
    """Return non_compatible options

    """
    if option == '--cross-validation-rate':
        return (args.test_set or args.evaluate or args.model or args.models or
                args.model_tag)
    return False


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


def dataset_processing(source, training_set, test_set, fields, api,
                       args, resume,  name=None, description=None,
                       dataset_fields=None, csv_properties=None,
                       session_file=None, path=None, log=None):
    """Creating or retrieving dataset from input arguments

    """
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
    if ((source and not args.dataset and not args.no_dataset
            and not has_models(args)) or
            (args.evaluate and args.test_set and not args.dataset)):
        dataset_args = r.set_dataset_args(name, description, args, fields,
                                          dataset_fields)
        dataset = r.create_dataset(source, dataset_args, args, api,
                                   path, session_file, log)

    # If a dataset is provided, let's retrieve it.
    elif args.dataset:
        dataset = bigml.api.get_dataset_id(args.dataset)

    # If we already have a dataset, we check the status and get the fields if
    # we hadn't them yet.
    if dataset:
        dataset = r.get_dataset(dataset, api, args.verbosity, session_file)
        if not csv_properties and 'locale' in dataset['object']:
            csv_properties = {
                'data_locale': dataset['object']['locale']}
        fields = Fields(dataset['object']['fields'], **csv_properties)
        if args.public_dataset:
            r.publish_dataset(dataset, api, args, session_file)
    return dataset, resume, csv_properties, fields


def split_processing(dataset, api, args, resume, name=None, description=None,
                     session_file=None, path=None, log=None):
    """Splits a dataset into train and test datasets
    """
    train_dataset = None
    test_dataset = None
    sample_rate = 1 - args.test_split
    # if resuming, try to extract train dataset form log files
    if resume:
        message = u.dated("Dataset not found. Resuming.\n")
        resume, train_dataset = c.checkpoint(
            c.is_dataset_created, path, "_train", debug=args.debug,
            message=message, log_file=session_file, console=args.verbosity)

    if train_dataset is None:
        dataset_split_args = r.set_dataset_split_args(
            "%s - train (%s %%)" % (name,
            int(sample_rate * 100)), description, args,
            sample_rate, out_of_bag=False)
        train_dataset = r.create_dataset(
            dataset, dataset_split_args, args, api, path, session_file,
            log, "train")
        if train_dataset:
            train_dataset = r.get_dataset(train_dataset, api,
                                          args.verbosity, session_file)

    # if resuming, try to extract test dataset form log files
    if resume:
        message = u.dated("Dataset not found. Resuming.\n")
        resume, test_dataset = c.checkpoint(
            c.is_dataset_created, path, "_test", debug=args.debug,
            message=message, log_file=session_file, console=args.verbosity)

    if test_dataset is None:
        dataset_split_args = r.set_dataset_split_args(
            "%s - test (%s %%)" % (name,
            int(args.test_split * 100)), description, args,
            sample_rate, out_of_bag=True)
        test_dataset = r.create_dataset(
            dataset, dataset_split_args, args, api, path, session_file,
            log, "test")
        if test_dataset:
            test_dataset = r.get_dataset(test_dataset, api, args.verbosity,
                                         session_file)
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


def model_per_label(labels, all_labels, dataset, fields,
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
        dataset, models, model_args_list, args, api,
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


def models_processing(dataset, models, model_ids, objective_field, fields,
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
    if dataset and not (has_models(args) or args.no_model):
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
                    labels, all_labels, dataset, fields,
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
            models, model_ids = r.create_models(dataset, models,
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


def compute_output(api, args, training_set, test_set=None, output=None,
                   objective_field=None,
                   description=None,
                   field_attributes=None,
                   types=None,
                   dataset_fields=None,
                   model_fields=None,
                   name=None, training_set_header=True,
                   test_set_header=True, model_ids=None,
                   votes_files=None, resume=False, fields_map=None):
    """ Creates one or more models using the `training_set` or uses the ids
    of previously created BigML models to make predictions for the `test_set`.

    """
    source = None
    dataset = None
    model = None
    models = None
    fields = None
    ensemble_ids = []

    # It is compulsory to have a description to publish either datasets or
    # models
    if (not description and
            (args.black_box or args.white_box or args.public_dataset)):
        sys.exit("You should provide a description to publish.")

    path = u.check_dir(output)
    session_file = "%s%s%s" % (path, os.sep, SESSIONS_LOG)
    csv_properties = {}
    # If logging is required, open the file for logging
    log = None
    if args.log_file:
        u.check_dir(args.log_file)
        log = args.log_file
        # If --clear_logs the log files are cleared
        if args.clear_logs:
            try:
                open(log, 'w', 0).close()
            except IOError:
                pass

    # labels to be used in multi-label expansion
    labels = (map(str.strip, args.labels.split(','))
              if args.labels is not None else None)
    if labels is not None:
        labels = sorted([label.decode("utf-8") for label in labels])

    # multi_label file must be preprocessed to obtain a new extended file
    if args.multi_label and training_set is not None:
        (training_set, labels,
         field_attributes, objective_field) = multi_label_expansion(
             training_set, training_set_header, objective_field, args, path,
             field_attributes=field_attributes, labels=labels,
             session_file=session_file)
        training_set_header = True
    all_labels = labels

    if args.multi_label and args.evaluate and args.test_set is not None:
        (test_set, test_labels,
         field_attributes, objective_field) = multi_label_expansion(
             test_set, test_set_header, objective_field, args, path,
             field_attributes=field_attributes, labels=labels,
             session_file=session_file)
        test_set_header = True

    source, resume, csv_properties, fields = source_processing(
        training_set, test_set, training_set_header, test_set_header,
        api, args, resume, name=name, description=description,
        csv_properties=csv_properties,
        field_attributes=field_attributes,
        types=types, session_file=session_file, path=path, log=log)

    dataset, resume, csv_properties, fields = dataset_processing(
        source, training_set, test_set, fields,
        api, args, resume, name=name, description=description,
        dataset_fields=dataset_fields, csv_properties=csv_properties,
        session_file=session_file, path=path, log=log)

    # If test_split is used, split the dataset in a training and a test dataset
    # according to the given split
    if args.test_split > 0:
        dataset, test_dataset, resume = split_processing(
            dataset, api, args, resume, name=name, description=description,
            session_file=session_file, path=path, log=log)

    models, model_ids, ensemble_ids, resume = models_processing(
        dataset, models, model_ids,
        objective_field, fields, api, args, resume,
        name=name, description=description, model_fields=model_fields,
        session_file=session_file, path=path, log=log, labels=labels,
        all_labels=all_labels)
    if models:
        model = models[0]
        single_model = len(models) == 1

    # We get the fields of the model if we haven't got
    # them yet and update its public state if needed
    if model and not args.evaluate and (test_set or args.black_box
                                        or args.white_box):
        if args.black_box or args.white_box:
            model = r.publish_model(model, args, api, session_file)
            models[0] = model
        # If more than one model, use the full field structure
        fields, objective_field = get_model_fields(
            model, csv_properties, args, single_model=single_model)

    # If multi-label flag is set and no training_set was provided, label
    # info is extracted from the fields structure
    if args.multi_label and training_set is None:
        fields_list = []
        for model in models:
            if (isinstance(model, basestring) or
                    bigml.api.get_status(model)['code'] != bigml.api.FINISHED):
                # if there's more than one model the first one must contain
                # the entire field structure to be used as reference.
                query_string = (r.FIELDS_QS if single_model
                                else r.ALL_FIELDS_QS)
                model = bigml.api.check_resource(model, api.get_model,
                                                 query_string=query_string)
            fields_list.append(model['object']['model']['fields'])
        fields_list.reverse()
        all_labels, labels = l.retrieve_labels(fields_list, labels)

    # If predicting
    if models and test_set and not args.evaluate:
        models_per_label = 1
        if args.multi_label:
            models_per_label = len(models) / len(all_labels)
        predict(test_set, test_set_header, models, fields, output,
                objective_field, args, api, log,
                args.max_batch_models, resume, session_file, labels=labels,
                models_per_label=models_per_label)

    # When combine_votes flag is used, retrieve the predictions files saved
    # in the comma separated list of directories and combine them
    if votes_files:
        model_id = re.sub(r'.*(model_[a-f0-9]{24})__predictions\.csv$',
                          r'\1', votes_files[0]).replace("_", "/")
        try:
            model = u.check_resource(model_id, api.get_model)
        except ValueError, exception:
            sys.exit("Failed to get model %s: %s" % (model_id, str(exception)))

        local_model = Model(model)
        message = u.dated("Combining votes.\n")
        u.log_message(message, log_file=session_file,
                      console=args.verbosity)
        combine_votes(votes_files, local_model.to_prediction,
                      output, args.method)

    # If evaluate flag is on, create remote evaluation and save results in
    # json and human-readable format.
    if args.evaluate:
        if args.test_split > 0:
            dataset = test_dataset
        models_or_ensembles = ensemble_ids if ensemble_ids != [] else models
        resume = evaluate(models_or_ensembles, [dataset], name, description,
                          fields, fields_map, output, api, args, resume,
                          session_file=session_file, path=path, log=log,
                          labels=labels, all_labels=all_labels,
                          objective_field=objective_field)

    # If cross_validation_rate is > 0, create remote evaluations and save
    # results in json and human-readable format. Then average the results to
    # issue a cross_validation measure set.
    if args.cross_validation_rate > 0:
        args.sample_rate = 1 - args.cross_validation_rate
        cross_validate(models, dataset, fields, api, args, resume,
                       name=name, description=description,
                       fields_map=fields_map, session_file=session_file,
                       path=path, log=log)

    # Workaround to restore windows console cp850 encoding to print the tree
    if sys.platform == "win32" and sys.stdout.isatty():
        import locale
        data_locale = locale.getlocale()
        if not data_locale[0] is None:
            locale.setlocale(locale.LC_ALL, (data_locale[0], "850"))
        message = (u"\nGenerated files:\n\n" +
                   unicode(u.print_tree(path, " "), "utf-8") + u"\n")
    else:
        message = "\nGenerated files:\n\n" + u.print_tree(path, " ") + "\n"
    u.log_message(message, log_file=session_file, console=args.verbosity)


def main(args=sys.argv[1:]):
    """Main process

    """
    train_stdin = False
    test_stdin = False
    flags = []
    for i in range(0, len(args)):
        if args[i].startswith("--"):
            flag = args[i]
            # syntax --flag=value
            if "=" in flag:
                flag = args[i][0: flag.index("=")]
            flag = flag.replace("_", "-")
            flags.append(flag)
            if (flag == '--train' and
                    (i == len(args) - 1 or args[i + 1].startswith("--"))):
                train_stdin = True
            elif (flag == '--test' and
                    (i == len(args) - 1 or args[i + 1].startswith("--"))):
                test_stdin = True

    # If --clear-logs the log files are cleared
    if "--clear-logs" in args:
        for log_file in LOG_FILES:
            try:
                open(log_file, 'w', 0).close()
            except IOError:
                pass
    literal_args = args[:]
    for i in range(0, len(args)):
        # quoting literals with blanks: 'petal length'
        if ' ' in args[i]:
            prefix = ""
            literal = args[i]
            # literals with blanks after "+" or "-": +'petal length'
            if args[i][0] in r.ADD_REMOVE_PREFIX:
                prefix = args[i][0]
                literal = args[i][1:]
            literal_args[i] = '%s"%s"' % (prefix, literal)
    message = "bigmler %s\n" % " ".join(literal_args)

    # Resume calls are not logged
    if not "--resume" in args:
        with open(COMMAND_LOG, "a", 0) as command_log:
            command_log.write(message)
        resume = False
    user_defaults = get_user_defaults()
    parser = create_parser(defaults=get_user_defaults(),
                           constants={'NOW': NOW,
                           'MAX_MODELS': MAX_MODELS, 'PLURALITY': PLURALITY})

    # Parses command line arguments.
    command_args = parser.parse_args(args)

    if command_args.cross_validation_rate > 0 and (
            non_compatible(command_args, '--cross-validation-rate')):
        parser.error("Non compatible flags: --cross-validation-rate"
                     " cannot be used with --evaluate, --model,"
                     " --models or --model-tag. Usage:\n\n"
                     "bigmler --train data/iris.csv "
                     "--cross-validation-rate 0.1")

    if train_stdin and command_args.multi_label:
        parser.error("Reading multi-label training sets from stream "
                     "is not yet available.")

    if test_stdin and command_args.resume:
        parser.error("Can't resume when using stream reading test sets.")

    default_output = ('evaluation' if command_args.evaluate
                      else 'predictions.csv')
    if command_args.resume:
        debug = command_args.debug
        command = u.get_log_reversed(COMMAND_LOG,
                                     command_args.stack_level)
        args = shlex.split(command)[1:]
        try:
            position = args.index("--train")
            train_stdin = (position == (len(args) - 1) or
                           args[position + 1].startswith("--"))
        except ValueError:
            pass
        try:
            position = args.index("--test")
            test_stdin = (position == (len(args) - 1) or
                          args[position + 1].startswith("--"))
        except ValueError:
            pass
        output_dir = u.get_log_reversed(DIRS_LOG,
                                        command_args.stack_level)
        defaults_file = "%s%s%s" % (output_dir, os.sep, DEFAULTS_FILE)
        user_defaults = get_user_defaults(defaults_file)
        parser = create_parser(defaults=user_defaults,
                               constants={'NOW': NOW,
                                          'MAX_MODELS': MAX_MODELS,
                                          'PLURALITY': PLURALITY})
        command_args = parser.parse_args(args)
        if command_args.predictions is None:
            command_args.predictions = ("%s%s%s" %
                                        (output_dir, os.sep,
                                         default_output))
        # Logs the issued command and the resumed command
        session_file = "%s%s%s" % (output_dir, os.sep, SESSIONS_LOG)
        u.log_message(message, log_file=session_file)
        message = "\nResuming command:\n%s\n\n" % command
        u.log_message(message, log_file=session_file, console=True)
        try:
            defaults_handler = open(defaults_file, 'r')
            contents = defaults_handler.read()
            message = "\nUsing the following defaults:\n%s\n\n" % contents
            u.log_message(message, log_file=session_file, console=True)
            defaults_handler.close()
        except IOError:
            pass

        resume = True
    else:
        if command_args.predictions is None:
            command_args.predictions = ("%s%s%s" %
                                        (NOW, os.sep,
                                         default_output))
        if len(os.path.dirname(command_args.predictions).strip()) == 0:
            command_args.predictions = ("%s%s%s" %
                                        (NOW, os.sep,
                                         command_args.predictions))
        directory = u.check_dir(command_args.predictions)
        session_file = "%s%s%s" % (directory, os.sep, SESSIONS_LOG)
        u.log_message(message + "\n", log_file=session_file)
        try:
            defaults_file = open(DEFAULTS_FILE, 'r')
            contents = defaults_file.read()
            defaults_file.close()
            defaults_copy = open("%s%s%s" % (directory, os.sep, DEFAULTS_FILE),
                                 'w', 0)
            defaults_copy.write(contents)
            defaults_copy.close()
        except IOError:
            pass
        with open(DIRS_LOG, "a", 0) as directory_log:
            directory_log.write("%s\n" % os.path.abspath(directory))

    if resume and debug:
        command_args.debug = True

    if train_stdin:
        if test_stdin:
            sys.exit("The standard input can't be used both for training and"
                     " testing. Choose one of them")
        command_args.training_set = StringIO.StringIO(sys.stdin.read())
    elif test_stdin:
        command_args.test_set = StringIO.StringIO(sys.stdin.read())

    api_command_args = {
        'username': command_args.username,
        'api_key': command_args.api_key,
        'dev_mode': command_args.dev_mode,
        'debug': command_args.debug}

    if command_args.store:
        api_command_args.update({'storage': u.check_dir(session_file)})

    api = bigml.api.BigML(**api_command_args)

    if (command_args.evaluate
        and not (command_args.training_set or command_args.source
                 or command_args.dataset)
        and not ((command_args.test_set or command_args.test_split) and
                 (command_args.model or
                  command_args.models or command_args.model_tag or
                  command_args.ensemble or command_args.ensembles or
                  command_args.ensemble_tag))):
        parser.error("Evaluation wrong syntax.\n"
                     "\nTry for instance:\n\nbigmler --train data/iris.csv"
                     " --evaluate\nbigmler --model "
                     "model/5081d067035d076151000011 --dataset "
                     "dataset/5081d067035d076151003423 --evaluate\n"
                     "bigmler --ensemble ensemble/5081d067035d076151003443"
                     " --dataset "
                     "dataset/5081d067035d076151003423 --evaluate")

    if command_args.objective_field:
        objective = command_args.objective_field
        try:
            command_args.objective_field = int(objective)
        except ValueError:
            if not command_args.train_header:
                sys.exit("The %s has been set as objective field but"
                         " the file has not been marked as containing"
                         " headers.\nPlease set the --train-header flag if"
                         " the file has headers or use a column number"
                         " to set the objective field." % objective)

    output_args = {
        "api": api,
        "training_set": command_args.training_set,
        "test_set": command_args.test_set,
        "output": command_args.predictions,
        "objective_field": command_args.objective_field,
        "name": command_args.name,
        "training_set_header": command_args.train_header,
        "test_set_header": command_args.test_header,
        "args": command_args,
        "resume": resume,
    }

    # Reads description if provided.
    if command_args.description:
        description_arg = u.read_description(command_args.description)
        output_args.update(description=description_arg)
    else:
        output_args.update(description="Created using BigMLer")

    # Parses fields if provided.
    if command_args.field_attributes:
        field_attributes_arg = (
            u.read_field_attributes(command_args.field_attributes))
        output_args.update(field_attributes=field_attributes_arg)

    # Parses types if provided.
    if command_args.types:
        types_arg = u.read_types(command_args.types)
        output_args.update(types=types_arg)

    # Parses dataset fields if provided.
    if command_args.dataset_fields:
        dataset_fields_arg = map(str.strip,
                                 command_args.dataset_fields.split(','))
        output_args.update(dataset_fields=dataset_fields_arg)

    # Parses model input fields if provided.
    if command_args.model_fields:
        model_fields_arg = map(str.strip,
                               command_args.model_fields.split(','))
        output_args.update(model_fields=model_fields_arg)

    model_ids = []
    # Parses model/ids if provided.
    if command_args.models:
        model_ids = u.read_resources(command_args.models)
        output_args.update(model_ids=model_ids)

    dataset_id = None
    # Parses dataset/id if provided.
    if command_args.datasets:
        dataset_id = u.read_dataset(command_args.datasets)
        command_args.dataset = dataset_id

    # Retrieve model/ids if provided.
    if command_args.model_tag:
        model_ids = (model_ids +
                     u.list_ids(api.list_models,
                                "tags__in=%s" % command_args.model_tag))
        output_args.update(model_ids=model_ids)

    # Reads a json filter if provided.
    if command_args.json_filter:
        json_filter = u.read_json_filter(command_args.json_filter)
        command_args.json_filter = json_filter

    # Reads a lisp filter if provided.
    if command_args.lisp_filter:
        lisp_filter = u.read_lisp_filter(command_args.lisp_filter)
        command_args.lisp_filter = lisp_filter

    # Adds default tags unless that it is requested not to do so.
    if command_args.no_tag:
        command_args.tag.append('BigMLer')
        command_args.tag.append('BigMLer_%s' % NOW)

    # Checks combined votes method
    if (command_args.method and
            not command_args.method in COMBINATION_WEIGHTS.keys()):
        command_args.method = 0
    else:
        combiner_methods = dict([[value, key]
                                for key, value in COMBINER_MAP.items()])
        command_args.method = combiner_methods.get(command_args.method, 0)

    # Adds replacement=True if creating ensemble and nothing is specified
    if (command_args.number_of_models > 1 and
            not command_args.replacement and
            not '--no-replacement' in flags and
            not 'replacement' in user_defaults and
            not '--no-randomize' in flags and
            not 'randomize' in user_defaults and
            not '--sample-rate' in flags and
            not 'sample_rate' in user_defaults):
        command_args.replacement = True

    # Reads votes files in the provided directories.
    if command_args.votes_dirs:
        dirs = map(str.strip, command_args.votes_dirs.split(','))
        votes_path = os.path.dirname(command_args.predictions)
        votes_files = u.read_votes_files(dirs, votes_path)
        output_args.update(votes_files=votes_files)

    # Parses fields map if provided.
    if command_args.fields_map:
        fields_map_arg = u.read_fields_map(command_args.fields_map)
        output_args.update(fields_map=fields_map_arg)

    # Old value for --prediction-info='full data' maps to 'full'
    if command_args.prediction_info == 'full data':
        print "WARNING: 'full data' is a deprecated value. Use 'full' instead"
        command_args.prediction_info = FULL_FORMAT

    # Parses resources ids if provided.
    if command_args.delete:
        if command_args.predictions is None:
            path = NOW
        else:
            path = u.check_dir(command_args.predictions)
        session_file = "%s%s%s" % (path, os.sep, SESSIONS_LOG)
        message = u.dated("Retrieving objects to delete.\n")
        u.log_message(message, log_file=session_file,
                      console=command_args.verbosity)
        delete_list = []
        if command_args.delete_list:
            delete_list = map(str.strip,
                              command_args.delete_list.split(','))
        if command_args.delete_file:
            if not os.path.exists(command_args.delete_file):
                sys.exit("File %s not found" % command_args.delete_file)
            delete_list.extend([line for line
                                in open(command_args.delete_file, "r")])
        if command_args.all_tag:
            query_string = "tags__in=%s" % command_args.all_tag
            delete_list.extend(u.list_ids(api.list_sources, query_string))
            delete_list.extend(u.list_ids(api.list_datasets, query_string))
            delete_list.extend(u.list_ids(api.list_models, query_string))
            delete_list.extend(u.list_ids(api.list_predictions, query_string))
            delete_list.extend(u.list_ids(api.list_evaluations, query_string))
        # Retrieve sources/ids if provided
        if command_args.source_tag:
            query_string = "tags__in=%s" % command_args.source_tag
            delete_list.extend(u.list_ids(api.list_sources, query_string))
        # Retrieve datasets/ids if provided
        if command_args.dataset_tag:
            query_string = "tags__in=%s" % command_args.dataset_tag
            delete_list.extend(u.list_ids(api.list_datasets, query_string))
        # Retrieve model/ids if provided
        if command_args.model_tag:
            query_string = "tags__in=%s" % command_args.model_tag
            delete_list.extend(u.list_ids(api.list_models, query_string))
        # Retrieve prediction/ids if provided
        if command_args.prediction_tag:
            query_string = "tags__in=%s" % command_args.prediction_tag
            delete_list.extend(u.list_ids(api.list_predictions, query_string))
        # Retrieve evaluation/ids if provided
        if command_args.evaluation_tag:
            query_string = "tags__in=%s" % command_args.evaluation_tag
            delete_list.extend(u.list_ids(api.list_evaluations, query_string))
        # Retrieve ensembles/ids if provided
        if command_args.ensemble_tag:
            query_string = "tags__in=%s" % command_args.ensemble_tag
            delete_list.extend(u.list_ids(api.list_ensembles, query_string))
        message = u.dated("Deleting objects.\n")
        u.log_message(message, log_file=session_file,
                      console=command_args.verbosity)
        message = "\n".join(delete_list)
        u.log_message(message, log_file=session_file)
        u.delete(api, delete_list)
        if sys.platform == "win32" and sys.stdout.isatty():
            message = (u"\nGenerated files:\n\n" +
                       unicode(u.print_tree(path, " "), "utf-8") + u"\n")
        else:
            message = "\nGenerated files:\n\n" + u.print_tree(path, " ") + "\n"
        u.log_message(message, log_file=session_file,
                      console=command_args.verbosity)
    elif (command_args.training_set or command_args.test_set
          or command_args.source or command_args.dataset
          or command_args.datasets or command_args.votes_dirs):
        compute_output(**output_args)
    u.log_message("_" * 80 + "\n", log_file=session_file)

if __name__ == '__main__':
    main(sys.argv[1:])
