# -*- coding: utf-8 -*-
#
# Copyright 2015-2017 BigML
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

"""BigMLer - Resources processing: creation, update and retrieval of
associations

"""
from __future__ import absolute_import

import bigmler.utils as u
import bigmler.resources as r
import bigmler.checkpoint as c

from bigml.fields import Fields, DEFAULT_MISSING_TOKENS


def has_associations(args):
    """Returns whether there's 'some kind of cluster info

    """
    return args.association or args.associations or args.association_tag


def associations_processing(datasets, associations, association_ids,
                            api, args, resume, fields=None,
                            session_file=None, path=None,
                            log=None):
    """Creates or retrieves associations from the input data

    """

    # If we have a dataset but not a model, we create the model if the no_model
    # flag hasn't been set up.
    if datasets and not (has_associations(args) or args.no_association):
        association_ids = []
        associations = []

        # Only 1 association per bigmler command at present
        number_of_associations = 1
        if resume:
            resume, association_ids = c.checkpoint(
                c.are_associations_created, path, number_of_associations,
                debug=args.debug)
            if not resume:
                message = u.dated("Found %s associations out of %s. Resuming.\n"
                                  % (len(association_ids),
                                     number_of_associations))
                u.log_message(message, log_file=session_file,
                              console=args.verbosity)

            associations = association_ids
            number_of_associations -= len(association_ids)

        association_args = r.set_association_args( \
            args, fields=fields, association_fields=args.association_fields_)
        associations, association_ids = r.create_associations( \
            datasets, associations, association_args, args, api,
            path, session_file, log)
    # If an association is provided, we use it.
    elif args.association:
        association_ids = [args.association]
        associations = association_ids[:]

    elif args.associations or args.association_tag:
        associations = association_ids[:]

    # If we are going to predict we must retrieve the associations
    if association_ids and args.test_set:
        associations, association_ids = r.get_associations( \
            associations, args, api, session_file)

    return associations, association_ids, resume


def get_association_fields(association, csv_properties, args):
    """Retrieves fields info from association resource

    """
    if not csv_properties:
        csv_properties = {}
    csv_properties.update(verbose=True)
    if args.user_locale is None:
        args.user_locale = association['object'].get('locale', None)
    csv_properties.update(data_locale=args.user_locale)
    csv_properties.update(missing_tokens=DEFAULT_MISSING_TOKENS)
    return Fields(association['object']['associations']['fields'],
                  **csv_properties)
