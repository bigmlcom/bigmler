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
"""Common Resource management functions

"""


import sys
import time

try:
    import simplejson as json
except ImportError:
    import json

import bigml.api

from bigml.util import bigml_locale
from bigml.multivote import THRESHOLD_CODE
from bigml.constants import EXTERNAL_CONNECTION_ATTRS
from bigml.api_handlers.externalconnectorhandler import get_env_connection_info

from bigmler.utils import (dated, get_url, log_message, plural, check_resource,
                           check_resource_error, log_created_resources,
                           transform_fields_keys, is_shared, FILE_ENCODING)
from bigmler.labels import label_model_args, get_all_labels
from bigmler.reports import report


EVALUATE_SAMPLE_RATE = 0.8
SEED = "BigML, Machine Learning made easy"
LOCALE_DEFAULT = "en_US"
FIELDS_QS = 'only_model=true'
ALL_FIELDS_QS = "limit=-1"
ADD_PREFIX = '+'
REMOVE_PREFIX = '-'
ADD_REMOVE_PREFIX = [ADD_PREFIX, REMOVE_PREFIX]
BRIEF_FORMAT = 'brief'
NORMAL_FORMAT = 'normal'
FULL_FORMAT = 'full'
VALID_FIELD_ATTRIBUTES = {
    "source": ["name", "label", "description", "optype", "term_analysis"],
    "dataset": ["name", "label", "description", "preferred", "term_analysis"]}
BOOSTING_OPTIONS = ["iterations", "early_holdout", "learning_rate", \
    "early_out_of_bag", "step_out_of_bag"]
DS_NAMES = "ABCDEFGHIJKLMNOPQRSTUVXYZ"


def get_basic_seed(order):
    """ Builds a standard seed from a text adding the order

    """
    return "%s - %s" % (SEED, order)


def shared_changed(shared, resource):
    """Returns True if the shared status of the resource differs from the user
       given value

    """
    return is_shared(resource) != shared


def configure_input_fields(fields, user_given_fields, by_name=False):
    """ Returns the input fields used in the new resource creation as given

        The user can choose to write all the fields that will be used in the
        new resource or modify the set of fields retrieved from the
        resource that will be used to create the new one.
    """
    def modify_input_fields(prefix, field, input_fields):
        """Adds or removes according to the prefix in the given field
           this field from the list of input fields.

        """
        if prefix == ADD_PREFIX:
            if not field in input_fields:
                input_fields.append(field)
        elif field in input_fields:
            input_fields.remove(field)

    # case of adding and removing fields to the dataset preferred field set
    if all([name[0] in ADD_REMOVE_PREFIX for name in user_given_fields]):
        preferred_fields = fields.preferred_fields()
        input_fields = list(preferred_fields.keys())
        if by_name:
            input_fields = [fields.field_name(field_id) for field_id in
                            input_fields]
        for name in user_given_fields:
            prefix = name[0]
            field_name = name[1:]
            if by_name:
                modify_input_fields(prefix, field_name, input_fields)
            else:
                try:
                    field_id = fields.field_id(field_name)
                except ValueError as exc:
                    sys.exit(exc)
                modify_input_fields(prefix, field_id, input_fields)
    # case of user given entire list of fields
    else:
        if by_name:
            return user_given_fields
        else:
            input_fields = []
            for name in user_given_fields:
                try:
                    input_fields.append(fields.field_id(name))
                except ValueError as exc:
                    sys.exit(exc)
    return input_fields


def utf8(text):
    """Encodes using the global FILE_ENCODING

    """
    return text.encode(FILE_ENCODING)

def update_attributes(updatable_attributes, new_attributes, by_column=False,
                      fields=None):
    """Correctly merging the "fields" attribute substructure in updates.

       updatable_attributes: previous attributes to be updated
       new_attributes: updates to be added
       by_column: set to True is keys are the column position of the field
       fields: Fields object info
    """
    if new_attributes:
        fields_substructure = updatable_attributes.get("fields", {})
        field_attributes = new_attributes.get("fields", {})
        if field_attributes and (not by_column or fields):
            for field_key, value in list(field_attributes.items()):
                field_id = (field_key if not by_column
                            else fields.field_id(field_key))
                if not field_id in list(fields_substructure.keys()):
                    fields_substructure.update({field_id: {}})
                fields_substructure[field_id].update(value)
            updatable_attributes.update({"fields": fields_substructure})
        else:
            updatable_attributes.update(new_attributes)


def update_json_args(resource_attributes, json_attributes, fields=None):
    """Updating the resource attributes with the contents of a JSON file

    """
    if fields is not None:
        # transforms the fields structure changes if columns are used as keys
        json_attributes = transform_fields_keys(json_attributes, fields)
    update_attributes(resource_attributes, json_attributes)


def relative_input_fields(fields, user_given_fields):
    """Returns the user given input fields using relative syntax

    """

    input_fields = []
    if all([(name[0] in ADD_REMOVE_PREFIX) for name in user_given_fields]):
        return user_given_fields

    preferred_fields = fields.preferred_fields()
    for field_id in list(preferred_fields.keys()):
        name = fields.fields[field_id]['name']
        if not name in user_given_fields:
            input_fields.append("%s%s" % (REMOVE_PREFIX, name))
    for name in user_given_fields:
        try:
            field_id = fields.field_id(name)
        except ValueError as exc:
            sys.exit(exc)
        input_fields.append("%s%s" % (ADD_PREFIX, name))

    return input_fields


def wait_for_available_tasks(inprogress, max_parallel, api,
                             resource_type, wait_step=2):
    """According to the max_parallel number of parallel resources to be
       created, when the number of in progress resources reaches the limit,
       it checks the ones in inprogress to see if there's a
       FINISHED or FAULTY resource. If found, it is removed from the
       inprogress list and returns to allow another one to be created.

    """

    check_kwargs = {"retries": 0, "query_string": "full=false", "api": api}
    while len(inprogress) == max_parallel:
        for j in range(0, len(inprogress)):
            try:
                ready = check_resource(inprogress[j], **check_kwargs)
                status = bigml.api.get_status(ready)
                if status['code'] == bigml.api.FINISHED:
                    del inprogress[j]
                    return
                elif status['code'] == bigml.api.FAULTY:
                    raise ValueError(status['message'])
            except ValueError as exception:
                sys.exit("Failed to get a finished %s: %s" %
                         (resource_type, str(exception)))
        time.sleep(max_parallel * wait_step)


def check_fields_struct(update_args, resource_type):
    """In case the args to update have a `fields` attribute, it checks the
    structure in this attribute and removes the attributes for each field
    that will not be accepted by the API.
    """
    if "fields" in update_args:
        fields_substr = update_args.get("fields")
        for _, field in list(fields_substr.items()):
            attributes = list(field.keys())
            for attribute in attributes:
                if not attribute in VALID_FIELD_ATTRIBUTES.get(resource_type):
                    del field[attribute]


def set_basic_args(args, name):
    """Sets the basic arguments, common to all resources

    """
    return {
        "name": name,
        "description": args.description_,
        "category": args.category,
        "tags": args.tag}


def set_basic_model_args(args, name):
    """Sets the additional args common to all models

    """
    model_args = set_basic_args(args, name)
    if args.default_numeric_value is not None:
        model_args.update({ \
            "default_numeric_value": args.default_numeric_value})
    return model_args


def set_basic_batch_args(args, name):
    """Sets the additional args common to all batch resources

    """
    batch_args = set_basic_args(args, name)
    header = (hasattr(args, "prediction_header") and args.prediction_header) \
        or (hasattr(args, "projection_header") and args.projection_header)
    batch_args.update({ \
        "header": header,
        "output_dataset": args.to_dataset
    })
    return batch_args


def map_fields(fields_map, model_fields, dataset_fields):
    """Build a dict to map model to dataset fields

    """
    update_map = {}
    for (model_column, dataset_column) in fields_map.items():
        try:
            update_map.update({
                model_fields.field_id(model_column):
                dataset_fields.field_id(dataset_column)})
        except ValueError as exc:
            sys.exit(exc)

    return update_map


def update_sample_parameters_args(resource_args, args):
    """Updates the information related to the common sampling options

    """
    if args.sample_rate != 1:
        resource_args.update({"sample_rate": args.sample_rate})
        if hasattr(args, "out_of_bag") and args.out_of_bag:
            resource_args.update({"out_of_bag": True})
    if hasattr(args, "replacement") and args.replacement:
        resource_args.update({"replacement": True})
    if hasattr(args, "randomize") and args.randomize:
        resource_args.update({"randomize": True})
    return resource_args


def save_txt_and_json(object_dict, output, api=None):
    """Saves in txt and JSON format the contents of a dict object

    """
    open_mode = 'wt'
    message = json.dumps(object_dict)
    with open(output + '.json', open_mode) as dict_json:
        dict_json.write(message)
    with open(output + '.txt', open_mode) as dict_txt:
        api.pprint(object_dict, dict_txt)
