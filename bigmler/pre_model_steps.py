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

""" Sources and Datasets common steps in dispatchers

"""
from __future__ import absolute_import

import os

import bigmler.processing.sources as ps
import bigmler.processing.datasets as pd
import bigmler.utils as u

def get_source_info(api, args, resume,
                    csv_properties, session_file, path, log):
    """Creating or retrieving the source and related information

    """
    source = None
    fields = None
    if args.source_file:
        # source is retrieved from the contents of the given local JSON file
        source, csv_properties, fields = u.read_local_resource(
            args.source_file,
            csv_properties=csv_properties)
    else:
        # source is retrieved from the remote object
        source, resume, csv_properties, fields = ps.source_processing(
            api, args, resume,
            csv_properties=csv_properties,
            session_file=session_file, path=path, log=log)

    if fields and args.export_fields:
        fields.summary_csv(os.path.join(path, args.export_fields))

    return source, resume, csv_properties, fields


def get_dataset_info(api, args, resume, source,
                     csv_properties, fields, session_file, path, log):
    """Creating or retrieving the dataset, test_dataset and related information

    """
    dataset = None
    datasets = None
    test_dataset = None
    if args.dataset_file:
        # dataset is retrieved from the contents of the given local JSON file
        model_dataset, csv_properties, fields = u.read_local_resource(
            args.dataset_file,
            csv_properties=csv_properties)
        if not args.datasets:
            datasets = [model_dataset]
            dataset = model_dataset
        else:
            datasets = u.read_datasets(args.datasets)
    if not datasets:
        # dataset is retrieved from the remote object
        datasets, resume, csv_properties, fields = pd.dataset_processing(
            source, api, args, resume,
            fields=fields,
            csv_properties=csv_properties,
            session_file=session_file, path=path, log=log)
    if datasets:
        dataset = datasets[0]
        if args.to_csv is not None:
            resume = pd.export_dataset(dataset, api, args, resume,
                                       session_file=session_file, path=path)

    # If test_split is used, split the dataset in a training and a test dataset
    # according to the given split
    if args.test_split > 0:
        dataset, test_dataset, resume = pd.split_processing(
            dataset, api, args, resume,
            session_file=session_file, path=path, log=log)
        datasets[0] = dataset

    # If multi-dataset flag is on, generate a new dataset from the given
    # list of datasets
    if args.multi_dataset:
        dataset, resume = pd.create_new_dataset(
            datasets, api, args, resume, fields=fields,
            session_file=session_file, path=path, log=log)
        datasets = [dataset]

    # Check if the dataset has a generators file associated with it, and
    # generate a new dataset with the specified field structure
    if args.new_fields:
        dataset, resume = pd.create_new_dataset(
            dataset, api, args, resume, fields=fields,
            session_file=session_file, path=path, log=log)
        datasets[0] = dataset

    if fields and args.export_fields:
        fields.summary_csv(os.path.join(path, args.export_fields))

    return dataset, datasets, test_dataset, resume, csv_properties, fields
