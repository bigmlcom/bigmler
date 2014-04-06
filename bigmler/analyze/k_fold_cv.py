# -*- coding: utf-8 -*-
#
# Copyright 2012-2014 BigML
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

"""k-fold cross-validation procedure (analysis subcommand)

   Functions used in k-fold cross-validation procedure.


"""
from __future__ import absolute_import


import os
import sys

import bigml

import bigmler.processing.args as a
from bigmler.dispatcher import main_dispatcher
from bigmler.processing.datasets import get_fields_structure
 
EXTENDED_DATASET = "kfold_dataset.json"
TEST_DATASET = "kfold_dataset-%s.json"

SELECTING_KFOLD = '["%s", %s, ["field", "%s"]]'
NEW_FIELD = '{"new_fields": [{"name": "%s", "field": "(rand-int %s)"}]}'

COMMAND_EXTENDED = ("main --dataset %s --new-field %s --no-model --output-dir "
                    "%s%sextended")
COMMAND_SELECTION = ("main --dataset %s --json-filter %s --no-model"
                     " --output-dir %s%s%s --objective %s")
COMMAND_CREATE_CV = ("main --datasets %s --output-dir %sk_fold_cv"
                     " --dataset-off --evaluate")
DEFAULT_KFOLD_FIELD = "__kfold__"


def create_kfold_cv(args, api):
    """Main procedure to create a k-fold cross-validation

    """
    #retrieve dataset
    #check kfold field name is unique
    #
    if args.output_dir is None:
        args.output_dir = a.NOW
    dataset_id = bigml.api.get_dataset_id(args.dataset)
    dataset = api.check_resource(dataset_id, api.get_dataset)
    csv_properties = {}
    if ('object' in dataset and 'objective_field' in dataset['object'] and
        'column_number' in dataset['object']['objective_field']):
        dataset_objective = dataset[
            'object']['objective_field']['column_number']
        csv_properties.update(objective_field=dataset_objective,
              objective_field_present=True)
    fields = get_fields_structure(dataset, csv_properties)
    fields.objective_field
    kfold_field_name = avoid_duplicates(DEFAULT_KFOLD_FIELD, fields)
    # creating auxiliar json files to generate test datasets
    extended_file, selecting_file_list = create_kfold_json(
        args.output_dir, kfold_field=kfold_field_name, k=args.k_fold_cv)
    # generate test datasets, models and evaluations
    if args.dataset:
        create_kfold_dataset(args.dataset, args.output_dir, args.k_fold_cv,
                             extended_file, selecting_file_list,
                             fields.objective_field)
     


def create_kfold_json(output_dir, kfold_field=DEFAULT_KFOLD_FIELD,
                      k=5):
    """Create the files to generate a new field with a random integer from
       0 to k-1, and a filter file for each of these indexes.

    """

    new_file = NEW_FIELD % (kfold_field, k)
    try:
        extended_file = "%s%s%s" % (output_dir, os.sep, EXTENDED_DATASET) 
        with open(extended_file, "w") as extended_dataset:
            extended_dataset.write(new_file)
        selecting_file_list = []
        selecting_out_file_list = []
        for index in range(0, k):
            selecting_file = TEST_DATASET % index
            selecting_file =  "%s%s%s" % (output_dir, os.sep, selecting_file)
            selecting_file_list.append(selecting_file)
            with open(selecting_file, "w") as test_dataset:
                test_dataset.write(SELECTING_KFOLD % ("!=", index,
                                                      kfold_field))
        return (extended_file, selecting_file_list)
    except IOError:
        sys.exit("Could not create the necessary files.")


def avoid_duplicates(field_name, fields, affix="_"):
    """Checks if a field name exists already in a fields structure.

    """
    if any([field['name'] == field_name
            for _, field in fields.fields.items()]):
        return avoid_duplicates(field_name, fields, affix=affix)
    return field_name


def create_kfold_dataset(dataset, output_dir, k, extended_file,
                         selecting_file_list, objective):
    """Calling the bigmler procedure to create the k-fold datasets

    """

    # creating the extended dataset
    extended_dataset_file = "%s%sextended%sdataset_gen" % (output_dir, os.sep,
                                                           os.sep)
    command = COMMAND_EXTENDED % (dataset, extended_file,
                                  output_dir, os.sep)
    main_dispatcher(args=command.split())
    # getting the extended dataset id
    with open(extended_dataset_file, "r") as extended_handler:
        extended_dataset_id = extended_handler.readline().strip()
    # creating the selecting datasets
    for index in range(0, len(selecting_file_list)):
        main_dispatcher(args=(COMMAND_SELECTION % (
            extended_dataset_id, selecting_file_list[index],
            output_dir, os.sep, "test", objective)).split())
    # creating the models from the datasets' files (multidatasets excluding
    # one test dataset at a time)
    datasets_directory = "%s%stest%s" % (output_dir, os.sep, os.sep)
    datasets_file = "%sdataset_gen" % datasets_directory
    print COMMAND_CREATE_CV % (datasets_file, datasets_directory)
    main_dispatcher(args=(COMMAND_CREATE_CV % (datasets_file,
                                               datasets_directory)).split())
