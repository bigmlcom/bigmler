# -*- coding: utf-8 -*-
#
# Copyright 2014-2021 BigML
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


"""Options for BigMLer source processing

"""

def get_source_options(defaults=None):
    """source-related options

    """

    if defaults is None:
        defaults = {}

    options = {
        # Path to the training set.
        '--train': {
            "action": 'store',
            "dest": 'training_set',
            'nargs': '?',
            "default": defaults.get('train', None),
            "help": "Training set path."},
        # If a BigML source is provided, the script won't create a new one
        '--source': {
            "action": 'store',
            "dest": 'source',
            "default": defaults.get('source', None),
            "help": "BigML source Id."},

        # If a BigML json file containing a source structure is provided,
        # the script will use it.
        '--source-file': {
            'action': 'store',
            'dest': 'source_file',
            'default': defaults.get('source_file', None),
            'help': "BigML source JSON structure file."},

        # The path to a file containing names if you want to alter BigML's
        # default field names or the ones provided by the train file header.
        # Kept for backwards compatibility
        '--field-names': {
            'action': 'store',
            'dest': 'field_attributes',
            'default': defaults.get('field_names', None),
            'help': ("Path to a csv file describing field names. One"
                     " definition per line (e.g., 0,'Last Name').")},

        # The path to a file containing attributes if you want to alter BigML's
        # default field attributes or the ones provided by the train file
        # header.
        '--field-attributes': {
            'action': 'store',
            'dest': 'field_attributes',
            'default': defaults.get('field_attributes', None),
            'help': ("Path to a csv file describing field attributes."
                     " One definition per line"
                     " (e.g., 0,'Last Name').")},
        # The path to a file containing types if you want to alter BigML's
        # type auto-detect.
        '--types': {
            'action': 'store',
            'dest': 'types',
            'default': defaults.get('types', None),
            'help': ("Path to a file describing field types. One"
                     " definition per line (e.g., 0, 'numeric').")},
        # Set when the training set file doesn't include a header on the first
        # line.
        '--no-train-header': {
            'action': 'store_false',
            'dest': 'train_header',
            'default': defaults.get('train_header', True),
            'help': "The train set file hasn't a header."},

        # Set when the training set file does include a header on the first
        # line. (opposed to --no-train-header)
        '--train-header': {
            'action': 'store_true',
            'dest': 'train_header',
            'default': defaults.get('train_header', True),
            'help': "The train set file has a header."},

        # Locale settings.
        '--locale': {
            'action': 'store',
            'dest': 'user_locale',
            'default': defaults.get('locale', None),
            'help': "Chosen locale code string."},

        # The path to a file containing source attributes.
        '--source-attributes': {
            'action': 'store',
            'dest': 'source_attributes',
            'default': defaults.get('source_attributes', None),
            'help': ("Path to a json file describing source"
                     " attributes.")},

        # Training set field separator. Defaults to the locale csv
        # separator.
        '--training-separator': {
            'action': 'store',
            'dest': 'training_separator',
            'default': defaults.get('training_separator', None),
            'help': ("Training set field separator.")},

        # Name of the project to be created and/or used in resource creation
        '--project': {
            'action': 'store',
            'dest': 'project',
            'default': defaults.get('project', None),
            'help': ("Name of the project to be created and/or used in"
                     "resource creation.")},

        # Id of the project to be used in resource creation
        '--project-id': {
            'action': 'store',
            'dest': 'project_id',
            'default': defaults.get('project_id', None),
            'help': ("Id of the project to be used in "
                     "resource creation.")},

        # The path to a file containing the fields information available in
        # the resource
        '--export-fields': {
            'action': 'store',
            'dest': 'export_fields',
            'default': defaults.get('export_fields', None),
            'help': ("Path to a csv file describing the available field"
                     " information. The first row is used as header.")},

        # The path to a file containing field attributes that will be used
        # to modify the fields structure.
        '--import-fields': {
            'action': 'store',
            'dest': 'import_fields',
            'default': defaults.get('import_fields', None),
            'help': ("Path to a csv file describing field attributes."
                     " The first row is used as header and rows are"
                     " expected to comply the the --export-fields output.")},

        # Whether o not the source will be closed for editing
        '--closed': {
            'action': 'store_true',
            'dest': 'closed',
            'default': defaults.get('closed', None),
            'help': ("Whether or not the source will be closed for editing.")},

        # Whether o not the source will be closed for editing
        '--open': {
            'action': 'store_false',
            'dest': 'closed',
            'default': defaults.get('closed', None),
            'help': ("Whether or not the source will be open for editing.")},

        # A comma-separated list of source identifiers to remove from a
        # composite and, if they do not belong to any other composite, delete
        # as individual resources.
        '--delete-sources': {
            'action': 'store',
            'dest': 'delete_sources',
            'default': defaults.get('delete_sources', None),
            'help': ("A comma-separated list of source identifiers to remove"
                     " from a composite and, if they do not belong to any"
                     " other composite, delete as individual resources.")},

        # A comma-separated list of source identifiers to remove from a
        # composite and, if they do not belong to any other composite, delete
        # as individual resources.
        '--remove-sources': {
            'action': 'store',
            'dest': 'remove_sources',
            'default': defaults.get('remove_sources', None),
            'help': ("A comma-separated list of source identifiers to remove"
                     " from a composite.")},

        # Values to be replaced in some fields and rows.
        '--row-values-json': {
            'action': 'store',
            'dest': 'row_values_json',
            'default': defaults.get('row_values_json', None),
            'help': ("Path to a JSON file that contains an array of objects"
                     " specifying values for different rows and label fields "
                     " in a composite via the following properties: "
                     " `indices, components, value, field."
                     " E.g.: [{\"field\": \"field1\", \"indices\": [0, 3],"
                     " \"value\": 8}, {\"field\": \"field2\","
                     " \"value\": 4}]."
                     " In the second element, no indices or components are "
                     " specified, so the properties \"row_components\" and "
                     " \"row_indices\" will be used as default for those.")},

        # Default for the components property of row_values
        '--row-components': {
            'action': 'store',
            'dest': 'row_components',
            'default': defaults.get('row_components', None),
            'help': ("Comma-separated list of IDs corresponding to the "
                     "sources in a composite that will be updated by "
                     "default when using \"row_values\" with no \"components\""
                     " specification.")},

        # Default for the indices property of row_values
        '--row-indices': {
            'action': 'store',
            'dest': 'row_indices',
            'default': defaults.get('row_indices', None),
            'help': ("Comma-separated list of indices corresponding to the "
                     "sources in a composite that will be updated by "
                     "default when using \"row_values\" with no \"indices\""
                     " specification.")}}

    return options
