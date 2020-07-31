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
of linear regressiom

"""


from bigml.fields import Fields, DEFAULT_MISSING_TOKENS

import bigmler.utils as u
import bigmler.resourcesapi.linear_regressions as r
import bigmler.checkpoint as c


def has_linear_regression(args):
    """Returns whether some kind of linear regression

    """
    return args.linear_regression or args.linear_regressions or \
        args.linear_regression_tag


def linear_regressions_processing(datasets, linear_regressions, \
    linear_regression_ids, api, args, resume, fields=None, \
    session_file=None, path=None, log=None):
    """Creates or retrieves linear regression from the input data

    """

    # If we have a dataset but not a model, we create the model if the no_model
    # flag hasn't been set up.
    if datasets and not (has_linear_regression(args) or \
            args.no_linear_regression):
        linear_regression_ids = []
        linear_regressions = []

        # Only 1 linear regression per bigmler command at present
        number_of_linear_regressions = 1
        if resume:
            resume, linear_regression_ids = c.checkpoint( \
                c.are_linear_regressions_created, path, \
                number_of_linear_regressions, debug=args.debug)
            if not resume:
                message = u.dated("Found %s linear regressions out of %s."
                                  " Resuming.\n"
                                  % (len(linear_regression_ids),
                                     number_of_linear_regressions))
                u.log_message(message, log_file=session_file,
                              console=args.verbosity)

            linear_regressions = linear_regression_ids
            number_of_linear_regressions -= len(linear_regression_ids)

        linear_regression_args = r.set_linear_regression_args( \
            args, fields=fields, \
            linear_regression_fields=args.linear_fields_,
            objective_id=args.objective_id_)
        linear_regressions, linear_regression_ids = \
            r.create_linear_regressions( \
            datasets, linear_regressions, linear_regression_args, \
            args, api, path, session_file, log)
    # If a linear regression is provided, we use it.
    elif args.linear_regression:
        linear_regression_ids = [args.linear_regression]
        linear_regressions = linear_regression_ids[:]

    elif args.linear_regressions or args.linear_regression_tag:
        linear_regressions = linear_regression_ids[:]

    # If we are going to predict we must retrieve the linear regressions
    if linear_regression_ids and (args.test_set or args.export_fields):
        linear_regressions, linear_regression_ids = \
            r.get_linear_regressions(linear_regressions, args, api, \
            session_file)

    return linear_regressions, linear_regression_ids, resume


def get_linear_fields(linear_regression, csv_properties, args):
    """Retrieves fields info from linear regression resource

    """
    if not csv_properties:
        csv_properties = {}
    csv_properties.update(verbose=True)
    if args.user_locale is None:
        args.user_locale = linear_regression['object'].get('locale', None)
    csv_properties.update(data_locale=args.user_locale)
    csv_properties.update(missing_tokens=DEFAULT_MISSING_TOKENS)
    return Fields(linear_regression['object'][ \
        'linear_regression']['fields'], \
        **csv_properties)
