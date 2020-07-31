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
of deepnets

"""


from bigml.fields import Fields, DEFAULT_MISSING_TOKENS

import bigmler.utils as u
import bigmler.resourcesapi.deepnets as r
import bigmler.checkpoint as c


def has_deepnet(args):
    """Returns whether some kind of deepnet

    """
    return args.deepnet or args.deepnets or \
        args.deepnet_tag


def deepnets_processing(datasets, deepnets, \
    deepnet_ids, api, args, resume, fields=None, \
    session_file=None, path=None, log=None):
    """Creates or retrieves deepnet from the input data

    """

    # If we have a dataset but not a model, we create the model if the no_model
    # flag hasn't been set up.
    if datasets and not (has_deepnet(args) or \
            args.no_deepnet):
        deepnet_ids = []
        deepnets = []

        # Only 1 deepnet per bigmler command at present
        number_of_deepnets = 1
        if resume:
            resume, deepnet_ids = c.checkpoint( \
                c.are_deepnets_created, path, \
                number_of_deepnets, debug=args.debug)
            if not resume:
                message = u.dated("Found %s deepnets out of %s."
                                  " Resuming.\n"
                                  % (len(deepnet_ids),
                                     number_of_deepnets))
                u.log_message(message, log_file=session_file,
                              console=args.verbosity)

            deepnets = deepnet_ids
            number_of_deepnets -= len(deepnet_ids)

        deepnet_args = r.set_deepnet_args( \
            args, fields=fields, \
            deepnet_fields=args.deepnet_fields_,
            objective_id=args.objective_id_)
        deepnets, deepnet_ids = \
            r.create_deepnets( \
            datasets, deepnets, deepnet_args, \
            args, api, path, session_file, log)
    # If a deepnet is provided, we use it.
    elif args.deepnet:
        deepnet_ids = [args.deepnet]
        deepnets = deepnet_ids[:]

    elif args.deepnets or args.deepnet_tag:
        deepnets = deepnet_ids[:]

    # If we are going to predict we must retrieve the deepnets
    if deepnet_ids and (args.test_set or args.export_fields):
        deepnets, deepnet_ids = \
            r.get_deepnets(deepnets, args, api, \
            session_file)

    return deepnets, deepnet_ids, resume


def get_deepnet_fields(deepnet, csv_properties, args):
    """Retrieves fields info from deepnet resource

    """
    if not csv_properties:
        csv_properties = {}
    csv_properties.update(verbose=True)
    if args.user_locale is None:
        args.user_locale = deepnet['object'].get('locale', None)
    csv_properties.update(data_locale=args.user_locale)
    csv_properties.update(missing_tokens=DEFAULT_MISSING_TOKENS)
    csv_properties.update(objective_field=deepnet['object'].get( \
        'objective_field'))
    return Fields(deepnet['object'][ \
        'deepnet']['fields'], **csv_properties)
