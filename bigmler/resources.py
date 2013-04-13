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

import sys
import time

try:
    import simplejson as json
except ImportError:
    import json

import bigml.api

from bigmler.utils import (dated, get_url, log_message, plural,
                           check_resource_error)

EVALUATE_SAMPLE_RATE = 0.8
SEED = "BigML, Machine Learning made easy"


def set_source_args(data_set_header, name, description, args):
    """Returns a source arguments dict

    """
    source_args = {
        "name": name,
        "description": description,
        "category": args.category,
        "tags": args.tag,
        "source_parser": {"header": data_set_header}}
    return source_args


def create_source(data_set, source_args,
                  args, api, path=None,
                  session_file=None, log=None):
    """Creates remote source

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Creating source.\n")
    log_message(message, log_file=session_file, console=args.verbosity)
    source = api.create_source(data_set, source_args,
                               progress_bar=args.progress_bar)
    check_resource_error(source, "Failed to create source: ")
    try:
        source = api.check_resource(source, api.get_source)
    except ValueError, exception:
        sys.exit("Failed to get a finished source: %s" % str(exception))
    message = dated("Source created: %s\n" % get_url(source, api))
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % source['resource'], log_file=log)

    if path is not None:
        try:
            with open(path + '/source', 'w', 0) as source_file:
                source_file.write("%s\n" % source['resource'])
                source_file.write("%s\n" % source['object']['name'])
        except IOError:
            raise IOError("Failed to write %s/source" % path)
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


def get_source(source, api=None, verbosity=True,
               session_file=None):
    """Retrieves the source in its actual state and its field info

    """
    if api is None:
        api = bigml.api.BigML()
    if (isinstance(source, basestring) or
            bigml.api.get_status(source)['code'] != bigml.api.FINISHED):
        message = dated("Retrieving source. %s\n" %
                        get_url(source, api))
        log_message(message, log_file=session_file,
                    console=verbosity)
        try:
            source = api.check_resource(source, api.get_source)
        except ValueError, exception:
            sys.exit("Failed to get a finished source: %s" % str(exception))
    return source


def update_source_fields(source, updated_values, fields, api=None,
                         verbosity=True, session_file=None):
    """Update remote source with new fields values

    """
    if api is None:
        api = bigml.api.BigML()
    update_fields = {}
    for (column, value) in updated_values.iteritems():
        update_fields.update({
            fields.field_id(column): value})
    message = dated("Updating source. %s\n" %
                    get_url(source, api))
    log_message(message, log_file=session_file,
                console=verbosity)
    source = api.update_source(source, {"fields": update_fields})
    check_resource_error(source, "Failed to update source: ")
    return source


def set_dataset_args(name, description, args, fields, dataset_fields):
    """Return dataset arguments dict

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
    return dataset_args


def create_dataset(source, dataset_args, args, api, path=None,
                   session_file=None, log=None):
    """Creates remote dataset

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Creating dataset.\n")
    log_message(message, log_file=session_file, console=args.verbosity)
    dataset = api.create_dataset(source, dataset_args)
    check_resource_error(dataset, "Failed to create dataset: ")
    try:
        dataset = api.check_resource(dataset, api.get_dataset)
    except ValueError, exception:
        sys.exit("Failed to get a finished dataset: %s" % str(exception))
    message = dated("Dataset created: %s\n" % get_url(dataset, api))
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % dataset['resource'], log_file=log)
    if path is not None:
        try:
            with open(path + '/dataset', 'w', 0) as dataset_file:
                dataset_file.write("%s\n" % dataset['resource'])
        except IOError:
            raise IOError("Failed to write %s/dataset" % path)
    return dataset


def get_dataset(dataset, api, verbosity=True, session_file=None):
    """Retrieves the dataset in its actual state

    """
    if api is None:
        api = bigml.api.BigML()
    if (isinstance(dataset, basestring) or
            bigml.api.get_status(dataset)['code'] != bigml.api.FINISHED):
        message = dated("Retrieving dataset. %s\n" %
                        get_url(dataset, api))
        log_message(message, log_file=session_file,
                    console=verbosity)
        dataset = api.check_resource(dataset, api.get_dataset)
        check_resource_error(dataset, "Failed to get dataset: ")
    return dataset


def publish_dataset(dataset, args, api,
                    session_file=None):
    """Publishes dataset and sets its price (if any)

    """
    if api is None:
        api = bigml.api.BigML()
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
    check_resource_error(dataset, "Failed to update dataset: ")
    return dataset


def set_model_args(name, description,
                   args, objective_field=None, fields=None,
                   model_fields=None):
    """Return model arguments dict

    """
    model_args = {
        "name": name,
        "description": description,
        "category": args.category,
        "tags": args.tag
    }
    if objective_field is not None and fields is not None:
        model_args.update({"objective_field":
                           fields.field_id(objective_field)})
    # If evaluate flag is on, we choose a deterministic sampling with
    # args.sample_rate (80% by default) of the data to create the model
    # If cross_validation_rate = n/100, then we choose to run 2 * n evaluations
    # by holding out a n% of randomly sampled data.
    if args.evaluate or args.cross_validation_rate > 0.0:
        model_args.update(seed=SEED)
        if args.cross_validation_rate > 0.0:
            args.sample_rate = 1 - args.cross_validation_rate
            args.replacement = False
        elif args.sample_rate == 1:
            args.sample_rate = EVALUATE_SAMPLE_RATE

    input_fields = []
    if model_fields and fields is not None:
        for name in model_fields:
            input_fields.append(fields.field_id(name))
        model_args.update(input_fields=input_fields)

    if args.pruning and args.pruning != 'smart':
        model_args.update(stat_pruning=(args.pruning == 'statistical'))

    model_args.update(sample_rate=args.sample_rate,
                      replacement=args.replacement,
                      randomize=args.randomize)
    return model_args


def create_models(dataset, model_ids, model_args,
                  args, api, path=None,
                  session_file=None, log=None):
    """Create remote models

    """
    if api is None:
        api = bigml.api.BigML()

    models = model_ids[:]
    existing_models = len(models)
    models_info = ""
    for model_id in model_ids:
        models_info += "%s\n" % model_id
    last_model = None
    if args.number_of_models > 0:
        message = dated("Creating %s.\n" %
                        plural("model", args.number_of_models))
        log_message(message, log_file=session_file,
                    console=args.verbosity)
        last_index = 0
        for i in range(1, args.number_of_models + 1):
            if i % args.max_parallel_models == 1 and i > 1:
                qstr = 'limit=-1'
                try:
                    models[last_index] = api.check_resource(last_model,
                                                            api.get_model,
                                                            query_string=qstr)
                except ValueError, exception:
                    sys.exit("Failed to get a finished model: %s" %
                             str(exception))
            if args.cross_validation_rate > 0.0:
                new_seed = "%s - %s" % (SEED, i + existing_models)
                model_args.update(seed=new_seed)
            model = api.create_model(dataset, model_args)
            check_resource_error(model, "Failed to create model %s:" %
                                 model['resource'])
            log_message("%s\n" % model['resource'], log_file=log)
            last_model = model
            last_index = i - 1
            model_ids.append(model['resource'])
            models.append(model)
            models_info = "%s\n" % model['resource']
            if path is not None:
                try:
                    with open(path + '/models', 'a', 0) as model_file:
                        model_file.write(models_info)
                except IOError:
                    raise IOError("Fails to write %s/models" % path)
        if args.number_of_models < 2 and args.verbosity:
            if bigml.api.get_status(model)['code'] != bigml.api.FINISHED:
                try:
                    model = api.check_resource(model, api.get_model,
                                               query_string='limit=-1')
                except ValueError, exception:
                    sys.exit("Failed to get a finished model: %s" %
                             str(exception))
                models[0] = model
            message = dated("Model created: %s.\n" %
                            get_url(model, api))
            log_message(message, log_file=session_file,
                        console=args.verbosity)

    return models, model_ids


def get_models(model_ids, args, api, session_file=None):
    """Retrieves remote models in its actual status

    """
    if api is None:
        api = bigml.api.BigML()
    model_id = ""
    models = model_ids
    if len(model_ids) == 1:
        model_id = model_ids[0]
    message = dated("Retrieving %s. %s\n" %
                    (plural("model", len(model_ids)),
                     get_url(model_id, api)))
    log_message(message, log_file=session_file, console=args.verbosity)
    if len(model_ids) < args.max_batch_models:
        models = []
        for model in model_ids:
            try:
                model = api.check_resource(model, api.get_model,
                                           query_string='limit=-1')
            except ValueError, exception:
                sys.exit("Failed to get a finished model: %s" %
                         str(exception))
            models.append(model)
        model = models[0]
    else:
        try:
            model = api.check_resource(model_ids[0], api.get_model,
                                       query_string='limit=-1')
        except ValueError, exception:
            sys.exit("Failed to get a finished model: %s" % str(exception))
        models[0] = model
    return models, model_ids


def publish_model(model, args, api=None, session_file=None):
    """Update model with publish info

    """
    if api is None:
        api = bigml.api.BigML()
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
        check_resource_error(model, "Failed to update model %s: " %
                             model['resource'])
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


def set_evaluation_args(name, description, args, fields=None, fields_map=None):
    """Return evaluation args dict

    """
    evaluation_args = {
        "name": name,
        "description": description,
        "tags": args.tag
    }
    if fields_map is not None and fields is not None:
        evaluation_args.update({"fields_map": map_fields(fields_map, fields)})
    # Two cases to use out_of_bag and sample_rate: standard evaluations where
    # only the training set is provided, and cross_validation
    if ((not ((args.dataset or args.test_set)
              and (args.model or args.models or args.model_tag))) or
        ((args.training_set or args.dataset) and
         args.cross_validation_rate > 0.0)):
        evaluation_args.update(out_of_bag=True, seed=SEED,
                               sample_rate=args.sample_rate)

    return evaluation_args


def create_evaluation(model, dataset, evaluation_args, args, api,
                      path=None, session_file=None, log=None, seed=SEED):
    """Create evaluation

    """
    if api is None:
        api = bigml.api.BigML()
    if args.cross_validation_rate > 0.0:
        evaluation_args.update(seed=seed)
    message = dated("Creating evaluation.\n")
    log_message(message, log_file=session_file,
                console=args.verbosity)
    evaluation = api.create_evaluation(model, dataset, evaluation_args)
    check_resource_error(evaluation, "Failed to create evaluation: ")
    log_message("%s\n" % evaluation['resource'], log_file=log)
    if path is not None:
        try:
            with open(path + '/evaluation', 'w', 0) as evaluation_file:
                evaluation_file.write("%s\n" % evaluation['resource'])
        except IOError:
            raise IOError("Failed to write %s/evaluation" % path)

    return evaluation


def create_evaluations(model_ids, dataset, evaluation_args, args, api,
                       path=None, session_file=None, log=None,
                       existing_evaluations=0):
    """Create evaluations for a list of models

    """
    evaluations = []
    if api is None:
        api = bigml.api.BigML()
    number_of_evaluations = len(model_ids)
    message = dated("Creating evaluations.\n")
    log_message(message, log_file=session_file,
                console=args.verbosity)
    for i in range(0, number_of_evaluations):
        model = model_ids[i]
        if args.cross_validation_rate > 0.0:
            new_seed = "%s - %s" % (SEED, i + existing_evaluations)
            evaluation_args.update(seed=new_seed)
        evaluation = api.create_evaluation(model, dataset, evaluation_args)
        check_resource_error(evaluation, "Failed to create evaluation: ")
        evaluations.append(evaluation)
        log_message("%s\n" % evaluation['resource'], log_file=log)
        if path is not None:
            try:
                with open(path + '/evaluations', 'a', 0) as evaluation_file:
                    evaluation_file.write("%s\n" % evaluation['resource'])
            except IOError:
                raise IOError("Failed to write %s/evaluations" % path)
    return evaluations


def get_evaluation(evaluation, api=None, verbosity=True, session_file=None):
    """Retrieves evaluation in its actual state

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Retrieving evaluation. %s\n" %
                    get_url(evaluation, api))
    log_message(message, log_file=session_file, console=verbosity)
    try:
        evaluation = api.check_resource(evaluation, api.get_evaluation)
    except ValueError, exception:
        sys.exit("Failed to get a finished evaluation: %s" % str(exception))
    return evaluation


def save_evaluation(evaluation, output, api=None):
    """Creates the evaluation .txt and .json files

    """
    if api is None:
        api = bigml.api.BigML()
    evaluation_json = open(output + '.json', 'w', 0)
    evaluation = evaluation.get('object', evaluation).get('result', evaluation)
    evaluation_json.write(json.dumps(evaluation))
    evaluation_json.flush()
    evaluation_json.close()
    evaluation_txt = open(output + '.txt', 'w', 0)
    api.pprint(evaluation,
               evaluation_txt)
    evaluation_txt.flush()
    evaluation_txt.close()
