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

"""BigMLer - reify processing dispatching

"""
from __future__ import absolute_import

import sys
import math
import pprint
import datetime

from bigml.resourcehandler import RESOURCE_RE, RENAMED_RESOURCES
from bigml.resourcehandler import get_resource_id, get_resource_type
from bigml.fields import Fields
from bigmler.reify.reify_defaults import COMMON_DEFAULTS, DEFAULTS

ORIGINS = {
    "source": [["file_name"]],
    "dataset": [[
        "origin_batch_resource", "cluster", "datasets",
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

QS = 'limit=-1;exclude=root,trees'
pp = pprint.PrettyPrinter(indent=4)


def get_method_suffix(resource_type):
    """Returns the suffix used in the REST method

    """
    if RESOURCE_RE.get(resource_type):
        return RENAMED_RESOURCES.get(resource_type, resource_type)
    else:
        sys.exit('Non allowed resource type. Check the provided resource ID')


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
                found_origins.append((origin, info))
                break

    if not found_origins:
        sys.exit("Failed to find the complete origin information.")
    if len(found_origins) == 1:
        return found_origins[0]
    else:
        return found_origins


def get_fields_changes(resource, referrer={}):
    """Changed field attributes

    """
    fields_attributes = {}
    updatable_attrs = ["name", "label", "description"]
    resource_fields = Fields(
        {'resource': resource['resource'], 'object': resource}).fields
    if get_resource_type(resource) == 'source':
        updatable_attrs.append("optype")
    if referrer:
        referrer_fields = Fields(
            {'resource': referrer['resource'], 'object': referrer}).fields
        for field_id in resource_fields.keys():
            field_opts = {}
            if not field_id in referrer_fields.keys(): continue
            field = resource_fields[field_id]

            for attribute in updatable_attrs:
                ref_values = ["", referrer_fields[field_id].get(attribute, "")]
                if not field.get(attribute, "") in ref_values:
                    field_opts.update({attribute: field[attribute]})

            if field_opts != {}:
                fields_attributes.update({field_id: field_opts})
    return fields_attributes


def get_input_fields(resource, referrer={}):
    """New list of input fields

    """
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
            referrer_fields = referrer_fields.preferred_fields()
            referrer_fields = sorted([field['name']
                                      for _, field in referrer_fields.items()])
        else:
            referrer_fields = sorted(referrer_fields.fields_by_name.keys())
        # check referrer input fields to see if they are equal
        referrer_input_fields.append(referrer_fields)
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
            referrer_input_fields.append([name for name in referrer_fields
                                          if name != referrer_objective])
        if input_fields in referrer_input_fields:
            return []
    return input_fields_ids


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
    non_inherited_opts(resource, referrer, opts)

    # non-default create options
    non_default_opts(resource, opts)

    # changes in fields structure
    fields_attributes = get_fields_changes(resource, referrer=referrer)
    if fields_attributes:
        opts['create'].update({"fields": fields_attributes})

    # input fields
    input_fields = get_input_fields(resource, referrer=referrer)
    if input_fields:
        opts['create'].update({'input_fields': input_fields})


def common_model_opts(resource, referrer, opts, call="create"):
    """Stores the options that are commont to all the model types

    """
    common_dataset_opts(resource, referrer, opts, call=call)

    # inherited row range
    if (not resource.get('range', []) in
            [[], [1, referrer.get('rows', None)]]):
        opts['create'].update({ "range": resource['range'] })


def common_batch_options(resource, referrer1, referrer2, opts, call="create"):
    """Stores the options that are common to all batch resources

    """
    # non-inherited create options
    non_inherited_opts(resource, referrer1, opts)

    # non-default create options
    non_default_opts(resource, opts)

    # model to dataset mapping
    fields = referrer2['fields'].keys()
    default_map = dict(zip(fields, fields))
    opts['create'].update(
        default_setting(resource, 'fields_map', default_map))

    if not child.get('all_fields', False):
        opts['create'].update(
            default_setting(resource, 'output_fields', [[]]))


class ResourceMap():
    """List of resources in the reverse chain of creation

    """


    def __init__(self, api):
        """Constructor: empty list of objects

        """
        self.objects = []
        self.api = api

    def get_resource(self, resource_id):
        """Auxiliar method to retrieve resources. The query string ensures
           low bandwith usage and full fields structure.

        """

        return self.api.check_resource(
            resource_id, query_string=QS).get('object')

    def add(self, objects):
        """Extend the list of objects

        """
        for obj in objects:
            resource_id = get_resource_id(obj)
            if not resource_id in self.objects:
                self.objects.append(resource_id)

    def translate(self, buf):
        counts = {}

        for obj in reversed(self.objects):

            resource_type = get_resource_type(obj)

            if resource_type in counts:
                counts[resource_type] += 1
            else:
                counts[resource_type] = 1

            buf = buf.replace('"%s"' % obj, '%s%s' % (
                resource_type, counts[resource_type]))

        return buf

    def reify_source(self, resource):

        resource_type = get_resource_type(resource)
        child = self.get_resource(resource)

        opts = { "create": {}, "update": {}, "args": {} }

        # create options
        source_defaults = DEFAULTS[resource_type].get("create", {})
        source_defaults.update(COMMON_DEFAULTS.get("create", {}))
        # special case, souces can be named like uploaded files
        name_as_file = [child.get('file_name')]
        name_as_file.extend(source_defaults["name"])
        source_defaults["name"] = name_as_file

        for attribute, default_value in source_defaults.items():
            opts["create"].update(
                default_setting(child, attribute, *default_value))

        # update options
        source_defaults = DEFAULTS[resource_type].get("update", {})

        for attribute, default_value in source_defaults.items():
            opts["update"].update(
                default_setting(child, attribute, *default_value))

        return ([ child ], opts)

    def reify_anomalyscore(self, resource):

        child = self.get_resource(resource)
        _, parent = get_origin_info(child)

        opts = { "create": {}, "update": {}, "args": {} }

        # non-inherited create options
        non_inherited_opts(child, parent, opts)

        opts['create'].update({'input_data': child['input_data']})

        # name, exclude automatic naming alternatives
        autonames = [u'']
        autonames.append(
            u'Score for %s' % parent['name'])
        if not child.get('name', '') in autonames:
            opts['create'].update({"name": child.get('name', '')})

        return ([ child, parent ], opts)

    def reify_centroid(self, resource):

        child = self.get_resource(resource)
        _, parent = get_origin_info(child)

        opts = { "create": {}, "update": {}, "args": {} }

        # non-inherited create options
        non_inherited_opts(child, parent, opts)

        # non-default create options
        non_default_opts(child, opts)

        opts['create'].update( {'input_data': child['input_data']} )

        # name, exclude automatic naming alternatives
        autonames = [u'']
        autonames.append(
            u'Centroid for %s' % parent['name'])
        if not child.get('name', '') in autonames:
            opts['create'].update({"name": child.get('name', '')})

        # non-default update options
        non_default_opts(child, opts, call="update")

        return ([ child, parent ], opts)

    def reify_prediction(self, resource):

        child = self.get_resource(resource)
        origin, parent = get_origin_info(child)
        if origin == 'models':
            model = self.get_resource(parent[0])
            parent =  self.get_resource('ensemble/%s' % model['ensemble_id'])
        else:
            parent = self.get_resource(parent)

        opts = { "create": {}, "update": {}, "args": {} }

        # non-inherited create options
        non_inherited_opts(child, parent, opts)

        # non-default create options
        non_default_opts(child, opts)

        opts['create'].update( {'input_data': child['input_data']} )

        # name, exclude automatic naming alternatives
        autonames = [u'']
        autonames.append(
            u'Prediction for %s' % child['objective_field_name'])
        if not child.get('name', '') in autonames:
            opts['create'].update({"name": child.get('name', '')})


        return ([ child, parent ], opts)

    def reify_batchanomalyscore(self, resource):

        child = self.get_resource(resource)
        # batch resources have 2 different origins as arguments
        [(_, parent1),
         (_, parent2)] = get_origin_info(resource)
        parent1 = self.get_resource(parent1)
        parent2 = self.get_resource(parent2)

        opts = { "create": {}, "update": {}, "args": {} }

        # common create options for batch resources
        common_batch_options(child, parent1, parent2, opts)

        # name, exclude automatic naming alternatives
        autonames = [u'']
        autonames.append(
            u'Batch Anomaly Score of %s with %s' % (
                parent1.get('name', ''), parent2.get('name', '')))
        if not child.get('name', '') in autonames:
            opts['create'].update({"name": child.get('name', '')})

        if child.get('header', True):
            opts['create'].update(
                default_setting(child, 'score_name', [None, '']))

        return ([ child, parent1, parent2 ], opts)

    def reify_batchcentroid(self, resource):

        child = self.get_resource(resource)
        # batch resources have 2 different origins as arguments
        [(_, parent1),
         (_, parent2)] = get_origin_info(resource)
        parent1 = self.get_resource(parent1)
        parent2 = self.get_resource(parent2)

        opts = { "create": {}, "update": {}, "args": {} }

        # common create options for batch resources
        common_batch_options(child, parent1, parent2, opts)

        if child.get('header', True):
            opts['create'].update(
                default_setting(child, 'distance_name', [None, '']))

        # name, exclude automatic naming alternatives
        autonames = [u'']
        autonames.append(
            u'Batch Centroid of %s with %s' % (
                parent1.get('name', ''), parent2.get('name', '')))
        if not child.get('name', '') in autonames:
            opts['create'].update({"name": child.get('name', '')})


        return ([ child, parent1, parent2 ], opts)

    def reify_batchprediction(self, resource):

        child = self.get_resource(resource)
        # evalutations have 2 different origins as arguments
        [(_, parent1),
         (_, parent2)] = get_origin_info(resource)
        parent1 = self.get_resource(parent1)
        parent2 = self.get_resource(parent2)

        opts = { "create": {}, "update": {}, "args": {} }

        # common create options for batch resources
        common_batch_options(child, parent1, parent2, opts)

        if child.get('header', True):
            opts['create'].update(
                default_setting(child, 'prediction_name', [None, '']))
            opts['create'].update(
                default_setting(child, 'centroid_name', [None, '']))

        # name, exclude automatic naming alternatives
        autonames = [u'']
        autonames.append(
            u'Batch Prediction of %s with %s' % (
                parent1.get('name', ''), parent2.get('name', '')))
        if not child.get('name', '') in autonames:
            opts['create'].update({"name": child.get('name', '')})

        return ([ child, parent1, parent2 ], opts)

    def reify_evaluation(self, resource):
        """ Extracts origin resources and arguments for evaluations:
            model/ensemble, dataset and args

        """

        child = self.get_resource(resource)
        # evalutations have 2 different origins as arguments
        [(_, parent1),
         (_, parent2)] = get_origin_info(resource)
        parent1 = self.get_resource(parent1)
        parent2 = self.get_resource(parent2)


        opts = { "create": {}, "update": {}, "args": {} }

        # non-inherited create options
        non_inherited_opts(child, parent1, opts)

        # non-default create options
        non_default_opts(child, opts)

        # model/ensemble to dataset mapping
        fields = parent2['fields'].keys()
        default_map = dict(zip(fields, fields))
        opts['create'].update(
            default_setting(child, 'fields_map', default_map))

        # name, exclude automatic naming alternatives
        autonames = [u'']
        autonames.append(
            u'Evaluation of %s with %s' % (parent1.get('name', ''),
                                           parent2.get('name', '')))
        if not child.get('name', '') in autonames:
            opts['create'].update({"name": child.get('name', '')})

        # range in dataset
        if not child.get('range', []) in [[], [1, parent2.get('rows', None)]]:
            opts['create'].update({ "range": child['range'] })


        return ([ child, parent1, parent2 ], opts)


    def reify_anomaly(self, resource):
        """Extracts origin resource and arguments for anomaly detectors

        """

        child = self.get_resource(resource)
        _, parent = get_origin_info(child)
        parent = self.get_resource(parent)

        opts = { "create": {}, "update": {}, "args": {} }

        # options common to all model types
        common_model_opts(child, parent, opts)

        # name, exclude automatic naming alternatives
        autonames = [u'']
        autonames.append(
            u'%s anomaly detector' % parent.get('name', ''))
        if not child.get('name', '') in autonames:
            opts['create'].update({"name": child.get('name', '')})

        return ([ child, parent ], opts)

    def reify_cluster(self, resource):
        """Extracts origin resources and arguments for clusters

        """
        child = self.get_resource(resource)
        _, parent = get_origin_info(child)
        parent = self.get_resource(parent)

        opts = { "create": {}, "update": {}, "args": {} }

        # options common to all model types
        common_model_opts(child, parent, opts)

        if 'k' in child:
            opts['create'].update( { "k": child['k'] } )

        # name, exclude automatic naming alternatives
        autonames = [u'']
        autonames.append(
            u'%s cluster' % parent.get('name', ''))
        if not child.get('name', '') in autonames:
            opts['create'].update({"name": child.get('name', '')})

        return ([ child, parent ], opts)

    def reify_ensemble(self, resource):

        child = self.get_resource(resource)
        _, parent = get_origin_info(child)
        parent = self.get_resource(parent)

        [ family, opts ] = self.reify_model(child['models'][0])

        # create options
        non_default_opts(child, opts)

        return ([ child, parent ], opts)

    #
    # Models come from datasets OR from clusters

    def reify_model(self, resource):

        child = self.get_resource(resource)
        origin, parent = get_origin_info(child)
        parent = self.get_resource(parent)
        # as two-steps result from a cluster
        if origin in ['cluster']:
            opts['create'].update({"centroid": child['centroid']})
            origin_gp, grandparent = get_origin_info(parent)
            grandparent = self.get_resource(grandparent)
        else:
            grandparent = parent
            if (child.get('objective_field') != \
                    grandparent.get('objective_field').get('id')):
                opts['create'].update(
                    { "objective_field": child.get('objective_field') })


        opts = { "create": {}, "update": {}, "args": {} }


        # options common to all model types
        common_model_opts(child, grandparent, opts)

        # name, exclude automatic naming alternatives
        autonames = [u'']
        autonames.append(
            u"%s model" % grandparent.get('name', ''))
        autonames.append(
            u"Cluster %s - %s" % (int(child.get('centroid', "0"), base=16),
                                  parent['name']))

        if not child.get('name', '') in autonames:
            opts['create'].update({"name": child.get('name', '')})

        if child.get('randomize') == True:
            default_random_candidates = int(
                math.floor(math.sqrt(len(child['input_fields']))))
            opts['create'].update(
                default_setting(
                    child, 'random_candidates', [default_random_candidates] ))

        return ([ child, parent ], opts)

    def reify_dataset(self, resource):

        child = self.get_resource(resource)
        grandparent = {}
        parent = {}
        origin, parent = get_origin_info(child)
        parent = self.get_resource(parent)
        # as two-steps result from a cluster or batch prediction, centroid
        # or anomaly score
        if origin in ['origin_batch_resource', 'cluster']:
            if origin == "cluster":
                opts['args'].update( { "centroid": child['centroid'] } )
            origin_gp, grandparent = get_origin_info(parent)
            grandparent = self.get_resource(grandparent)
        else:
            grandparent = parent


        opts = { "create": {}, "update": {}, "args": {} }


        # options common to all model types
        common_dataset_opts(child, grandparent, opts)

        # update options
        dataset_defaults = DEFAULTS["dataset"].get("update", {})
        dataset_defaults.update(COMMON_DEFAULTS.get("update", {}))

        for attribute, default_value in dataset_defaults.items():
            opts["update"].update(
                default_setting(child, attribute, *default_value))

        # name, exclude automatic naming alternatives
        autonames = [u'']
        suffixes = ["filtered", "sampled", "dataset", "extended",
                    "- batchprediction", "- batchanomalyscore",
                    "- batchcentroid" ]
        autonames.extend([u'%s %s' % (grandparent.get('name', ''), suffix)
                          for suffix in suffixes])
        autonames.append(
            u"%s' dataset" % '.'.join(parent['name'].split('.')[0:-1]))
        autonames.append(
            u"Cluster %s - %s" % (int(child.get('centroid', "0"), base=16),
                                  parent['name']))
        autonames.append(
            u"Dataset from %s model - segment" % parent['name'])
        if not child.get('name', '') in autonames:
            opts['create'].update({"name": child.get('name', '')})

        # objective field
        resource_fields = Fields(
            {'resource': child['resource'], 'object': child})
        objective_id = child['objective_field']['id']
        preferred_fields = resource_fields.preferred_fields()
        max_column = sorted([field['column_number']
                             for _, field in preferred_fields.items()],
                            reverse=True)[0]
        objective_column = preferred_fields[objective_id]['column_number']
        if objective_column != max_column:
            opts['create'].update({ "objective_field": { "id": objective_id}})

        # resize
        if (child['size'] != grandparent['size'] and
            get_resource_type(parent) == 'source'):
            opts['create'].update({"size": child['size']})

        # generated fields
        if child.get('new_fields', None):
            new_fields = child['new_fields']
            for new_field in new_fields:
                new_field['field'] = new_field['generator']
                del(new_field['generator'])

            opts['create'].update({ "new_fields": new_fields })

        if not child.get('range', []) in [ [], [1, grandparent.get('rows', None)] ]:
            opts['create'].update({ "range": child['range'] })
        return ([ child, parent ], opts)


def build_reification(family, opts):

    child = family[0]
    parents = family[1:]


    resource_type = get_resource_type(child)
    reification = '"%s" = api.create_%s(' % (child['resource'],
                                             get_method_suffix(resource_type))

    if resource_type == "source":
        if child.get('remote') != None:
            source = child['remote']
        elif child.get('file_name') != None:
            source = child['file_name']
        else:
            source = "UNKNOWN-INLINE-DATA"

        reification += '"%s"' % source

    else:
        reification += ', '.join([ '"%s"' % parent.get('resource', parent) for parent in parents ])

    if opts['create'] != {}:
        reification += ', %s' % opts['create']

    if opts['args'] != {}:
        reification += ', args=%s' % opts['args']

    reification += ')'

    if opts['update'] != {}:
        reification += '\n"%s" = api.update_%s(%s)' % ( child['resource'], resource_type, opts['update'] )

    return reification

def inherit_setting(relative, child, key, default):

    if not child.get(key, default) in [ default, relative.get(key, default) ]:
        return { key: child.get(key) }
    else:
        return {}

def default_setting(child, key, *defaults):

    if isinstance(defaults, basestring):
        defaults = [ defaults ]

    if not child.get(key, defaults[0]) in defaults:
        return { key: child[key] }
    else:
        return {}



def unique_buffer(line_buffer):

    new_buffer = []

    for line in line_buffer.splitlines():
        if not line in new_buffer:
            new_buffer.append(line)

    return '\n'.join(new_buffer)

#
# We reify recursively until we get to a source.
#

def reify_object(resource_id, resource_map, reification=""):

    resource_type = get_resource_type(resource_id)

    reify_handler = getattr(resource_map, 'reify_%s' % resource_type)

    [ family, opts ] = reify_handler(resource_id)

    resource_map.add(family)

    reification = build_reification(family, opts) + '\n' + reification

    if resource_type != "source":

        for parent in family[1:]:
            reification = 'api.ok("%s")\n' % parent['resource'] + reification
            [ new_reification, resource_map ] = reify_object(parent['resource'], resource_map)
            reification = new_reification + '\n' + reification

    return (reification, resource_map)

#############

def reify_resources(args, api):
    """ Extracts the properties of the created resources and generates
        code to rebuild them
    """

    resource_map = ResourceMap(api)
#obj = sys.argv[1]

    resource_id = get_resource_id(args.resource_id)
    if resource_id is None:
        sys.exit("No resource was found for this resource id: %s" % args.id)

    [ reification, resource_map ] = reify_object(resource_id, resource_map )
    print resource_map.translate(unique_buffer(reification))
