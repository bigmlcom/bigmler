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

import bigmler.processing.args as a
from bigmler.dispatcher import main_dispatcher
 
EXTENDED_DATASET = "kfold_dataset.json"
TRAIN_DATASET = "kfold_dataset_%s.json"
TEST_DATASET = "kfold_dataset-%s.json"

SELECTING_KFOLD = '["%s", %s, ["field", "%s"]]'
NEW_FIELD = '{"new_fields": [{"name": "%s", "field": "(rand-int %s)"}]}'

COMMAND_EXTENDED = ("main --dataset %s --new-field %s --no-model --output-dir "
                    "%s%sextended")
COMMAND_SELECTION = ("main --dataset %s --json-filter %s --no-model"
                     " --output-dir %s%s%s")
DEFAULT_KFOLD_FIELD = "__kfold__"

def create_kfold_cv(args):
    """Main procedure to create a k-fold cross-validation

    """
    #retrieve dataset
    #check kfold field name is unique
    #
    if args.output_dir is None:
        args.output_dir = a.NOW
    (extended_file, selecting_file_list,
     selecting_out_file_list) = create_kfold_json(args.output_dir)
    if args.dataset:
        create_kfold_dataset(args.dataset, args.output_dir, args.k_fold_cv,
                             extended_file, selecting_file_list,
                             selecting_out_file_list)

def create_kfold_json(output_dir, kfold_field=DEFAULT_KFOLD_FIELD, k=5):
    """Create the files to generate a new field with a random integer from
       0 to k-1, and a filter file for each of these indexes.

    """

    new_file = NEW_FIELD % (kfold_field, k - 1)
    try:
        extended_file = "%s%s%s" % (output_dir, os.sep, EXTENDED_DATASET) 
        with open(extended_file, "w") as extended_dataset:
            extended_dataset.write(new_file)
        selecting_file_list = []
        selecting_out_file_list = []
        for index in range(0, k - 1):
            selecting_file = TRAIN_DATASET % index
            selecting_file =  "%s%s%s" % (output_dir, os.sep, selecting_file)
            selecting_file_list.append(selecting_file)
            with open(selecting_file, "w") as train_dataset:
                train_dataset.write(SELECTING_KFOLD % ("=", index,
                                                       kfold_field))
            selecting_file = TEST_DATASET % index
            selecting_file =  "%s%s%s" % (output_dir, os.sep, selecting_file)
            selecting_out_file_list.append(selecting_file)
            with open(selecting_file, "w") as test_dataset:
                test_dataset.write(SELECTING_KFOLD % ("!=", index,
                                                      kfold_field))
        return (extended_file, selecting_file_list, selecting_out_file_list)
    except IOError:
        sys.exit("Could not create the necessary files.")


def create_kfold_dataset(dataset, output_dir, k, extended_file,
                         selecting_file_list, selecting_out_file_list):
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
        print 
        main_dispatcher(args=(COMMAND_SELECTION % (
            extended_dataset_id, selecting_file_list[index],
            output_dir, os.sep, "training")).split())
        main_dispatcher(args=(COMMAND_SELECTION % (
            extended_dataset_id, selecting_out_file_list[index],
            output_dir, os.sep, "test")).split())

"""TODO:
    - creating model and evaluation for each i in range(1,k)
    - creating average
"""


