# -*- coding: utf-8 -*-
#
# Copyright 2014-2020 BigML
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
of logistic regressiom

"""



from bigml.fields import Fields, DEFAULT_MISSING_TOKENS

import bigmler.utils as u
import bigmler.resourcesapi.logistic_regressions as r
import bigmler.checkpoint as c


def has_logistic_regression(args):
    """Returns whether some kind of logistic regression

    """
    return args.logistic_regression or args.logistic_regressions or \
        args.logistic_regression_tag


def logistic_regressions_processing(datasets, logistic_regressions, \
    logistic_regression_ids, api, args, resume, fields=None, \
    session_file=None, path=None, log=None):
    """Creates or retrieves logistic regression from the input data

    """

    # If we have a dataset but not a model, we create the model if the no_model
    # flag hasn't been set up.
    if datasets and not (has_logistic_regression(args) or \
            args.no_logistic_regression):
        logistic_regression_ids = []
        logistic_regressions = []

        # Only 1 logistic regression per bigmler command at present
        number_of_logistic_regressions = 1
        if resume:
            resume, logistic_regression_ids = c.checkpoint( \
                c.are_logistic_regressions_created, path, \
                number_of_logistic_regressions, debug=args.debug)
            if not resume:
                message = u.dated("Found %s logistic regressions out of %s."
                                  " Resuming.\n"
                                  % (len(logistic_regression_ids),
                                     number_of_logistic_regressions))
                u.log_message(message, log_file=session_file,
                              console=args.verbosity)

            logistic_regressions = logistic_regression_ids
            number_of_logistic_regressions -= len(logistic_regression_ids)

        logistic_regression_args = r.set_logistic_regression_args( \
            args, fields=fields, \
            logistic_regression_fields=args.logistic_fields_,
            objective_id=args.objective_id_)
        logistic_regressions, logistic_regression_ids = \
            r.create_logistic_regressions( \
            datasets, logistic_regressions, logistic_regression_args, \
            args, api, path, session_file, log)
    # If a logistic regression is provided, we use it.
    elif args.logistic_regression:
        logistic_regression_ids = [args.logistic_regression]
        logistic_regressions = logistic_regression_ids[:]

    elif args.logistic_regressions or args.logistic_regression_tag:
        logistic_regressions = logistic_regression_ids[:]

    # If we are going to predict we must retrieve the logistic regressions
    if logistic_regression_ids and (args.test_set or args.export_fields):
        logistic_regressions, logistic_regression_ids = \
            r.get_logistic_regressions(logistic_regressions, args, api, \
            session_file)

    return logistic_regressions, logistic_regression_ids, resume


def get_logistic_fields(logistic_regression, csv_properties, args):
    """Retrieves fields info from logistic regression resource

    """
    if not csv_properties:
        csv_properties = {}
    csv_properties.update(verbose=True)
    if args.user_locale is None:
        args.user_locale = logistic_regression['object'].get('locale', None)
    csv_properties.update(data_locale=args.user_locale)
    csv_properties.update(missing_tokens=DEFAULT_MISSING_TOKENS)
    return Fields(logistic_regression['object'][ \
        'logistic_regression']['fields'], \
        **csv_properties)
