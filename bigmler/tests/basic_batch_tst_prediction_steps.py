# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2014-2024 BigML
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

import os

from bigml.api import check_resource

from bigmler.tests.common_steps import shell_execute
from bigmler.tests.world import world, res_filename, ok_


def i_check_create_batch_prediction(step):
    """Step: I check that the batch prediction has been created"""
    batch_prediction_file = os.path.join(world.directory, "batch_prediction")
    message = None
    try:
        with open(batch_prediction_file) as handler:
            batch_prediction = check_resource(handler.readline().strip(),
                                              world.api.get_batch_prediction)
        world.batch_predictions.append(batch_prediction['resource'])
        world.batch_prediction = batch_prediction
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_create_batch_projection(step):
    """Step: I check that the batch projection has been created"""
    batch_projection_file = os.path.join(world.directory, "batch_projection")
    message = None
    try:
        with open(batch_projection_file) as handler:
            batch_projection = check_resource(handler.readline().strip(),
                                              world.api.get_batch_projection)
        world.batch_projections.append(batch_projection['resource'])
        world.batch_projection = batch_projection
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_create_test_source(step):
    """Step: I check that the source has been created from the test file"""
    test_source_file = os.path.join(world.directory, "source_test")
    message = None
    try:
        with open(test_source_file) as handler:
            test_source = check_resource(handler.readline().strip(),
                                         world.api.get_source)
        world.sources.append(test_source['resource'])
        world.test_source = test_source
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_create_test_dataset(step):
    """Step: I check that the dataset has been created from the test file"""
    test_dataset_file = os.path.join(world.directory, "dataset_test")
    message = None
    try:
        with open(test_dataset_file) as handler:
            test_dataset = check_resource(handler.readline().strip(),
                                          world.api.get_dataset)
        world.datasets.append(test_dataset['resource'])
        world.test_lines = test_dataset['object']['rows'] + world.test_header
        world.test_dataset = test_dataset
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_create_batch_centroid(step):
    """Step: I check that the batch centroid prediction has been created"""
    batch_prediction_file = os.path.join(world.directory, "batch_centroid")
    message = None
    try:
        with open(batch_prediction_file) as handler:
            batch_centroid = check_resource(handler.readline().strip(),
                                            world.api.get_batch_centroid)
        world.batch_centroids.append(batch_centroid['resource'])
        world.batch_centroid = batch_centroid
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_create_batch_anomaly_scores(step):
    """Step: I check that the batch anomaly scores prediction has been
    created
    """
    batch_prediction_file = os.path.join(world.directory,
        "batch_anomaly_score")
    message = None
    try:
        with open(batch_prediction_file) as handler:
            batch_anomaly_score = check_resource(
                handler.readline().strip(), world.api.get_batch_anomaly_score)
        world.batch_anomaly_scores.append(batch_anomaly_score['resource'])
        world.batch_anomaly_score = batch_anomaly_score
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_create_batch_predictions_dataset(step):
    """Step: I check that the batch predictions dataset exists"""
    dataset_file = os.path.join(world.directory, "batch_prediction_dataset")
    message = None
    try:
        with open(dataset_file) as handler:
            dataset = check_resource(handler.readline().strip(),
                                     api=world.api)
            world.datasets.append(dataset['resource'])
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_create_batch_centroids_dataset(step):
    """Step: I check that the batch centroids dataset exists"""
    dataset_file = os.path.join(world.directory, "batch_centroid_dataset")
    message = None
    try:
        with open(dataset_file) as handler:
            dataset = check_resource(handler.readline().strip(),
                                     api=world.api)
        world.datasets.append(dataset['resource'])
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_create_resources_from_model_with_op_remote(step, operating_point=None,
                                                 test=None, output=None):
    """Step: I create BigML resources using model with operating point
    <operating_point> to test <test> and log predictions in <output>
    """
    ok_(operating_point is not None and
        test is not None and output is not None)
    test = res_filename(test)
    operating_point = res_filename(operating_point)
    command = ("bigmler --model " + world.model['resource'] + " --test " +
               test + " --operating-point " + operating_point +
               " --store --remote --output " + output +
               " --max-batch-models 1")
    shell_execute(command, output, test=test, options="--no-header")


def i_create_resources_from_model_remote_no_batch(step,
                                                  test=None, output=None):
    """Step: I create BigML remote predictions one by one using model
    to test <test> and log predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --model " + world.model['resource'] + " --test " +
               test + " --no-batch --store --remote --output " + output +
               " --max-batch-models 1")
    shell_execute(command, output, test=test, options="--no-header")
