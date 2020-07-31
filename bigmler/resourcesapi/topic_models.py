# -*- coding: utf-8 -*-
#
# Copyright 2020 BigML
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
"""Resources management functions

"""


import sys

import bigml.api

from bigmler.utils import (dated, get_url, log_message, check_resource,
                           plural, is_shared,
                           check_resource_error, log_created_resources)
from bigmler.reports import report

from bigmler.resourcesapi.common import set_basic_args, \
    configure_input_fields, update_sample_parameters_args, \
    update_json_args, wait_for_available_tasks

from bigmler.resourcesapi.common import SEED, FIELDS_QS, \
    ALL_FIELDS_QS


def set_topic_model_args(args, name=None, fields=None,
                         topic_model_fields=None):
    """Return topic_model arguments dict

    """
    if name is None:
        name = args.name
    if topic_model_fields is None:
        topic_model_fields = args.topic_model_fields_

    topic_model_args = set_basic_args(args, name)
    topic_model_args.update({
        "seed": SEED if args.seed is None else args.seed,
        "topicmodel_seed": SEED if args.seed is None else args.seed
    })

    if topic_model_fields and fields is not None:
        input_fields = configure_input_fields(fields, topic_model_fields)
        topic_model_args.update(input_fields=input_fields)
    topic_model_args.update({"sample_rate": args.sample_rate})
    topic_model_args.update({"bigrams": args.bigrams})
    topic_model_args.update({"case_sensitive": args.case_sensitive})
    if args.number_of_topics is not None:
        topic_model_args.update({"number_of_topics": args.number_of_topics})
    if args.term_limit is not None:
        topic_model_args.update({"term_limit": args.term_limit})
    if args.top_n_terms is not None:
        topic_model_args.update({"top_n_terms": args.top_n_terms})
    if args.minimum_name_terms is not None:
        topic_model_args.update({"minimum_name_terms":
                                 args.minimum_name_terms})

    if args.excluded_terms:
        topic_model_args.update({"excluded_terms": args.excluded_terms_})

    topic_model_args = update_sample_parameters_args( \
        topic_model_args, args)

    if 'topic_model' in args.json_args:
        update_json_args(topic_model_args,
                         args.json_args.get('topic_model'),
                         fields)
    return topic_model_args


def create_topic_models(datasets, topic_model_ids, topic_model_args,
                        args, api=None, path=None,
                        session_file=None, log=None):
    """Create remote topic models

    """
    if api is None:
        api = bigml.api.BigML()

    topic_models = topic_model_ids[:]
    existing_topic_models = len(topic_models)
    topic_model_args_list = []
    datasets = datasets[existing_topic_models:]
    # if resuming and all topic models were created, there will
    # be no datasets left
    if datasets:
        if isinstance(topic_model_args, list):
            topic_model_args_list = topic_model_args

        # Only one topic model per command, at present
        number_of_topic_models = 1
        message = dated("Creating %s.\n" %
                        plural("topic model", number_of_topic_models))
        log_message(message, log_file=session_file,
                    console=args.verbosity)

        query_string = FIELDS_QS
        inprogress = []
        for i in range(0, number_of_topic_models):
            wait_for_available_tasks(inprogress,
                                     args.max_parallel_topic_models,
                                     api, "topicmodel")
            if topic_model_args_list:
                topic_model_args = topic_model_args_list[i]

            topic_model = api.create_topic_model(datasets,
                                                 topic_model_args,
                                                 retries=None)
            topic_model_id = check_resource_error( \
                topic_model,
                "Failed to create topic model: ")
            log_message("%s\n" % topic_model_id, log_file=log)
            topic_model_ids.append(topic_model_id)
            inprogress.append(topic_model_id)
            topic_models.append(topic_model)
            log_created_resources("topic_models", path, topic_model_id,
                                  mode='a')

        if args.verbosity:
            if bigml.api.get_status(topic_model)['code'] != bigml.api.FINISHED:
                try:
                    topic_model = check_resource( \
                        topic_model, api.get_topic_model,
                        query_string=query_string,
                        raise_on_error=True)
                except Exception as exception:
                    sys.exit("Failed to get a finished topic model: %s" %
                             str(exception))
                topic_models[0] = topic_model
            message = dated("Topic model created: %s\n" %
                            get_url(topic_model))
            log_message(message, log_file=session_file,
                        console=args.verbosity)
            if args.reports:
                report(args.reports, path, topic_model)

    return topic_models, topic_model_ids


def get_topic_models(topic_model_ids,
                     args, api=None, session_file=None):
    """Retrieves remote topic model in its actual status

    """
    if api is None:
        api = bigml.api.BigML()

    topic_model_id = ""
    topic_models = topic_model_ids
    topic_model_id = topic_model_ids[0]
    message = dated("Retrieving %s. %s\n" %
                    (plural("topic model", len(topic_model_ids)),
                     get_url(topic_model_id)))
    log_message(message, log_file=session_file, console=args.verbosity)
    # only one topic_model at present
    try:
        # we need the whole fields structure when exporting fields
        query_string = FIELDS_QS if not args.export_fields else ALL_FIELDS_QS
        topic_model = check_resource(topic_model_ids[0],
                                     api.get_topic_model,
                                     query_string=query_string,
                                     raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a finished topic model: %s" % \
            str(exception))
    topic_models[0] = topic_model

    return topic_models, topic_model_ids


def set_publish_topic_model_args(args):
    """Set args to publish topic model

    """
    public_topic_model = {}
    if args.public_topic_model:
        public_topic_model = {"private": False}
        if args.model_price:
            public_topic_model.update(price=args.model_price)
        if args.cpp:
            public_topic_model.update(credits_per_prediction=args.cpp)
    return public_topic_model


def update_topic_model(topic_model, topic_model_args,
                       args, api=None, path=None, session_file=None):
    """Updates topic model properties

    """
    if api is None:
        api = bigml.api.BigML()

    message = dated("Updating topic model. %s\n" %
                    get_url(topic_model))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    topic_model = api.update_topic_model(topic_model, \
        topic_model_args)
    check_resource_error(topic_model,
                         "Failed to update topic model: %s"
                         % topic_model['resource'])
    topic_model = check_resource(topic_model,
                                 api.get_topic_model,
                                 query_string=FIELDS_QS,
                                 raise_on_error=True)
    if is_shared(topic_model):
        message = dated("Shared topic model link. %s\n" %
                        get_url(topic_model, shared=True))
        log_message(message, log_file=session_file, console=args.verbosity)
        if args.reports:
            report(args.reports, path, topic_model)

    return topic_model
