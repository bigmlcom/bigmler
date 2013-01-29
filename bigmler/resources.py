# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012 BigML
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
"""Resources management functions

"""
from __future__ import absolute_import

import bigml.api
try:
    import simplejson as json
except ImportError:
    import json

from bigmler.utils import (dated, get_url, log_message, checkpoint,
                           are_models_created, plural)


EVALUATE_SAMPLE_RATE = 0.8
SEED = "BigML, Machine Learning made easy"


def create_source(data_set, data_set_header, name, description,
                  api, args, path, session_file=None, log=None):
    """Creates remote source

    """
    source_args = {
        "name": name,
        "description": description,
        "category": args.category,
        "tags": args.tag,
        "source_parser": {"header": data_set_header}}
    message = dated("Creating source.\n")
    log_message(message, log_file=session_file, console=args.verbosity)
    source = api.create_source(data_set, source_args,
                               progress_bar=args.progress_bar)
    source = api.check_resource(source, api.get_source)
    message = dated("Source created: %s\n" % get_url(source, api))
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % source['resource'], log_file=log)

    source_file = open(path + '/source', 'w', 0)
    source_file.write("%s\n" % source['resource'])
    source_file.write("%s\n" % source['object']['name'])
    source_file.flush()
    source_file.close()
    return source


def data_to_source(training_set, test_set,
                   training_set_header, test_set_header, args):
    """Extracts the flags info to create a source object

    """
    data_set = None
    data_set_header = None
    if (training_set and not args.source and not args.dataset and
            not args.model and not args.models):
        data_set = training_set
        data_set_header = training_set_header
    elif (args.evaluate and test_set and not args.source):
        data_set = test_set
        data_set_header = test_set_header
    return data_set, data_set_header


def get_source(source, api, verbosity=True, session_file=None):
    """Retrieves the source in its actual state and its field info

    """
    if (isinstance(source, basestring) or
            source['object']['status']['code'] != bigml.api.FINISHED):
        message = dated("Retrieving source. %s\n" %
                        get_url(source, api))
        log_message(message, log_file=session_file,
                    console=verbosity)
        source = api.check_resource(source, api.get_source)
    return source


def update_source_fields(source, updated_values, api, fields, verbosity,
                         session_file=None):
    """Update remote source with new fields values

    """
    update_fields = {}
    for (column, value) in updated_values.iteritems():
        update_fields.update({
            fields.field_id(column): value})
    message = dated("Updating source. %s\n" %
                    get_url(source, api))
    log_message(message, log_file=session_file,
                console=verbosity)
    source = api.update_source(source, {"fields": update_fields})
    return source


def create_dataset(source, name, description, api, args, fields,
                   dataset_fields, path,
                   session_file=None, log=None):
    """Creates remote dataset

    """
    dataset_args = {
        "name": name,
        "description": description,
        "category": args.category,
        "tags": args.tag
    }

    if args.json_filter:
        dataset_args.update(json_filter=args.json_filter)
    elif args.lisp_filter:
        dataset_args.update(lisp_filter=args.lisp_filter)

    input_fields = []
    if dataset_fields:
        for name in dataset_fields:
            input_fields.append(fields.field_id(name))
        dataset_args.update(input_fields=input_fields)
    message = dated("Creating dataset.\n")
    log_message(message, log_file=session_file, console=args.verbosity)
    dataset = api.create_dataset(source, dataset_args)
    dataset = api.check_resource(dataset, api.get_dataset)
    message = dated("Dataset created: %s\n" % get_url(dataset, api))
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % dataset['resource'], log_file=log)
    dataset_file = open(path + '/dataset', 'w', 0)
    dataset_file.write("%s\n" % dataset['resource'])
    dataset_file.flush()
    dataset_file.close()
    return dataset


def get_dataset(dataset, api, verbosity=True, session_file=None):
    """Retrieves the dataset in its actual state

    """
    if (isinstance(dataset, basestring) or
            dataset['object']['status']['code'] != bigml.api.FINISHED):
        message = dated("Retrieving dataset. %s\n" %
                        get_url(dataset, api))
        log_message(message, log_file=session_file,
                    console=verbosity)
        dataset = api.check_resource(dataset, api.get_dataset)
    return dataset


def publish_dataset(dataset, api, args,
                    session_file=None):
    """Publishes dataset and sets its price (if any)

    """
    public_dataset = {"private": False}
    if args.dataset_price:
        message = dated("Updating dataset. %s\n" %
                        get_url(dataset, api))
        log_message(message, log_file=session_file,
                    console=args.verbosity)
        public_dataset.update(price=args.dataset_price)
    message = dated("Updating dataset. %s\n" %
                    get_url(dataset, api))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    dataset = api.update_dataset(dataset, public_dataset)
    return dataset


def create_models(dataset, model_ids, name, description, api,
                  args, objective_field, fields, model_fields, path, resume,
                  session_file=None, log=None):
    """Create remote models

    """
    model_args = {
        "name": name,
        "description": description,
        "category": args.category,
        "tags": args.tag
    }
    if objective_field is not None:
        model_args.update({"objective_field":
                           fields.field_id(objective_field)})
    # If evaluate flag is on, we choose a deterministic sampling with 80%
    # of the data to create the model
    if args.evaluate:
        if args.sample_rate == 1:
            args.sample_rate = EVALUATE_SAMPLE_RATE
        seed = SEED
        model_args.update(seed=seed)

    input_fields = []
    if model_fields:
        for name in model_fields:
            input_fields.append(fields.field_id(name))
        model_args.update(input_fields=input_fields)

    if args.pruning and args.pruning != 'smart':
        model_args.update(stat_pruning=(args.pruning == 'statistical'))

    model_args.update(sample_rate=args.sample_rate,
                      replacement=args.replacement,
                      randomize=args.randomize)
    model_ids = []
    models = []
    if resume:
        resume, model_ids = checkpoint(are_models_created, path,
                                       args.number_of_models,
                                       debug=args.debug)
        if not resume:
            message = dated("Found %s models out of %s. Resuming.\n" %
                            (len(model_ids),
                             args.number_of_models))
            log_message(message, log_file=session_file,
                        console=args.verbosity)
        models = model_ids
        args.number_of_models -= len(model_ids)

    model_file = open(path + '/models', 'w', 0)
    for model_id in model_ids:
        model_file.write("%s\n" % model_id)
    last_model = None
    if args.number_of_models > 0:
        message = dated("Creating %s.\n" %
                        plural("model", args.number_of_models))
        log_message(message, log_file=session_file,
                    console=args.verbosity)
        for i in range(1, args.number_of_models + 1):
            if i > args.max_parallel_models:
                api.check_resource(last_model, api.get_model)
            model = api.create_model(dataset, model_args)
            log_message("%s\n" % model['resource'], log_file=log)
            last_model = model
            model_ids.append(model['resource'])
            models.append(model)
            model_file.write("%s\n" % model['resource'])
            model_file.flush()
        if args.number_of_models < 2 and args.verbosity:
            if model['object']['status']['code'] != bigml.api.FINISHED:
                model = api.check_resource(model, api.get_model)
                models[0] = model
            message = dated("Model created: %s.\n" %
                            get_url(model, api))
            log_message(message, log_file=session_file,
                        console=args.verbosity)
    model_file.close()
    return models, model_ids, resume


def get_models(model_ids, api, args, session_file=None):
    """Retrieves remote models in its actual status

    """
    model_id = ""
    models = []
    if len(model_ids) == 1:
        model_id = model_ids[0]
    message = dated("Retrieving %s. %s\n" %
                    (plural("model", len(model_ids)),
                     get_url(model_id, api)))
    log_message(message, log_file=session_file, console=args.verbosity)
    if len(model_ids) < args.max_batch_models:
        for model in model_ids:
            model = api.check_resource(model, api.get_model)
            models.append(model)
        model = models[0]
    else:
        model = api.check_resource(model_ids[0], api.get_model)
        models.append(model)
    return models, model_ids


def publish_model(model, api, args, session_file=None):
    """Update model with publish info
    """
    public_model = {}
    if args.black_box:
        public_model = {"private": False}
    if args.white_box:
        public_model = {"private": False, "white_box": True}
        if args.model_price:
            public_model.update(price=args.model_price)
        if args.cpp:
            public_model.update(credits_per_prediction=args.cpp)
    if public_model:
        message = dated("Updating model. %s\n" %
                        get_url(model, api))
        log_message(message, log_file=session_file,
                    console=args.verbosity)
        model = api.update_model(model, public_model)
    return model


def map_fields(fields_map, fields):
    """Build a dict to map dataset to model fields

    """
    update_map = {}
    for (dataset_column, model_column) in fields_map.iteritems():
        update_map.update({
            fields.field_id(dataset_column):
            fields.field_id(model_column)})
    return update_map


def create_evaluation(model, dataset, name, description, api, args, fields,
                      path, fields_map=None, session_file=None, log=None):
    """Create evaluation

    """
    evaluation_args = {
        "name": name,
        "description": description,
        "tags": args.tag
    }
    if not fields_map is None:
        evaluation_args.update({"fields_map": map_fields(fields_map, fields)})
    if not ((args.dataset or args.test_set)
            and (args.model or args.models or args.model_tag)):
        evaluation_args.update(out_of_bag=True, seed=SEED,
                               sample_rate=args.sample_rate)
    message = dated("Creating evaluation.\n")
    log_message(message, log_file=session_file,
                console=args.verbosity)
    evaluation = api.create_evaluation(model, dataset, evaluation_args)
    log_message("%s\n" % evaluation['resource'], log_file=log)
    evaluation_file = open(path + '/evaluation', 'w', 0)
    evaluation_file.write("%s\n" % evaluation['resource'])
    evaluation_file.flush()
    evaluation_file.close()
    return evaluation


def get_evaluation(evaluation, api, verbosity=True, session_file=None):
    """Retrieves evaluation in its actual state

    """
    message = dated("Retrieving evaluation. %s\n" %
                    get_url(evaluation, api))
    log_message(message, log_file=session_file, console=verbosity)
    evaluation = api.check_resource(evaluation, api.get_evaluation)
    return evaluation


def save_evaluation(evaluation, api, output):
    """Prints the evaluation .txt and .json files

    """
    evaluation_json = open(output + '.json', 'w', 0)
    evaluation_json.write(json.dumps(evaluation['object']['result']))
    evaluation_json.flush()
    evaluation_json.close()
    evaluation_txt = open(output + '.txt', 'w', 0)
    api.pprint(evaluation['object']['result'],
               evaluation_txt)
    evaluation_txt.flush()
    evaluation_txt.close()
