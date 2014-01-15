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

"""BigMLer - Resources processing: creation, update and retrieval of ensembles

"""
from __future__ import absolute_import


import bigmler.utils as u
import bigmler.resources as r
import bigmler.checkpoint as c


MISSING_TOKENS = ['', 'N/A', 'n/a', 'NULL', 'null', '-', '#DIV/0', '#REF!',
                  '#NAME?', 'NIL', 'nil', 'NA', 'na', '#VALUE!', '#NULL!',
                  'NaN', '#N/A', '#NUM!', '?']
MONTECARLO_FACTOR = 200


def ensemble_processing(datasets, objective_field, fields, api, args, resume,
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
            datasets, ensembles, ensemble_args, args, api=api, path=path,
            session_file=session_file, log=log)
    return ensembles, ensemble_ids, models, model_ids, resume


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
