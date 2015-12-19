# -*- coding: utf-8 -*-
#
# Copyright 2015 BigML
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

"""Auxiliary RESTChain utils that abstract the steps to reify resources

"""

from __future__ import absolute_import

import sys


from bigml.resourcehandler import get_resource_type
from bigml.fields import Fields

from bigmler.reify.restcall import RESTCall
from bigmler.reify.reify_defaults import COMMON_DEFAULTS, DEFAULTS

DEFAULT_UPDATABLE = ["name", "label", "description"]

SOURCE_UPDATABLE = ["name", "label", "description", "optype"]

ORIGINS = {
    "source": [["file_name"]],
    "dataset": [[
        "origin_batch_resource", "cluster", "ranges",
        "origin_dataset", "source"]],
    "model": [["cluster", "datasets", "dataset"]],
    "ensemble": [["datasets", "dataset"]],
    "cluster": [["datasets", "dataset"]],
    "anomaly": [["datasets", "dataset"]],
    "prediction": [["models", "model"]],
    "centroid": [["cluster"]],
    "anomalyscore": [["anomaly"]],
    "evaluation": [["ensemble", "model"], ["dataset"]],
    "batchprediction": [["models", "model"], ["dataset"]],
    "batchcentroid": [["cluster"], ["dataset"]],
    "batchanomalyscore": [["anomaly"], ["dataset"]]
}


def get_origin_info(resource):
    """Key and value that stores the origin resource id

    """
    resource_type = get_resource_type(resource)
    origins = ORIGINS.get(resource_type, [])
    found_origins = []
    for argument_origins in origins:
        for origin in argument_origins:
            info = resource.get(origin)
            if info:
                if origin == 'ranges':
                    info = info.keys()
                found_origins.append((origin, info))
                break

    if not found_origins:
        sys.exit("Failed to find the complete origin information.")
    if len(found_origins) == 1:
        return found_origins[0]
    else:
        return found_origins


def get_fields_changes(resource, referrer=None,
                       updatable_attrs=DEFAULT_UPDATABLE):
    """Changed field attributes

    """
    if referrer is None:
        referrer = {}
    fields_attributes = {}

    resource_fields = Fields(
        {'resource': resource['resource'], 'object': resource}).fields
    resource_type = get_resource_type(resource)
    # for sources, extract all the updatable attributes
    if get_resource_type(resource) == 'source':
        updatable_attrs = SOURCE_UPDATABLE
        for field_id in resource_fields.keys():
            field_opts = {}
            field = resource_fields[field_id]
            for attribute in updatable_attrs:
                if field.get(attribute):
                    field_opts.update({attribute: field[attribute]})
            if field_opts != {}:
                fields_attributes.update({field_id: field_opts})
        return fields_attributes
    # for the rest of resources, check which attributes changed
    if referrer:
        referrer_fields = Fields(
            {'resource': referrer['resource'], 'object': referrer}).fields
        for field_id in resource_fields.keys():
            field_opts = {}
            if not field_id in referrer_fields.keys():
                continue
            field = resource_fields[field_id]

            for attribute in updatable_attrs:
                ref_values = ["", referrer_fields[field_id].get(attribute, "")]
                if not field.get(attribute, "") in ref_values:
                    field_opts.update({attribute: field[attribute]})

            if field_opts != {}:
                fields_attributes.update({field_id: field_opts})
    return fields_attributes


def get_input_fields(resource, referrer=None):
    """New list of input fields

    """
    if referrer is None:
        referrer = {}
    input_fields_ids = resource.get('input_fields', [])
    if referrer:
        referrer_input_fields = [[]]
        # compare fields by name
        resource_fields = Fields(
            {'resource': resource['resource'], 'object': resource})
        referrer_fields = Fields(
            {'resource': referrer['resource'], 'object': referrer})
        input_fields = [resource_fields.field_name(field_id) for field_id in
                        input_fields_ids]
        input_fields = sorted(input_fields)
        referrer_type = get_resource_type(referrer)
        if referrer_type == 'dataset':
            referrer_fields = Fields(referrer_fields.preferred_fields())
            referrer_fields_names = sorted( \
                [field['name'] for _, field in referrer_fields.fields.items()])
        else:
            referrer_fields_names = sorted( \
                referrer_fields.fields_by_name.keys())
        # check referrer input fields to see if they are equal
        referrer_input_fields.append(referrer_fields_names)
        # check whether the resource has an objective field not included in
        # the input fields list
        resource_type = get_resource_type(resource)
        if resource_type == 'model':
            objective_id = resource.get('objective_field')
            try:
                objective_id = objective_id.get('id')
            except AttributeError:
                pass
            referrer_objective = resource_fields.field_name(
                objective_id)
            referrer_input_fields.append([name for name in
                                          referrer_fields_names
                                          if name != referrer_objective])
        if input_fields in referrer_input_fields:
            return []
    return referrer_fields.fields.keys()


def non_inherited_opts(resource, referrer, opts, call="create"):
    """Stores the options that have not been inherited from origin resources

    """
    for attribute, default_value in COMMON_DEFAULTS[call].items():
        opts[call].update(
            inherit_setting(
                referrer, resource, attribute, default_value[0]))


def non_default_opts(resource, opts, call="create"):
    """Stores the options that are not constant defaults

    """
    resource_type = get_resource_type(resource)
    defaults = DEFAULTS[resource_type].get(call, {})
    for attribute, default_value in defaults.items():
        opts[call].update(
            default_setting(resource, attribute, *default_value))



def common_dataset_opts(resource, referrer, opts, call="create"):
    """Stores the options that are common to all dataset and model types

    """
    # not inherited create options
    non_inherited_opts(resource, referrer, opts, call=call)
    # non-default create options
    non_default_opts(resource, opts, call=call)
    # changes in fields structure
    fields_attributes = get_fields_changes(resource, referrer=referrer)
    if fields_attributes:
        opts[call].update({"fields": fields_attributes})
    if call == "create":
        # input fields
        input_fields = get_input_fields(resource, referrer=referrer)
        if input_fields:
            opts[call].update({'input_fields': input_fields})


def range_opts(resource, referrer, opts, call="create"):
    """Stores the range option

    """
    # inherited row range
    if resource.get('ranges'):
        rows = sum([row_range[1][1] for
                    row_range in resource.get('ranges').items()])
        if resource.get('range') != [1, rows]:
            opts[call].update({"range": resource['range']})
    elif not resource.get('range', []) in \
            [[], [1, referrer.get('rows', None)]]:
        opts[call].update({"range": resource['range']})


def common_model_opts(resource, referrer, opts, call="create"):
    """Stores the options that are commont to all the model types

    """
    common_dataset_opts(resource, referrer, opts, call=call)

    # inherited row range
    range_opts(resource, referrer, opts, call=call)


def common_batch_options(resource, referrer1, referrer2, opts, call="create"):
    """Stores the options that are common to all batch resources

    """
    # non-inherited create options
    non_inherited_opts(resource, referrer1, opts, call=call)

    # non-default create options
    non_default_opts(resource, opts, call=call)

    # model to dataset mapping
    fields = referrer2['fields'].keys()
    default_map = dict(zip(fields, fields))
    opts[call].update(
        default_setting(resource, 'fields_map', default_map))


def get_resource_alias(resource_id, counts, alias):
    """Creates a human-friendly alias for the resource

    """
    if alias.get(resource_id):
        return alias.get(resource_id)
    else:
        resource_type = get_resource_type(resource_id)
        if resource_type in counts:
            counts[resource_type] += 1
        else:
            counts[resource_type] = 1
        new_alias = "%s%s" % (resource_type, counts[resource_type])
        alias[resource_id] = new_alias
        return new_alias


def inherit_setting(relative, child, key, default):
    """Returns setting only in case it was not inherited from ancestors

    """
    if not child.get(key, default) in [default, relative.get(key, default)]:
        return {key: child.get(key)}
    else:
        return {}


def default_setting(child, key, *defaults):
    """Returns setting only if it is not a default value

    """

    if isinstance(defaults, basestring):
        defaults = [defaults]
    if not child.get(key, defaults[0]) in defaults:
        return {key: child[key]}
    else:
        return {}


def non_automatic_name(resource, opts, autonames=None, autoname=None,
                       call="create"):
    """Checks whether the name of the resource is in the list of automated
       names and includes it in the name argument otherwise.

    """
    if autonames is None:
        autonames = [u'']
    if autoname is not None:
        autonames.append(autoname)
    if not resource.get('name', '') in autonames:
        opts[call].update({"name": resource.get('name', '')})


def build_calls(resource_id, origin_ids, opts, suffix=None):
    """Builds the REST API call objects to obtain the resource

    """
    calls = []
    if not suffix:
        calls.append(
            RESTCall("create",
                     origins=origin_ids,
                     args=opts["create"], resource_id=resource_id))
    if (not opts["create"] and opts["update"]) or opts.get("get"):
        calls.append(
            RESTCall("get",
                     origins=origin_ids,
                     args=opts["get"], resource_id=resource_id, suffix=suffix))
    if opts["update"]:
        calls.append(
            RESTCall("update", args=opts["update"],
                     resource_id=resource_id))
    return calls
