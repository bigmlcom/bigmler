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

"""BigMLer - Resources processing: creation, update and retrieval
of time-series

"""


import bigmler.utils as u
import bigmler.resourcesapi.time_series as r
import bigmler.checkpoint as c


def has_time_series(args):
    """Returns whether there's some kind of time-series ID

    """
    return args.time_series or args.time_series_set or \
        args.time_series_file


def time_series_processing(datasets, time_series_set, \
    time_series_ids, api, args, resume, fields=None, \
    session_file=None, path=None, log=None):
    """Creates or retrieves time_series from the input data

    """

    # If we have a dataset but not a model, we create the model if the no_model
    # flag hasn't been set up.
    if datasets and not (has_time_series(args) or \
            args.no_time_series):
        time_series_ids = []
        time_series_set = []

        # Only 1 time-series per bigmler command at present
        number_of_time_series = 1
        if resume:
            resume, time_series_ids = c.checkpoint( \
                c.are_time_series_created, path, \
                number_of_time_series, debug=args.debug)
            if not resume:
                message = u.dated("Found %s time-series out of %s."
                                  " Resuming.\n"
                                  % (len(time_series_ids),
                                     number_of_time_series))
                u.log_message(message, log_file=session_file,
                              console=args.verbosity)

            time_series_set = time_series_ids
            number_of_time_series -= len(time_series_ids)

        time_series_args = r.set_time_series_args( \
            args, fields=fields,
            objective_id=args.objective_id_)
        time_series_set, time_series_ids = \
            r.create_time_series( \
            datasets, time_series_set, time_series_args, \
            args, api, path, session_file, log)
    # If a time_series is provided, we use it.
    elif args.time_series:
        time_series_ids = [args.time_series]
        time_series_set = time_series_ids[:]

    elif args.time_series_set or args.time_series_tag:
        time_series_set = time_series_ids[:]

    # If we are going to predict we must retrieve the time-series
    if time_series_ids and args.export_fields:
        time_series_set, time_series_ids = \
            r.get_time_series(time_series_set, args, api, \
            session_file)

    return time_series_set, time_series_ids, resume
