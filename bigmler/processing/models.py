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

"""BigMLer - Resources processing: creation, update and retrieval of models

"""
from __future__ import absolute_import

import copy

import bigml.api

from bigml.fields import Fields, DEFAULT_MISSING_TOKENS

import bigmler.utils as u
import bigmler.resources as r
import bigmler.checkpoint as c

from bigmler.processing.ensembles import (ensemble_processing,
                                          ensemble_per_label)

MONTECARLO_FACTOR = 200


def model_per_label(labels, datasets, api, args, resume, fields=None,
                    multi_label_data=None,
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
    model_args_list = r.set_label_model_args(args, fields, labels,
                                             multi_label_data)

    # create models changing the input_field to select
    # only one label at a time
    models, model_ids = r.create_models(
        datasets, models, model_args_list, args, api,
        path, session_file, log)
    args.number_of_models = 1
    return models, model_ids, resume


def models_processing(datasets, models, model_ids,
                      api, args, resume, fields=None,
                      session_file=None, path=None,
                      log=None, labels=None, multi_label_data=None,
                      other_label=None):
    """Creates or retrieves models from the input data

    """
    ensemble_ids = []

    # If we have a dataset but not a model, we create the model if the no_model
    # flag hasn't been set up.
    if datasets and not (args.has_models_ or args.no_model):
        dataset = datasets[0]
        model_ids = []
        models = []
        if args.multi_label:
            # If --number-of-models is not set or is 1, and there's
            # no boosting options on, create one model per
            # label. Otherwise, create one ensemble per label with the required
            # number of models
            if args.number_of_models < 2 and not args.boosting:
                models, model_ids, resume = model_per_label(
                    labels, datasets, api, args, resume,
                    fields=fields, multi_label_data=multi_label_data,
                    session_file=session_file, path=path, log=log)
            else:
                (ensembles, ensemble_ids,
                 models, model_ids, resume) = ensemble_per_label(
                     labels, dataset, api, args, resume, fields=fields,
                     multi_label_data=multi_label_data,
                     session_file=session_file, path=path, log=log)

        elif args.number_of_models > 1 or args.boosting:
            ensembles = []
            # Ensembles of models
            (ensembles, ensemble_ids,
             models, model_ids, resume) = ensemble_processing(
                 datasets, api, args, resume,
                 fields=fields,
                 session_file=session_file, path=path, log=log)
            ensemble = ensembles[0]
            args.ensemble = bigml.api.get_ensemble_id(ensemble)

        else:
            # Set of partial datasets created setting args.max_categories
            if len(datasets) > 1 and args.max_categories:
                args.number_of_models = len(datasets)
            if ((args.test_datasets and args.evaluate) or
                    (args.datasets and args.evaluate and args.dataset_off)):
                args.number_of_models = len(args.dataset_ids)
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
            model_args = r.set_model_args(args,
                                          fields=fields,
                                          objective_id=args.objective_id_,
                                          model_fields=args.model_fields_,
                                          other_label=other_label)
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
        if not args.ensemble in ensemble_ids:
            ensemble_ids.append(args.ensemble)
        if not args.evaluate:
            ensemble = r.get_ensemble(args.ensemble, api, args.verbosity,
                                      session_file)
            model_ids = ensemble['object']['models']
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


def get_model_fields(model, csv_properties, args, single_model=True,
                     multi_label_data=None):
    """Retrieves fields info from model resource

    """
    if not csv_properties:
        csv_properties = {}
    csv_properties.update(verbose=True)
    if args.user_locale is None:
        args.user_locale = model['object'].get('locale', None)
    csv_properties.update(data_locale=args.user_locale)
    if (single_model and 'model_fields' in model['object']['model'] and
            args.test_header):
        model_fields = model['object']['model']['model_fields'].keys()
        csv_properties.update(include=model_fields)
    else:
        csv_properties.update(include=None)
    if 'missing_tokens' in model['object']['model']:
        missing_tokens = model['object']['model']['missing_tokens']
    else:
        missing_tokens = DEFAULT_MISSING_TOKENS
    csv_properties.update(missing_tokens=missing_tokens)
    # if the model belongs to a multi-label set of models, the real objective
    # field is never amongst the set of fields of each individual model, so
    # we must add it.
    fields_dict = copy.deepcopy(model['object']['model']['fields'])

    if args.multi_label:
        # Adds the real objective field to fields_dict
        objective_field = multi_label_data['objective_name']
        objective_id = multi_label_data['objective_id']
        objective_column = multi_label_data['objective_column']
        fields_dict[objective_id] = {"op_type": "categorical",
                                     "name": objective_field,
                                     "column_number": objective_column}
    else:
        objective_field = model['object']['objective_fields']
        if isinstance(objective_field, list):
            objective_field = objective_field[0]
    csv_properties.update(objective_field=objective_field)
    args.objective_field = objective_field
    return Fields(fields_dict, **csv_properties)
