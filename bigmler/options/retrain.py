# -*- coding: utf-8 -*-
#
# Copyright 2017-2020 BigML
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


"""Options for BigMLer retrain option

"""

def get_retrain_options(defaults=None):
    """Retrain-related options

    """

    if defaults is None:
        defaults = {}
    options = {

        # Resource ID
        '--id': {
            'dest': 'resource_id',
            'default': defaults.get('resource_id', None),
            'help': ("ID for the resource to be retrained.")},
        # path to the data file to be added
        '--add': {
            'dest': 'add',
            'default': defaults.get('add', None),
            'help': ("Path to the data file to be added.")},
        # maximum number of datasets to be used when retraining
        '--window-size': {
            'type': int,
            'dest': 'window_size',
            'default': defaults.get('window_size', -1),
            'help': ("Maximum number of datasets to be used in retraining."
                     " When not set, the new dataset will be added to the"
                     " last one used.")}
    }

    return options
