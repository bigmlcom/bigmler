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
"""Resources management functions

"""
from __future__ import absolute_import

import sys

try:
    import simplejson as json
except ImportError:
    import json

import bigml.api

from bigmler.utils import (dated, get_url, log_message, plural, check_resource,
                           check_resource_error, log_created_resources)
from bigmler.labels import label_model_args
from bigml.util import bigml_locale

EVALUATE_SAMPLE_RATE = 0.8
SEED = "BigML, Machine Learning made easy"
LOCALE_DEFAULT = "en_US"
FIELDS_QS = 'only_model=true'
ALL_FIELDS_QS = "limit=-1"
ADD_PREFIX = '+'
REMOVE_PREFIX = '-'
ADD_REMOVE_PREFIX = [ADD_PREFIX, REMOVE_PREFIX]


def get_basic_seed(order):
    """ Builds a standard seed from a text adding the order

    """
    return "%s - %s" % (SEED, order)


def configure_input_fields(fields, user_given_fields):
    """ Returns the input fields used in the new resource creation as given

        The user can choose to write all the fields that will be used in the
        new resource or modify the set of fields retrieved from the
        resource that will be used to create the new one.
    """
    # case of adding and removing fields to the dataset preferred field set
    if all([name[0] in ADD_REMOVE_PREFIX for name in user_given_fields]):
        preferred_fields = fields.preferred_fields()
        input_fields = preferred_fields.keys()
        for name in user_given_fields:
            field_id = fields.field_id(name[1:])
            if name[0] == ADD_PREFIX:
                if not field_id in input_fields:
                    input_fields.append(field_id)
            elif field_id in input_fields:
                input_fields.remove(field_id)
    # case of user given entire list of fields
    else:
        input_fields = []
        for name in user_given_fields:
            input_fields.append(fields.field_id(name))
    return input_fields


def relative_input_fields(fields, user_given_fields):
    """Returns the user given input fields using relative syntax

    """

    input_fields = []
    if all([(name[0] in ADD_REMOVE_PREFIX) for name in user_given_fields]):
        return user_given_fields

    preferred_fields = fields.preferred_fields()
    for field_id in preferred_fields.keys():
        name = fields.fields[field_id]['name']
        if not name in user_given_fields:
            input_fields.append("%s%s" % (REMOVE_PREFIX, name))
    for name in user_given_fields:
        field_id = fields.field_id(name)
        input_fields.append("%s%s" % (ADD_PREFIX, name))

    return input_fields


def set_source_args(data_set_header, name, description, args):
    """Returns a source arguments dict

    """
    source_args = {
        "name": name,
        "description": description,
        "category": args.category,
        "tags": args.tag,
        "source_parser": {"header": data_set_header}}
    # If user has given an OS locale, try to add the locale used in bigml.com
    if args.user_locale is not None:
        source_locale = bigml_locale(args.user_locale)
        if source_locale is None:
            log_message("WARNING: %s locale equivalence not found."
                        " Using %s instead.\n" % (args.user_locale,
                        LOCALE_DEFAULT), log_file=None, console=True)
            source_locale = LOCALE_DEFAULT
        source_args["source_parser"].update({'locale': source_locale})

    return source_args


def create_source(data_set, source_args,
                  args, api=None, path=None,
                  session_file=None, log=None):
    """Creates remote source

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Creating source.\n")
    log_message(message, log_file=session_file, console=args.verbosity)
    source = api.create_source(data_set, source_args,
                               progress_bar=args.progress_bar)
    if path is not None:
        try:
            with open(path + '/source', 'w', 0) as source_file:
                source_file.write("%s\n" % source['resource'])
                source_file.write("%s\n" % source['object']['name'])
        except IOError, exc:
            sys.exit("%s: Failed to write %s/source" % (str(exc), path))
    source_id = check_resource_error(source, "Failed to create source: ")
    try:
        source = check_resource(source, api.get_source,
                                query_string=ALL_FIELDS_QS)
    except ValueError, exception:
        sys.exit("Failed to get a finished source: %s" % str(exception))
    message = dated("Source created: %s\n" % get_url(source))
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % source_id, log_file=log)

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
                        get_url(source))
        log_message(message, log_file=session_file,
                    console=verbosity)
        try:
            source = check_resource(source, api.get_source,
                                    query_string=ALL_FIELDS_QS)
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
                    get_url(source))
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

    if dataset_fields and fields is not None:
        input_fields = configure_input_fields(fields, dataset_fields)
        dataset_args.update(input_fields=input_fields)
    return dataset_args


def set_dataset_split_args(name, description, args, sample_rate,
                           out_of_bag=False):
    """Return dataset arguments dict to split a dataset

    """
    return {
        "name": name,
        "description": description,
        "category": args.category,
        "tags": args.tag,
        "seed": SEED if args.seed is None else args.seed,
        "sample_rate": sample_rate,
        "out_of_bag": out_of_bag
    }


def create_dataset(source_or_dataset, dataset_args, args, api=None, path=None,
                   session_file=None, log=None, dataset_type=None):
    """Creates remote dataset

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Creating dataset.\n")
    log_message(message, log_file=session_file, console=args.verbosity)
    dataset = api.create_dataset(source_or_dataset, dataset_args)
    suffix = "_" + dataset_type if dataset_type else ""
    log_created_resources("dataset%s" % suffix, path,
                          bigml.api.get_dataset_id(dataset))
    dataset_id = check_resource_error(dataset, "Failed to create dataset: ")
    try:
        dataset = check_resource(dataset, api.get_dataset,
                                 query_string=ALL_FIELDS_QS)
    except ValueError, exception:
        sys.exit("Failed to get a finished dataset: %s" % str(exception))
    message = dated("Dataset created: %s\n" % get_url(dataset))
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % dataset_id, log_file=log)
    return dataset


def get_dataset(dataset, api=None, verbosity=True, session_file=None):
    """Retrieves the dataset in its actual state

    """
    if api is None:
        api = bigml.api.BigML()
    if (isinstance(dataset, basestring) or
            bigml.api.get_status(dataset)['code'] != bigml.api.FINISHED):
        message = dated("Retrieving dataset. %s\n" %
                        get_url(dataset))
        log_message(message, log_file=session_file,
                    console=verbosity)
        dataset = check_resource(dataset, api.get_dataset,
                                 query_string=ALL_FIELDS_QS)
        check_resource_error(dataset, "Failed to get dataset: ")
    return dataset


def publish_dataset(dataset, args, api=None, session_file=None):
    """Publishes dataset and sets its price (if any)

    """
    if api is None:
        api = bigml.api.BigML()
    public_dataset = {"private": False}
    if args.dataset_price:
        message = dated("Updating dataset. %s\n" %
                        get_url(dataset))
        log_message(message, log_file=session_file,
                    console=args.verbosity)
        public_dataset.update(price=args.dataset_price)
    message = dated("Updating dataset. %s\n" %
                    get_url(dataset))
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
    # If evaluate flag is on and no test_split flag is provided,
    # we choose a deterministic sampling with
    # args.sample_rate (80% by default) of the data to create the model
    # If cross_validation_rate = n/100, then we choose to run 2 * n evaluations
    # by holding out a n% of randomly sampled data.

    if ((args.evaluate and args.test_split == 0) or
            args.cross_validation_rate > 0):
        model_args.update(seed=SEED)
        if args.cross_validation_rate > 0:
            args.sample_rate = 1 - args.cross_validation_rate
            args.replacement = False
        elif args.sample_rate == 1:
            args.sample_rate = EVALUATE_SAMPLE_RATE

    if model_fields and fields is not None:
        input_fields = configure_input_fields(fields, model_fields)
        model_args.update(input_fields=input_fields)

    if args.pruning and args.pruning != 'smart':
        model_args.update(stat_pruning=(args.pruning == 'statistical'))

    model_args.update(sample_rate=args.sample_rate,
                      replacement=args.replacement,
                      randomize=args.randomize)
    return model_args


def set_label_model_args(name, description, args, labels, all_labels, fields,
                         model_fields, objective_field):
    """Set of args needed to build a model per label

    """
    if model_fields is None:
        model_fields = []
    else:
        model_fields = relative_input_fields(fields, model_fields)
    if objective_field is None:
        objective_id = fields.field_id(fields.objective_field)
        objective_field = fields.fields[objective_id]['name']
    model_args_list = []

    for index in range(args.number_of_models - 1, -1, -1):
        label = labels[index]
        (new_name, label_field, single_label_fields) = label_model_args(
            name, label, all_labels, model_fields, objective_field)
        model_args = set_model_args(new_name, description, args,
                                    label_field, fields,
                                    single_label_fields)
        model_args_list.append(model_args)
    return model_args_list


def create_models(dataset, model_ids, model_args,
                  args, api=None, path=None,
                  session_file=None, log=None):
    """Create remote models

    """
    if api is None:
        api = bigml.api.BigML()

    models = model_ids[:]
    existing_models = len(models)
    model_args_list = []
    if isinstance(model_args, list):
        model_args_list = model_args
    if args.number_of_models > 0:
        message = dated("Creating %s.\n" %
                        plural("model", args.number_of_models))
        log_message(message, log_file=session_file,
                    console=args.verbosity)

        single_model = args.number_of_models == 1 and existing_models == 0
        # if there's more than one model the first one must contain
        # the entire field structure to be used as reference.
        query_string = (FIELDS_QS if single_model
                        else ALL_FIELDS_QS)
        for i in range(0, args.number_of_models):
            if i % args.max_parallel_models == 0 and i > 0:
                try:
                    models[i - 1] = check_resource(
                        models[i - 1], api.get_model,
                        query_string=query_string)
                except ValueError, exception:
                    sys.exit("Failed to get a finished model: %s" %
                             str(exception))
            if model_args_list:
                model_args = model_args_list[i]
            if args.cross_validation_rate > 0:
                new_seed = get_basic_seed(i + existing_models)
                model_args.update(seed=new_seed)
            model = api.create_model(dataset, model_args)
            model_id = check_resource_error(model, "Failed to create model: ")
            log_message("%s\n" % model_id, log_file=log)
            model_ids.append(model_id)
            models.append(model)
            log_created_resources("models", path, model_id, open_mode='a')

        if args.number_of_models < 2 and args.verbosity:
            if bigml.api.get_status(model)['code'] != bigml.api.FINISHED:
                try:
                    model = check_resource(model, api.get_model,
                                           query_string=query_string)
                except ValueError, exception:
                    sys.exit("Failed to get a finished model: %s" %
                             str(exception))
                models[0] = model
            message = dated("Model created: %s.\n" %
                            get_url(model))
            log_message(message, log_file=session_file,
                        console=args.verbosity)

    return models, model_ids


def get_models(model_ids, args, api=None, session_file=None):
    """Retrieves remote models in its actual status

    """
    if api is None:
        api = bigml.api.BigML()
    model_id = ""
    models = model_ids
    single_model = len(model_ids) == 1
    if single_model:
        model_id = model_ids[0]
    message = dated("Retrieving %s. %s\n" %
                    (plural("model", len(model_ids)),
                     get_url(model_id)))
    log_message(message, log_file=session_file, console=args.verbosity)
    if len(model_ids) < args.max_batch_models:
        models = []
        for model in model_ids:
            try:
                # if there's more than one model the first one must contain
                # the entire field structure to be used as reference.
                query_string = (ALL_FIELDS_QS if not single_model
                                and (len(models) == 0 or args.multi_label)
                                else FIELDS_QS)
                model = check_resource(model, api.get_model,
                                       query_string=query_string)
            except ValueError, exception:
                sys.exit("Failed to get a finished model: %s" %
                         str(exception))
            models.append(model)
        model = models[0]
    else:
        try:
            query_string = (ALL_FIELDS_QS if not single_model
                            else FIELDS_QS)
            model = check_resource(model_ids[0], api.get_model,
                                   query_string=query_string)
        except ValueError, exception:
            sys.exit("Failed to get a finished model: %s" % str(exception))
        models[0] = model
    return models, model_ids


def set_label_ensemble_args(name, description, args, labels, all_labels,
                            number_of_ensembles, fields, model_fields,
                            objective_field):
    """Set of args needed to build an ensemble per label

    """
    if model_fields is None:
        model_fields = []
    else:
        model_fields = relative_input_fields(fields, model_fields)
    if objective_field is None:
        objective_id = fields.field_id(fields.objective_field)
        objective_field = fields.fields[objective_id]['name']
    ensemble_args_list = []

    for index in range(number_of_ensembles - 1, -1, -1):
        label = labels[index]
        (new_name, label_field, single_label_fields) = label_model_args(
            name, label, all_labels, model_fields, objective_field)
        ensemble_args = set_ensemble_args(new_name, description, args,
                                          single_label_fields,
                                          label_field, fields)
        ensemble_args_list.append(ensemble_args)
    return ensemble_args_list


def set_ensemble_args(name, description, args, model_fields,
                      objective_field=None, fields=None):
    """Return ensemble arguments dict

    """
    ensemble_args = {
        "name": name,
        "description": description,
        "number_of_models": args.number_of_models,
        "category": args.category,
        "tags": args.tag
    }
    if objective_field is not None and fields is not None:
        ensemble_args.update({"objective_field":
                              fields.field_id(objective_field)})
    # If evaluate flag is on and no test_split flag is provided,
    # we choose a deterministic sampling with
    # args.sample_rate (80% by default) of the data to create the model

    if (args.evaluate and args.test_split == 0):
        ensemble_args.update(seed=SEED)
        if args.sample_rate == 1:
            args.sample_rate = EVALUATE_SAMPLE_RATE

    if model_fields and fields is not None:
        input_fields = configure_input_fields(fields, model_fields)
        ensemble_args.update(input_fields=input_fields)

    if args.pruning and args.pruning != 'smart':
        ensemble_args.update(stat_pruning=(args.pruning == 'statistical'))

    ensemble_args.update(sample_rate=args.sample_rate,
                         replacement=args.replacement,
                         randomize=args.randomize,
                         tlp=args.tlp)
    return ensemble_args


def create_ensembles(dataset, ensemble_ids, ensemble_args, args,
                     number_of_ensembles=1,
                     api=None, path=None, session_file=None, log=None):
    """Create ensembles from input data

    """
    if api is None:
        api = bigml.api.BigML()
    ensembles = ensemble_ids[:]
    model_ids = []
    ensemble_args_list = []
    if isinstance(ensemble_args, list):
        ensemble_args_list = ensemble_args
    if number_of_ensembles > 0:
        message = dated("Creating %s.\n" %
                        plural("ensemble", number_of_ensembles))
        log_message(message, log_file=session_file,
                    console=args.verbosity)
        query_string = ALL_FIELDS_QS
        for i in range(0, number_of_ensembles):
            if i % args.max_parallel_ensembles == 0 and i > 0:
                try:
                    ensembles[i - 1] = check_resource(
                        ensembles[i - 1], api.get_ensemble,
                        query_string=query_string)
                except ValueError, exception:
                    sys.exit("Failed to get a finished ensemble: %s" %
                             str(exception))
            if ensemble_args_list:
                ensemble_args = ensemble_args_list[i]
            ensemble = api.create_ensemble(dataset, ensemble_args)
            ensemble_id = check_resource_error(ensemble,
                                               "Failed to create ensemble: ")
            log_message("%s\n" % ensemble_id, log_file=log)
            ensemble_ids.append(ensemble_id)
            ensembles.append(ensemble)
            log_created_resources("ensembles", path, ensemble_id,
                                  open_mode='a')

        models, model_ids = retrieve_ensembles_models(ensembles, api, path)
        if number_of_ensembles < 2 and args.verbosity:
            message = dated("Ensemble created: %s.\n" %
                            get_url(ensemble))
            log_message(message, log_file=session_file,
                        console=args.verbosity)

    return ensembles, ensemble_ids, models, model_ids


def retrieve_ensembles_models(ensembles, api, path=None):
    """Retrieves the models associated to a list of ensembles

    """
    models = []
    model_ids = []
    for index in range(0, len(ensembles)):
        ensemble = ensembles[index]
        if (isinstance(ensemble, basestring) or
                bigml.api.get_status(ensemble)['code'] != bigml.api.FINISHED):
            try:
                ensemble = check_resource(ensemble, api.get_ensemble)
                ensembles[index] = ensemble
            except ValueError, exception:
                sys.exit("Failed to get a finished ensemble: %s" %
                         str(exception))
        model_ids.extend(ensemble['object']['models'])
    if path is not None:
        for model_id in model_ids:
            log_created_resources("models", path, model_id, open_mode='a')
    models = model_ids[:]
    models[0] = check_resource(models[0], api.get_model,
                               query_string=ALL_FIELDS_QS)
    return models, model_ids


def get_ensemble(ensemble, api=None, verbosity=True, session_file=None):
    """Retrieves remote ensemble in its actual status

    """
    if api is None:
        api = bigml.api.BigML()
    if (isinstance(ensemble, basestring) or
            bigml.api.get_status(ensemble)['code'] != bigml.api.FINISHED):
        message = dated("Retrieving ensemble. %s\n" %
                        get_url(ensemble))
        log_message(message, log_file=session_file,
                    console=verbosity)
        ensemble = check_resource(ensemble, api.get_ensemble)
        check_resource_error(ensemble, "Failed to get ensemble: ")
    return ensemble


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
                        get_url(model))
        log_message(message, log_file=session_file,
                    console=args.verbosity)
        model = api.update_model(model, public_model)
        check_resource_error(model, "Failed to update model %s: " %
                             model['resource'])
    return model


def map_fields(fields_map, fields):
    """Build a dict to map model to dataset fields

    """
    update_map = {}
    for (model_column, dataset_column) in fields_map.iteritems():
        update_map.update({
            fields.field_id(model_column):
            fields.field_id(dataset_column)})

    return update_map


def set_evaluation_args(name, description, args, fields=None, fields_map=None):
    """Return evaluation args dict

    """
    evaluation_args = {
        "name": name,
        "description": description,
        "tags": args.tag
    }
    if (args.number_of_models > 1 or args.ensemble):
        evaluation_args.update(combiner=args.method)
    if fields_map is not None and fields is not None:
        evaluation_args.update({"fields_map": map_fields(fields_map, fields)})
    # Two cases to use out_of_bag and sample_rate: standard evaluations where
    # only the training set is provided, and cross_validation
    # [--dataset|--test] [--model|--models|--model-tag|--ensemble] --evaluate
    if ((args.dataset or args.test_set)
            and (args.model or args.models or args.model_tag or
                 (args.ensemble and args.number_of_models == 1))):
        return evaluation_args
    # [--train|--dataset] --test-split --evaluate
    if (args.test_split > 0 and (args.training_set or args.dataset)):
        return evaluation_args
    if args.sample_rate == 1:
        args.sample_rate = EVALUATE_SAMPLE_RATE
    evaluation_args.update(out_of_bag=True, seed=SEED,
                           sample_rate=args.sample_rate)
    return evaluation_args


def set_label_evaluation_args(name, description, args, labels, all_labels,
                              number_of_evaluations, fields, fields_map,
                              objective_field):
    """Set of args needed to build an evaluation per label

    """
    if objective_field is None:
        objective_id = fields.field_id(fields.objective_field)
        objective_field = fields.fields[objective_id]['name']
    evaluation_args_list = []

    for index in range(number_of_evaluations - 1, -1, -1):
        label = labels[index]
        new_name = label_model_args(
            name, label, all_labels, [], objective_field)[0]
        evaluation_args = set_evaluation_args(new_name, description, args,
                                              fields, fields_map)
        evaluation_args_list.append(evaluation_args)
    return evaluation_args_list


def create_evaluations(model_ids, datasets, evaluation_args, args, api=None,
                       path=None, session_file=None, log=None,
                       existing_evaluations=0):
    """Create evaluations for a list of models

       ``model_ids``: list of model ids to create an evaluation of
       ``datasets``: dataset objects or ids to evaluate with
       ``evaluation_args``: arguments for the ``create_evaluation`` call
       ``args``: input values for bigmler flags
       ``api``: api to remote objects in BigML
       ``path``: directory to store the BigMLer generated files in
       ``session_file``: file to store the messages of that session
       ``log``: user provided log file
       ``existing_evaluations``: evaluations found when attempting resume
    """
    evaluations = []
    dataset = datasets[0]
    evaluation_args_list = []
    if isinstance(evaluation_args, list):
        evaluation_args_list = evaluation_args
    if api is None:
        api = bigml.api.BigML()
    remaining_ids = model_ids[existing_evaluations:]
    number_of_evaluations = len(remaining_ids)
    message = dated("Creating evaluations.\n")
    log_message(message, log_file=session_file,
                console=args.verbosity)
    for i in range(0, number_of_evaluations):
        model = remaining_ids[i]

        if i % args.max_parallel_evaluations == 0 and i > 0:
            try:
                evaluations[i - 1] = check_resource(
                    evaluations[i - 1], api.get_evaluation)
            except ValueError, exception:
                sys.exit("Failed to get a finished evaluation: %s" %
                         str(exception))
        if evaluation_args_list != []:
            evaluation_args = evaluation_args_list[i]
        if args.cross_validation_rate > 0:
            new_seed = get_basic_seed(i + existing_evaluations)
            evaluation_args.update(seed=new_seed)
        evaluation = api.create_evaluation(model, dataset, evaluation_args)
        evaluation_id = check_resource_error(evaluation,
                                             "Failed to create evaluation: ")
        log_created_resources("evaluations", path, evaluation_id,
                              open_mode='a')
        evaluations.append(evaluation)
        log_message("%s\n" % evaluation['resource'], log_file=log)

    return evaluations


def get_evaluation(evaluation, api=None, verbosity=True, session_file=None):
    """Retrieves evaluation in its actual state

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Retrieving evaluation. %s\n" %
                    get_url(evaluation))
    log_message(message, log_file=session_file, console=verbosity)
    try:
        evaluation = check_resource(evaluation, api.get_evaluation)
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
    api.pprint(evaluation, evaluation_txt)
    evaluation_txt.flush()
    evaluation_txt.close()
