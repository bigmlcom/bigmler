# -*- coding: utf-8 -*-
#
# Copyright 2017-2020 BigML
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

"""Evaluation related functions for BigMLer

"""


import bigmler.utils as u
import bigmler.resourcesapi.evaluations as r
import bigmler.checkpoint as c

from bigmler.resourcesapi.common import shared_changed

def evaluate(time_series_set, datasets, api, args, resume,
             session_file=None, path=None, log=None,
             fields=None, dataset_fields=None):
    """Evaluates a list of time-series with the given dataset

    """
    output = args.predictions
    evaluations, resume = evaluations_process(
        time_series_set, datasets, fields,
        dataset_fields, api, args, resume,
        session_file=session_file, path=path, log=log)
    for evaluation in evaluations:
        evaluation = r.get_evaluation(evaluation, api, args.verbosity,
                                      session_file)
        if shared_changed(args.shared, evaluation):
            evaluation_args = {"shared": args.shared}
            evaluation = r.update_evaluation(evaluation, evaluation_args,
                                             args, api=api, path=path,
                                             session_file=session_file)
        file_name = output
        r.save_evaluation(evaluation, file_name, api)
    return resume


def evaluations_process(time_series_set, datasets,
                        fields, dataset_fields, api, args, resume,
                        session_file=None, path=None, log=None):
    """Evaluates time-series against datasets

    """

    existing_evaluations = 0
    evaluations = []
    number_of_evaluations = len(time_series_set)
    if resume:
        resume, evaluations = c.checkpoint(c.are_evaluations_created, path,
                                           number_of_evaluations,
                                           debug=args.debug)
        if not resume:
            existing_evaluations = len(evaluations)
            message = u.dated("Found %s evaluations from %s. Resuming.\n" %
                              (existing_evaluations,
                               number_of_evaluations))
            number_of_evaluations -= existing_evaluations
            u.log_message(message, log_file=session_file,
                          console=args.verbosity)
    if not resume:
        evaluation_args = r.set_evaluation_args(args, fields,
                                                dataset_fields)
        evaluations.extend(r.create_evaluations(
            time_series_set, datasets, evaluation_args,
            args, api, path=path, session_file=session_file,
            log=log, existing_evaluations=existing_evaluations))

    return evaluations, resume
