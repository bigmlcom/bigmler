# -*- coding: utf-8 -*-
#
# Copyright 2019-2020 BigML
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
of PCAs

"""


from bigml.fields import Fields, DEFAULT_MISSING_TOKENS

import bigmler.utils as u
import bigmler.resourcesapi.pcas as r
import bigmler.checkpoint as c


def has_pca(args):
    """Returns whether some kind of PCA reference is given

    """
    return args.pca or args.pcas or \
        args.pca_tag


def pca_processing(datasets, pca, \
    pca_ids, api, args, resume, fields=None, \
    session_file=None, path=None, log=None):
    """Creates or retrieves pca from the input data

    """

    # If we have a dataset but not a model, we create the model if the no_model
    # flag hasn't been set up.
    if datasets and not (has_pca(args) or \
            args.no_pca):
        pca_ids = []

        # Only 1 pca per bigmler command at present
        number_of_pcas = 1
        if resume:
            resume, pca_ids = c.checkpoint( \
                c.are_pcas_created, path, \
                number_of_pcas, debug=args.debug)
            if not resume:
                message = u.dated("Found %s pcas out of %s."
                                  " Resuming.\n"
                                  % (len(pca_ids),
                                     number_of_pcas))
                u.log_message(message, log_file=session_file,
                              console=args.verbosity)

            number_of_pcas -= len(pca_ids)

        args.exclude_fields = []
        if args.exclude_objective:
            dataset = datasets[0]
            fields = Fields(dataset)
            objective_id =  \
                fields.fields_by_column_number[fields.objective_field]
            args.exclude_fields = [objective_id]
        pca_args = r.set_pca_args( \
            args, fields=fields, \
            pca_fields=args.pca_fields_)
        pca = \
            r.create_pca( \
            datasets, pca, pca_args, \
            args, api, path, session_file, log)

    # If a pca is provided, we use it.
    elif args.pca:
        pca_ids = [args.pca]
        pca = pca_ids[0]

    elif args.pca or args.pca_tag:
        pca = pca_ids[0]

    # If we are going to create projections, we must retrieve the pca
    if pca_ids and (args.test_set or args.export_fields):
        pca = \
            r.get_pca(pca, args, api, session_file)

    return pca, resume


def get_pca_fields(pca, csv_properties, args):
    """Retrieves fields info from PCA resource

    """
    args.retrieve_api_.ok(pca)
    if not csv_properties:
        csv_properties = {}
    csv_properties.update(verbose=True)
    if args.user_locale is None:
        args.user_locale = pca['object'].get('locale', None)
    csv_properties.update(data_locale=args.user_locale)
    csv_properties.update(missing_tokens=DEFAULT_MISSING_TOKENS)
    if args.exclude_objective:
        csv_properties.update({"objective_field_present": False})
        csv_properties.update({"objective_field": None})
    return Fields(pca['object']['pca']['fields'], \
        **csv_properties)
