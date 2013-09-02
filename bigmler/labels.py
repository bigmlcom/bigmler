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
from __future__ import absolute_import

from bigmler.utils import get_label_field


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

