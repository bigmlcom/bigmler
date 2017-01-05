# -*- coding: utf-8 -*-
#
# Copyright 2016-2017 BigML
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

"""BigMLer - Resources processing: creation, update and retrieval of topic
models

"""
from __future__ import absolute_import

import bigmler.utils as u
import bigmler.resources as r
import bigmler.checkpoint as c

from bigml.fields import Fields, DEFAULT_MISSING_TOKENS


def has_topic_models(args):
    """Returns whether some kind of topic model

    """
    return args.topic_model or args.topic_models or args.topic_model_tag


def topic_model_processing(datasets, topic_models, topic_model_ids,
                           api, args, resume, fields=None,
                           session_file=None, path=None,
                           log=None):
    """Creates or retrieves topic models from the input data

    """

    # If we have a dataset but not a topic model, we create the topic model
    # if the no_topic_model
    # flag hasn't been set up.
    if datasets and not (has_topic_models(args) or args.no_topic_model):
        topic_model_ids = []
        topic_models = []

        # Only 1 topic model per bigmler command at present
        number_of_topic_models = 1
        if resume:
            resume, topic_model_ids = c.checkpoint(
                c.are_topic_models_created, path, number_of_topic_models,
                debug=args.debug)
            if not resume:
                message = u.dated(
                    "Found %s topic models out of %s. Resuming.\n"
                    % (len(topic_model_ids),
                       number_of_topic_models))
                u.log_message(message, log_file=session_file,
                              console=args.verbosity)

            topic_models = topic_model_ids
            number_of_topic_models -= len(topic_model_ids)

        topic_model_args = r.set_topic_model_args( \
            args,
            fields=fields,
            topic_model_fields=args.topic_model_fields_)
        topic_models, topic_model_ids = r.create_topic_models( \
            datasets, topic_models,
            topic_model_args, args, api,
            path, session_file, log)
    # If a topic model is provided, we use it.
    elif args.topic_model:
        topic_model_ids = [args.topic_model]
        topic_models = topic_model_ids[:]

    elif args.topic_models or args.topic_model_tag:
        topic_models = topic_model_ids[:]

    # If we are going to predict we must retrieve the topic models
    if topic_model_ids and args.test_set:
        topic_models, topic_model_ids = r.get_topic_models(
            topic_models, args, api,
            session_file)

    return topic_models, topic_model_ids, resume


def get_topic_model_fields(topic_model, csv_properties, args):
    """Retrieves fields info from topic model resource

    """
    if not csv_properties:
        csv_properties = {}
    csv_properties.update(verbose=True)
    if args.user_locale is None:
        args.user_locale = topic_model['object'].get('locale', None)
    csv_properties.update(data_locale=args.user_locale)
    csv_properties.update(missing_tokens=DEFAULT_MISSING_TOKENS)
    return Fields(topic_model, **csv_properties)
