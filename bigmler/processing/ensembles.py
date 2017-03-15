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

"""BigMLer - Resources processing: creation, update and retrieval of ensembles

"""
from __future__ import absolute_import


import bigmler.utils as u
import bigmler.resources as r
import bigmler.checkpoint as c


MONTECARLO_FACTOR = 200


def ensemble_processing(datasets, api, args, resume,
                        fields=None,
                        session_file=None,
                        path=None, log=None):
    """Creates an ensemble of models from the input data

    """
    ensembles = []
    ensemble_ids = []
    models = []
    model_ids = []
    number_of_ensembles = len(datasets)

    if resume:
        resume, ensemble_ids = c.checkpoint(
            c.are_ensembles_created, path, number_of_ensembles,
            debug=args.debug)
        if args.number_of_models > 1:
            _, model_ids = c.checkpoint(c.are_models_created, path, \
                number_of_ensembles * args.number_of_models)
            models = model_ids
        if not resume:
            message = u.dated("Found %s ensembles out of %s. Resuming.\n"
                              % (len(ensemble_ids),
                                 number_of_ensembles))
            u.log_message(message, log_file=session_file,
                          console=args.verbosity)
        ensembles = ensemble_ids
        number_of_ensembles -= len(ensemble_ids)

    if number_of_ensembles > 0:
        ensemble_args = r.set_ensemble_args(args, fields=fields)
        ensembles, ensemble_ids, models, model_ids = r.create_ensembles(
            datasets, ensembles, ensemble_args, args, api=api, path=path,
            number_of_ensembles=number_of_ensembles,
            session_file=session_file, log=log)
    return ensembles, ensemble_ids, models, model_ids, resume


def ensemble_per_label(labels, dataset, api, args, resume, fields=None,
                       multi_label_data=None,
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
                                    mode='w')
    number_of_ensembles = len(labels) - len(ensemble_ids)
    ensemble_args_list = r.set_label_ensemble_args(
        args,
        labels, multi_label_data, number_of_ensembles,
        fields)

    # create ensembles changing the input_field to select
    # only one label at a time
    (ensembles, ensemble_ids,
     models, model_ids) = r.create_ensembles(
         dataset, ensemble_ids, ensemble_args_list, args,
         number_of_ensembles, api,
         path, session_file, log)
    return ensembles, ensemble_ids, models, model_ids, resume
