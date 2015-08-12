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

from bigml.resourcehandler import RESOURCE_RE, RENAMED_RESOURCES
from bigml.resourcehandler import get_resource_id, get_resource_type
from bigml.fields import Fields
from bigmler.reify.reify_defaults import COMMON_DEFAULTS, DEFAULTS

ORIGINS = {
    "source": [["file_name"]],
    "dataset": [[
        "origin_batch_resource", "cluster", "datasets",
        "origin_dataset", "source"]],
    "model": [["cluster", "dataset", "datasets"]],
    "ensemble": [["dataset", "datasets"]],
    "cluster": [["dataset", "datasets"]],
    "anomaly": [["dataset", "datasets"]],
    "prediction": [["model", "ensemble"], ["input_data"]],
    "centroid": [["cluster"], ["input_data"]],
    "anomalyscore": [["anomaly"], ["input_data"]],
    "evaluation": [["model", "ensemble"], ["dataset"]],
    "batchprediction": [["model", "ensemble"], ["dataset"]],
    "batchcentroid": [["cluster"], ["dataset"]],
    "batchanomalyscore": [["anomaly"], ["dataset"]]
}


pp = pprint.PrettyPrinter(indent=4)


def get_method_suffix(resource_type):
    """Returns the suffix used in the REST method

    """
    if RESOURCE_RE.get(resource_type):
        return RENAMED_RESOURCES.get(resource_type, resource_type)
    else:
        sys.exit('Non allowed resource type. Check the provided resource ID')


def get_origin_info(resource, argument=0):
    """Key and value that stores the origin resource id

    """
    resource_type = get_resource_type(resource)
    for origin in ORIGINS.get(resource_type, [])[argument]:
        info = (origin, resource.get(origin))
        if info[1] is not None:
            return info


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
        # compare fields by name
        resource_fields = Fields(
            {'resource': resource['resource'], 'object': resource})
        referrer_fields = Fields(
            {'resource': referrer['resource'], 'object': referrer})
        input_fields = [resource_fields.field_name(field_id) for field_id in
                        input_fields_ids]
        input_fields = sorted(input_fields)
        if input_fields in [[], sorted(referrer_fields.fields_by_name.keys())]:
            return []
    return input_fields_ids


class ResourceMap():
    """List of resources in the reverse chain of creation

    """


    def __init__(self, api):
        """Constructor: empty list of objects

        """
        self.objects = []
        self.api = api

    def get_resource(self, resource_id):
        return self.api.check_resource(resource_id).get('object')

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

            buf = buf.replace('"%s"' % obj, '%s%s' % ( resource_type, counts[resource_type] ))

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
            opts["create"].update( default_setting(child, attribute, *default_value))

        # update options
        source_defaults = DEFAULTS[resource_type].get("update", {})
        source_defaults.update(COMMON_DEFAULTS.get("update", {}))

        for attribute, default_value in source_defaults.items():
            opts["update"].update( default_setting(child, attribute, *default_value))

        return ([ child ], opts)

    def reify_anomalyscore(self, resource):

        child = self.get_resource(resource)
        parent = self.get_resource(child['anomaly'])

        opts = { "create": {}, "update": {}, "args": {} }

        opts['create'].update( inherit_setting(parent, child, 'category', 0) )
        opts['create'].update( inherit_setting(parent, child, 'description', '') )
        opts['create'].update( {'input_data': child['input_data']} )

        if not child.get('name', '') in [ '', 'Score for %s' % parent['name'] ]:
            opts['create'].update({ "name": child['name'] })

        opts['create'].update( inherit_setting(parent, child, 'tags', []) )

        return ([ child, parent ], opts)

    def reify_centroid(self, resource):

        child = self.get_resource(resource)
        parent = self.get_resource(child['cluster'])

        opts = { "create": {}, "update": {}, "args": {} }

        opts['create'].update( inherit_setting(parent, child, 'category', 0) )
        opts['create'].update( inherit_setting(parent, child, 'description', '') )
        opts['create'].update( {'input_data': child['input_data']} )

        opts['create'].update( default_setting(child, 'missing_strategy', 0) )

        if not child.get('name', '') in [ '', 'Centroid for %s' % parent['name'] ]:
            opts['create'].update({ "name": child['name'] })

        opts['update'].update( default_setting(child, 'private', True) )
        opts['create'].update( inherit_setting(parent, child, 'tags', []) )

        return ([ child, parent ], opts)

    def reify_prediction(self, resource):

        child = self.get_resource(resource)

        if child.get('models', '') != '':
            parent = self.get_resource('ensemble/%s' % self.get_resource(child['models'][0])['ensemble_id'])
        elif child.get('model', '') != '':
            parent = self.get_resource(child['model'])
        else:
            raise Exception("Prediction does not have a valid parent?")

        opts = { "create": {}, "update": {}, "args": {} }

        opts['create'].update( inherit_setting(parent, child, 'category', 0) )
        opts['create'].update( default_setting(child, 'combiner', 0, None) )
        opts['create'].update( inherit_setting(parent, child, 'description', '') )

        opts['create'].update( {'input_data': child['input_data']} )

        opts['create'].update( default_setting(child, 'missing_strategy', 0) )

        if not child.get('name', '') in [ '', 'Prediction for %s' % child['objective_field_name'] ]:
            opts['create'].update({ "name": child['name'] })

        opts['update'].update( default_setting(child, 'private', True) )
        opts['create'].update( inherit_setting(parent, child, 'tags', []) )
        opts['update'].update( default_setting(child, 'threshold', None, {}) )

        return ([ child, parent ], opts)

    def reify_batchanomalyscore(self, resource):

        child = self.get_resource(resource)
        parentB = self.get_resource(child['dataset'])
        parentA = self.get_resource(child['anomaly'])

        opts = { "create": {}, "update": {}, "args": {} }

        opts['create'].update( default_setting(child, 'all_fields', False) )
        opts['create'].update( inherit_setting(parentA, child, 'category', 0) )
        opts['create'].update( inherit_setting(parentA, child, 'description', '') )

        default_map = dict([ (el, el) for el in parentB['fields'] ])
        opts['create'].update( default_setting(child, 'fields_map', default_map) )

        opts['create'].update( default_setting(child, 'header', True) )

        if not child.get('name', '') in [ '', 'Batch Anomaly Score of %s with %s' % ( parentA.get('name', ''), parentB.get('name', '')) ]:
            opts['create'].update({ "name": child['name'] })

        opts['create'].update( default_setting(child, 'output_dataset', False) )

        if child.get('all_fields', False) == False:
            opts['create'].update( default_setting(child, 'output_fields', []) )

        if child.get('header', True) == True:
            opts['create'].update( default_setting(child, 'score_name', None, '') )

        opts['create'].update( default_setting(child, 'separator', ',') )
        opts['create'].update( inherit_setting(parentA, child, 'tags', []) )

        return ([ child, parentA, parentB ], opts)

    def reify_batchcentroid(self, resource):

        child = self.get_resource(resource)
        parentB = self.get_resource(child['dataset'])
        parentA = self.get_resource(child['cluster'])

        opts = { "create": {}, "update": {}, "args": {} }

        opts['create'].update( default_setting(child, 'all_fields', False) )
        opts['create'].update( inherit_setting(parentA, child, 'category', 0) )
        opts['create'].update( default_setting(child, 'distance', False) )

        if child.get('header', True) == True:
            opts['create'].update( default_setting(child, 'distance_name', None, '') )
            opts['create'].update( default_setting(child, 'centroid_name', None, '') )

        opts['create'].update( inherit_setting(parentA, child, 'description', '') )

        default_map = dict([ (el, el) for el in parentB['fields'] ])
        opts['create'].update( default_setting(child, 'fields_map', default_map) )

        opts['create'].update( default_setting(child, 'header', True) )

        if not child.get('name', '') in [ '', 'Batch Centroid of %s with %s' % ( parentA.get('name', ''), parentB.get('name', '')) ]:
            opts['create'].update({ "name": child['name'] })

        opts['create'].update( default_setting(child, 'output_dataset', False) )

        if child.get('all_fields', False) == False:
            opts['create'].update( default_setting(child, 'output_fields', []) )

        opts['create'].update( default_setting(child, 'separator', ',') )
        opts['create'].update( inherit_setting(parentA, child, 'tags', []) )

        return ([ child, parentA, parentB ], opts)

    def reify_batchprediction(self, resource):

        child = self.get_resource(resource)
        parentB = self.get_resource(child['dataset'])

        if child['model'] != "":
            parentA = self.get_resource(child['model'])
        elif child['ensemble'] != "":
            parentA = self.get_resource(child['ensemble'])
        else:
            raise Exception("Ensemble does not have a valid parent?")

        opts = { "create": {}, "update": {}, "args": {} }

        opts['create'].update( default_setting(child, 'all_fields', False) )
        opts['create'].update( inherit_setting(parentA, child, 'category', 0) )
        opts['create'].update( default_setting(child, 'confidence_threshold', None) )
        opts['create'].update( default_setting(child, 'combiner', 0, None) )
        opts['create'].update( default_setting(child, 'confidence', False) )
        opts['create'].update( default_setting(child, 'confidence_name', None, '') )
        opts['create'].update( inherit_setting(parentA, child, 'description', '') )

        default_map = dict([ (el, el) for el in parentB['fields'] ])
        opts['create'].update( default_setting(child, 'fields_map', default_map) )

        opts['create'].update( default_setting(child, 'header', True) )
        opts['create'].update( default_setting(child, 'missing_strategy', 0) )

        if not child.get('name', '') in [ '', 'Batch Prediction of %s with %s' % ( parentA.get('name', ''), parentB.get('name', '')) ]:
            opts['create'].update({ "name": child['name'] })

        opts['create'].update( default_setting(child, 'negative_class', None) )
        opts['create'].update( default_setting(child, 'negative_class_confidence', None) )
        opts['create'].update( default_setting(child, 'output_dataset', False) )

        if child.get('all_fields', False) == False:
            opts['create'].update( default_setting(child, 'output_fields', []) )

        opts['create'].update( default_setting(child, 'positive_class', None) )

        if child.get('header', True) == True:
            opts['create'].update( default_setting(child, 'prediction_name', None, '') )

        opts['create'].update( default_setting(child, 'separator', ',') )
        opts['create'].update( inherit_setting(parentA, child, 'tags', []) )
        opts['create'].update( default_setting(child, 'threshold', None) )

        return ([ child, parentA, parentB ], opts)

    #
    # cluster come from datasets

    def reify_evaluation(self, resource):

        child = self.get_resource(resource)
        parentB = self.get_resource(child['dataset'])

        if child['ensemble'] != "":
            parentA = self.get_resource(child['ensemble'])
        elif child['model'] != "":
            parentA = self.get_resource(child['model'])
        else:
            raise Exception("Ensemble does not have a valid parent?")

        opts = { "create": {}, "update": {}, "args": {} }

        opts['create'].update( inherit_setting(parentA, child, 'category', 0) )
        opts['create'].update( default_setting(child, 'confidence_threshold', None) )
        opts['create'].update( default_setting(child, 'combiner', 0, None) )
        opts['create'].update( inherit_setting(parentA, child, 'description', '') )

        default_map = dict([ (el, el) for el in parentB['fields'] ])
        opts['create'].update( default_setting(child, 'fields_map', default_map) )

        opts['create'].update( default_setting(child, 'missing_strategy', 0) )

        if not child.get('name', '') in [ '', 'Evaluation of %s with %s' % ( parentA.get('name', ''), parentB.get('name', '')) ]:
            opts['create'].update({ "name": child['name'] })

        opts['create'].update( default_setting(child, 'ordering', 0) )
        opts['create'].update( default_setting(child, 'out_of_bag', False) )
        opts['create'].update( default_setting(child, 'negative_class', None) )
        opts['create'].update( default_setting(child, 'positive_class', None) )

        opts['update'].update( default_setting(child, 'private', True) )

        if not child.get('range', []) in [ [], [1, parentB.get('rows', None)] ]:
            opts['create'].update({ "range": child['range'] })

        opts['create'].update( default_setting(child, 'replacement', False) )
        opts['create'].update( default_setting(child, 'sample_rate', 1.0) )
        opts['create'].update( default_setting(child, 'seed', None) )
        opts['create'].update( inherit_setting(parentA, child, 'tags', []) )
        opts['create'].update( default_setting(child, 'threshold', None) )

        return ([ child, parentA, parentB ], opts)

    #
    # cluster come from datasets

    def reify_anomaly(self, resource):

        child = self.get_resource(resource)
        parent = self.get_resource(child['dataset'])

        opts = { "create": {}, "update": {}, "args": {} }

        opts['create'].update( default_setting(child, 'anomaly_seed', None) )
        opts['create'].update( inherit_setting(parent, child, 'category', 0) )
        opts['create'].update( default_setting(child, 'constraints', False) )
        opts['create'].update( inherit_setting(parent, child, 'description', '') )
        opts['create'].update( default_setting(child, 'excluded_fields', []) )

        for field in child['model']['fields']:
            if not field in parent['fields']: continue

            field_opts = {}

            if not child['model']['fields'][field].get("name", "") in [ "", parent['fields'][field].get("name", "") ]:
                opts['create'].update({ "fields": { field: { "name": child['model']['fields'][field]["name"] } } })


        opts['create'].update( default_setting(child, 'id_fields', [] ) )

        if not child.get('input_fields', []) in [ [], [ el for el in sorted(parent['fields'].keys()) if parent['fields'][el]['preferred'] == True ] ]:
            opts['create'].update( { "input_fields": child['input_fields'] } )

        opts['create'].update( default_setting(child, 'forest_size', 128) )

        if not child.get('name', '') in [ '', '%s anomaly detector' % parent.get('name', '') ]:
            opts['create'].update({ "name": child['name'] })

        opts['create'].update( default_setting(child, 'out_of_bag', False) )

        if not child.get('range', []) in [ [], [1, parent.get('rows', None)] ]:
            opts['create'].update({ "range": child['range'] })

        opts['create'].update( default_setting(child, 'replacement', False) )
        opts['create'].update( default_setting(child, 'sample_rate', 1.0) )
        opts['create'].update( default_setting(child, 'seed', None) )
        opts['create'].update( inherit_setting(parent, child, 'tags', []) )
        opts['create'].update( default_setting(child, 'top_n', 10) )

        return ([ child, parent ], opts)

    #
    # cluster come from datasets

    def reify_cluster(self, resource):

        child = self.get_resource(resource)
        parent = self.get_resource(child['dataset'])

        opts = { "create": {}, "update": {}, "args": {} }

        opts['create'].update( default_setting(child, 'balance_fields', True) )
        opts['create'].update( inherit_setting(parent, child, 'category', 0) )
        opts['create'].update( default_setting(child, 'cluster_seed', None) )
        opts['create'].update( inherit_setting(parent, child, 'description', '') )
        opts['create'].update( default_setting(child, 'default_numeric_value', None) )
        opts['create'].update( default_setting(child, 'excluded_fields', []) )

        for field in child['clusters']['fields']:
            if not field in parent['fields']: continue

            field_opts = {}

            if not child['clusters']['fields'][field].get("name", "") in [ "", parent['fields'][field].get("name", "") ]:
                opts['create'].update({ "fields": { field: { "name": child['clusters']['fields'][field]["name"] } } })

        opts['create'].update( default_setting(child, 'field_scales', {} ) )

        if not child.get('input_fields', []) in [ [], [ el for el in sorted(parent['fields'].keys()) if parent['fields'][el]['preferred'] == True ] ]:
            opts['create'].update( { "input_fields": child['input_fields'] } )

        if 'k' in child:
            opts['create'].update( { "k": child['k'] } )

        if not child.get('name', '') in [ '', '%s cluster' % parent.get('name', '') ]:
            opts['create'].update({ "name": child['name'] })

        opts['create'].update( default_setting(child, 'model_clusters', False) )
        opts['create'].update( default_setting(child, 'out_of_bag', False) )

        if not child.get('range', []) in [ [], [1, parent.get('rows', None)] ]:
            opts['create'].update({ "range": child['range'] })

        opts['create'].update( default_setting(child, 'replacement', False) )
        opts['create'].update( default_setting(child, 'sample_rate', 1.0) )
        opts['create'].update( default_setting(child, 'seed', None) )
        opts['create'].update( default_setting(child, 'summary_fields', []) )
        opts['create'].update( inherit_setting(parent, child, 'tags', []) )
        opts['create'].update( default_setting(child, 'weight_field', "") )

        return ([ child, parent ], opts)

    def reify_ensemble(self, resource):

        child = self.get_resource(resource)
        parent = self.get_resource(child['dataset'])

        [ family, opts ] = reify_model(child['models'][0])

        opts['create'].update( default_setting(child, 'number_of_models', 10) )
        opts['create'].update( default_setting(child, 'tlp', 1) )

        return ([ child, parent ], opts)

    #
    # Models come from datasets OR from clusters

    def reify_model(self, resource):

        resource_type = get_resource_type(resource)
        child = self.get_resource(resource)
        grandparent = {}
        parent = {}
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


        # inherited create options
        model_defaults = COMMON_DEFAULTS.get("create", {})
        model_defaults.update({'tags': [[]]})
        for attribute, default_value in model_defaults.items():
            opts["create"].update(
                inherit_setting(
                    grandparent, child, attribute, default_value[0]))
        # create options
        dataset_defaults = DEFAULTS[resource_type].get("create", {})
        for attribute, default_value in dataset_defaults.items():
            opts["create"].update(
                default_setting(child, attribute, *default_value))


        if child.get('randomize') == True:
            default_random_candidates = int(
                math.floor(math.sqrt(len(child['input_fields']))))
            opts['create'].update(
                default_setting(
                    child, 'random_candidates', [default_random_candidates] ))

        if (not child.get('range', []) in
                [[], [1, grandparent.get('rows', None)]]):
            opts['create'].update({ "range": child['range'] })

        # changes in fields structure
        fields_attributes = get_fields_changes(child, referrer=grandparent)
        if fields_attributes:
            opts['create'].update({"fields": fields_attributes})

        # input fields
        input_fields = get_input_fields(child, referrer=grandparent)
        if input_fields:
            opts['create'].update({'input_fields': input_fields})

        # name, exclude automatic naming alternatives
        autonames = [u'']
        autonames.append(
            u"'%s model" % grandparent.get('name', ''))
        autonames.append(
            u"Cluster %s - %s" % (int(child.get('centroid', "0"), base=16),
                                  parent['name']))
        if not child.get('name', '') in autonames:
            opts['create'].update({"name": child.get('name', '')})

        return ([ child, parent ], opts)

    def reify_dataset(self, resource):
        resource_type = get_resource_type(resource)
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


        # inherited create options
        dataset_defaults = COMMON_DEFAULTS.get("create", {})
        for attribute, default_value in dataset_defaults.items():
            opts["create"].update(
                inherit_setting(
                    grandparent, child, attribute, default_value[0]))
        # create options
        dataset_defaults = DEFAULTS[resource_type].get("create", {})
        for attribute, default_value in dataset_defaults.items():
            opts["create"].update(
                default_setting(child, attribute, *default_value))

        # update options
        dataset_defaults = DEFAULTS[resource_type].get("update", {})
        dataset_defaults.update(COMMON_DEFAULTS.get("update", {}))

        for attribute, default_value in dataset_defaults.items():
            opts["update"].update(
                default_setting(child, attribute, *default_value))

        # changes in fields structure
        fields_attributes = get_fields_changes(child, referrer=grandparent)
        if fields_attributes:
            opts['create'].update({"fields": fields_attributes})

        # input fields
        input_fields = get_input_fields(child, referrer=grandparent)
        if input_fields:
            opts['create'].update({'input_fields': input_fields})

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
