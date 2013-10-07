# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2013 BigML
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
"""Multi-label labels management functions

"""
MULTI_LABEL_LABEL = "multi-label label: "


def get_label_field(objective_name, label):
    """Returns a field name based on the original multi-label objective field
       name and the label

    """
    return "%s - %s" % (objective_name, label)


def get_labels_from_fields(fields):
    """Returns the name of the labels for a multi-label field structure.

       'fields' is a field dict and the label fields can be selected
       checking the 'label' attribute that will contain the literal:
       multi-label label: [label]
    """
    labels = []
    for field_id in fields:
        label_attribute = fields[field_id].get('label', None)
        if (label_attribute is not None and
                label_attribute.startswith(MULTI_LABEL_LABEL)):
            label = label_attribute[len(MULTI_LABEL_LABEL):]
            if not label in labels:
                labels.append(label)
    return labels


def retrieve_labels(fields, labels):
    """Returns the name of lables for a multi-label field structure either
       from the labels given by the user or from a field dict

    """
    # Labels info will be known only if the training set was provided
    # as starting point. Otherwise, the user can provide the labels
    # or the labels will be retrieved from the same fields structure.
    # Fields used as labels must have its "label" attribute set to
    # "multi-label label: [label]
    fields_labels = []
    if isinstance(fields, list):
        fields_list = fields
        for fields in fields_list:
            fields_labels.extend(get_labels_from_fields(fields))
            fields_labels = list(set(fields_labels))
    else:
        fields_labels = get_labels_from_fields(fields)
    if labels is not None:
        missing_labels = []
        for index in range(len(labels) - 1, -1, -1):
            label = labels[index]
            if not label in fields_labels:
                missing_labels.append(label)
                del labels[index]
        if missing_labels:
            print ("WARNING: Some of the given labels can't be"
                   " found in the models: %s" %
                   ", ".join(missing_labels))
    else:
        labels = fields_labels
    return fields_labels, sorted(labels)


def label_model_args(name, label, all_labels, model_fields, objective_field):
    """Adapts model arguments to choose only one label field as objective

    """
    label_field = get_label_field(objective_field, label)
    # TODO: modify fields if user set it absolutely
    single_label_fields = model_fields[:]
    single_label_fields.extend(
        map(lambda x: ("-%s" % get_label_field(objective_field, x)
                       if x != label_field
                       else
                       "+%s" % get_label_field(objective_field,
                                               x)),
            all_labels))
    single_label_fields.append("-%s" % objective_field)
    new_name = "%s for %s" % (name, label_field)

    return new_name, label_field, single_label_fields
