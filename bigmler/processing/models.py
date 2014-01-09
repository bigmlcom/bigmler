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

"""BigMLer - Resources processing: creation, update and retrieval of models

"""
from __future__ import absolute_import

import sys
import copy

import bigml.api
import bigmler.utils as u
import bigmler.resources as r
import bigmler.checkpoint as c
import bigmler.labels as l

from bigml.fields import Fields

from bigmler.processing.ensembles import (ensemble_processing,
                                          ensemble_per_label)

from bigmler.processing.ensembles import MISSING_TOKENS

MONTECARLO_FACTOR = 200


def has_models(args):
    """Returns if some kind of model or ensemble is given in args.

    """
    return (args.model or args.ensemble or args.ensembles
            or args.models or args.model_tag or args.ensemble_tag)


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
            sys.exit("It seems that the label of multi-labeled fields has"
                     " been altered. You should not change the labels of"
                     " generated fields.")
    else:
        sys.exit("It seems that the label of multi-labeled fields has been"
                 " altered. You should not change the labels of generated"
                 " fields.")


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


def models_processing(datasets, models, model_ids, objective_field, fields,
                      api, args, resume,
                      name=None, description=None, model_fields=None,
                      session_file=None, path=None,
                      log=None, labels=None, all_labels=None):
    """Creates or retrieves models from the input data

    """
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
                if objective_field is None:
                    objective_field = fields.objective_field
                objective_id = fields.field_id(objective_field)
                objective_name = fields.fields[objective_id]['name']
                all_labels, labels = l.retrieve_labels(fields.fields, labels,
                                                       objective_name)
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
                 datasets, objective_field, fields, api, args, resume,
                 name=name, description=description, model_fields=model_fields,
                 session_file=session_file, path=path, log=log)
            ensemble = ensembles[0]
            args.ensemble = bigml.api.get_ensemble_id(ensemble)

        else:
            # Set of partial datasets created setting args.max_categories
            if len(datasets) > 1 and args.max_categories:
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
