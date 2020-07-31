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
                           is_shared,
                           check_resource_error, log_created_resources)
from bigmler.reports import report

from bigmler.resourcesapi.common import set_basic_args, update_attributes, \
    update_json_args, configure_input_fields, \
    check_fields_struct

from bigmler.resourcesapi.common import SEED, DS_NAMES, \
    ALL_FIELDS_QS


def set_basic_dataset_args(args, name=None):
    """Return dataset basic arguments dict

    """
    if name is None:
        name = args.name
    dataset_args = set_basic_args(args, name)
    if args.sample_rate != 1 and args.no_model:
        dataset_args.update({
            "seed": SEED if args.seed is None else args.seed,
            "sample_rate": args.sample_rate
        })

    if hasattr(args, "range") and args.range_:
        dataset_args.update({
            "range": args.range_
        })
    return dataset_args


def set_dataset_args(args, fields, multi_label_data=None):
    """Return dataset arguments dict

    """
    dataset_args = set_basic_dataset_args(args)
    objective_field = (None if not hasattr(args, 'objective_field')
                       else args.objective_field)
    if multi_label_data is not None and objective_field is None:
        objective_field = multi_label_data['objective_name']
    if objective_field is not None and fields is not None:
        try:
            objective_id = fields.field_id(objective_field)
        except ValueError as exc:
            sys.exit(exc)
        dataset_args.update(objective_field={'id': objective_id})

    if hasattr(args, 'juxtapose') and args.juxtapose:
        dataset_args.update({"juxtapose": args.juxtapose})

    if hasattr(args, 'sql_query') and args.sql_query:
        dataset_args.update({"sql_query": args.sql_query})

    if hasattr(args, 'sql_output_fields_') and args.sql_output_fields_:
        dataset_args.update({"sql_output_fields": args.sql_output_fields_})

    if hasattr(args, 'json_query_') and args.json_query_:
        dataset_args.update({"json_query": args.json_query_})

    if args.json_filter:
        dataset_args.update(json_filter=args.json_filter)
    elif args.lisp_filter:
        dataset_args.update(lisp_filter=args.lisp_filter)

    if args.dataset_fields_ and fields is not None:
        input_fields = configure_input_fields(fields, args.dataset_fields_)
        dataset_args.update(input_fields=input_fields)
    if (hasattr(args, 'multi_label') and args.multi_label
            and multi_label_data is not None):
        dataset_args.update(
            user_metadata={'multi_label_data': multi_label_data})

    if fields and args.import_fields:
        fields_struct = fields.new_fields_structure(args.import_fields)
        check_fields_struct(fields_struct, "dataset")
        update_attributes(dataset_args, fields_struct)
    if 'dataset' in args.json_args:
        update_json_args(dataset_args, args.json_args.get('dataset'), fields)

    return dataset_args


def set_dataset_split_args(name, description, args, sample_rate=1,
                           out_of_bag=False, multi_label_data=None):
    """Return dataset arguments dict to split a dataset

    """
    dataset_args = {
        "name": name,
        "description": description,
        "category": args.category,
        "tags": args.tag,
        "seed": SEED if args.seed is None else args.seed,
        "sample_rate": sample_rate,
        "out_of_bag": out_of_bag
    }

    if hasattr(args, "range") and args.range_:
        dataset_args.update({
            "range": args.range_
        })
    if (hasattr(args, "multi_label") and
            args.multi_label and multi_label_data is not None):
        dataset_args.update(
            user_metadata={'multi_label_data': multi_label_data})

    return dataset_args


def create_dataset(origin_resource, dataset_args, args, api=None,
                   path=None, session_file=None, log=None, dataset_type=None):
    """Creates remote dataset from source, dataset, cluster or datasets list

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Creating dataset.\n")
    log_message(message, log_file=session_file, console=args.verbosity)
    check_fields_struct(dataset_args, "dataset")

    # if --json-query or --sql-query are used and no names are set for
    # the datasets, we create default naming to A, B, C, etc. for the datasets
    # to be used as origin

    if ((hasattr(args, 'sql_query') and args.sql_query) or \
            (hasattr(args, 'json_query') and args.sql_query)) and \
            isinstance(origin_resource, list) and \
            ((not isinstance(origin_resource[0], dict)) or \
            origin_resource[0].get("name") is None):
        for index, element in enumerate(origin_resource):
            if index < len(DS_NAMES):
                if isinstance(element, dict):
                    if element.get("resource") is not None:
                        element = {"id": element["resource"]}
                    element.update({"name": DS_NAMES[index]})
                    origin_resource[index] = element
                elif isinstance(element, str):
                    origin_resource[index] = {"id": element,
                                              "name": DS_NAMES[index]}

    dataset = api.create_dataset(origin_resource, dataset_args, retries=None)
    suffix = "_" + dataset_type if dataset_type else ""
    log_created_resources("dataset%s" % suffix, path,
                          bigml.api.get_dataset_id(dataset), mode='a')
    dataset_id = check_resource_error(dataset, "Failed to create dataset: ")
    try:
        dataset = check_resource(dataset, api.get_dataset,
                                 query_string=ALL_FIELDS_QS,
                                 raise_on_error=True)
    except Exception as exception:
        sys.exit("Failed to get a finished dataset: %s" % str(exception))
    message = dated("Dataset created: %s\n" % get_url(dataset))
    log_message(message, log_file=session_file, console=args.verbosity)
    log_message("%s\n" % dataset_id, log_file=log)
    if args.reports:
        report(args.reports, path, dataset)
    return dataset


def get_dataset(dataset, api=None, verbosity=True, session_file=None):
    """Retrieves the dataset in its actual state

    """
    if api is None:
        api = bigml.api.BigML()
    if (isinstance(dataset, str) or
            bigml.api.get_status(dataset)['code'] != bigml.api.FINISHED):
        message = dated("Retrieving dataset. %s\n" %
                        get_url(dataset))
        log_message(message, log_file=session_file,
                    console=verbosity)
        dataset = check_resource(dataset, api.get_dataset,
                                 query_string=ALL_FIELDS_QS)
        check_resource_error(dataset, "Failed to get dataset: ")
    return dataset


def publish_dataset(dataset, args, api=None, session_file=None):
    """Publishes dataset and sets its price (if any)

    """
    if api is None:
        api = bigml.api.BigML()
    public_dataset = {"private": False}
    if args.dataset_price:
        public_dataset.update(price=args.dataset_price)
    dataset = update_dataset(dataset, public_dataset, args, api=api,
                             session_file=session_file)
    check_resource_error(dataset, "Failed to update dataset: ")
    dataset = check_resource(dataset, api.get_dataset,
                             query_string=ALL_FIELDS_QS)
    return dataset

def update_dataset(dataset, dataset_args, args,
                   api=None, path=None, session_file=None):
    """Updates dataset properties

    """
    if api is None:
        api = bigml.api.BigML()
    message = dated("Updating dataset. %s\n" %
                    get_url(dataset))
    log_message(message, log_file=session_file,
                console=args.verbosity)
    dataset = api.update_dataset(dataset, dataset_args)
    if is_shared(dataset):
        message = dated("Shared dataset link. %s\n" %
                        get_url(dataset, shared=True))
        log_message(message, log_file=session_file,
                    console=args.verbosity)
        if args.reports:
            report(args.reports, path, dataset)
    check_resource_error(dataset, "Failed to update dataset: ")
    dataset = check_resource(dataset, api.get_dataset,
                             query_string=ALL_FIELDS_QS)

    return dataset
