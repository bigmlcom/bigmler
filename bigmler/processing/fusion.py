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
of Fusions

"""


from bigml.fields import Fields, DEFAULT_MISSING_TOKENS

import bigmler.utils as u
import bigmler.resourcesapi.fusions as r
import bigmler.checkpoint as c


def has_fusion(args):
    """Returns whether some kind of Fusion reference is given

    """
    return args.fusion or args.fusions or \
        args.fusion_tag


def fusion_processing(fusion, \
    fusion_ids, api, args, resume, fields=None, \
    session_file=None, path=None, log=None):
    """Creates or retrieves fusion from the input data

    """

    # If we have a models' list but not a fusion,
    # we create the model if the no_model
    # flag hasn't been set up.
    if args.fusion_models_ is not None and not has_fusion(args):
        fusion_ids = []

        # Only 1 fusion per bigmler command at present
        number_of_fusions = 1
        if resume:
            resume, fusion_ids = c.checkpoint( \
                c.are_fusions_created, path, \
                number_of_fusions, debug=args.debug)
            if not resume:
                message = u.dated("Found %s fusions out of %s."
                                  " Resuming.\n"
                                  % (len(fusion_ids),
                                     number_of_fusions))
                u.log_message(message, log_file=session_file,
                              console=args.verbosity)

            fusion = fusion_ids[0]
            first_model_id = api.get_fusion(fusion)[ \
                "object"]["fusion"]["models"][0]["id"]
            first_model_kind = api.get_fusion(fusion)[ \
                "object"]["fusion"]["models"][0]["kind"]
            first_model = api.getters[first_model_kind](first_model_id)
            fields = Fields(first_model)
            number_of_fusions -= len(fusion_ids)

        fusion_args = r.set_fusion_args( \
            args, fields)
        fusion = \
            r.create_fusion( \
            args.fusion_models_, fusion, fusion_args, \
            args, api, path, session_file, log)

    # If a fusion is provided, we use it.
    elif args.fusion:
        fusion_ids = [args.fusion]
        fusion = fusion_ids[0]

    elif args.fusion or args.fusion_tag:
        fusion = fusion_ids[0]

    # If we are going to create predictions, we must retrieve the fusion
    if fusion_ids and args.test_set:
        fusion = \
            r.get_fusion(fusion, args, api, session_file)
        args.objective_field = fusion['object']['objective_field_name']

    return fusion, resume


def get_fusion_fields(fusion, csv_properties, args):
    """Retrieves fields info from Fusion resource

    """
    args.retrieve_api_.ok(fusion)
    if not csv_properties:
        csv_properties = {}
    csv_properties.update(verbose=True)
    csv_properties.update(missing_tokens=DEFAULT_MISSING_TOKENS)
    return Fields(fusion['object']['fusion']['fields'], \
        **csv_properties)
