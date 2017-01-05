# -*- coding: utf-8 -*-
#
# Copyright 2014-2017 BigML
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


"""Options for BigMLer multi-label processing

"""

def get_multi_label_options(defaults=None):
    """Multi-label-related options

    """

    if defaults is None:
        defaults = {}
    options = {
        # Multi-label labels. If set, only the given labels are expanded
        '--labels': {
            'action': 'store',
            'dest': 'labels',
            'default': defaults.get('labels', None),
            'help': ("Comma-separated list of the labels"
                     " to be expanded from a multi-label field.")},

        # Multi-label label separator. Separator used when splitting labels in
        # the objective field.
        '--label-separator': {
            'action': 'store',
            'dest': 'label_separator',
            'default': defaults.get('label_separator', None),
            'help': ("Separator used when splitting labels in the"
                     " objective field.")},

        # Multi-label fields. Comma-separated list of fields that should be
        # treated as being multi-label fields.
        # Either its name or column number.
        '--multi-label-fields': {
            'action': 'store',
            'dest': 'multi_label_fields',
            'default': defaults.get('multi_label_fields', None),
            'help': ("Comma-separated list of the fields"
                     " to be expanded as being multi-label. Name"
                     " or column number.")},

        # Label-aggregates. Comma-separated list of aggregation functions
        # for the multi-label fields.
        '--label-aggregates': {
            'action': 'store',
            'dest': 'label_aggregates',
            'default': defaults.get('label_aggregates', None),
            'help': ("Comma-separated list of aggregation functions "
                     "for the multi-label field labels."
                     " Allowed aggregates: count, first and last")}}

    return options
