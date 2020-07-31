# -*- coding: utf-8 -*-
#
# Copyright 2014-2020 BigML
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
import time
import csv
import json
from bigmler.tests.world import world, res_filename
from subprocess import check_call, CalledProcessError
from bigml.api import check_resource
from nose.tools import ok_
from bigmler.tests.common_steps import check_debug
from bigmler.checkpoint import file_number_of_lines


def shell_execute(command, output, test=None, options=None,
                  test_rows=None, project=True):
    """Excute bigmler command in shell

    """
    command = check_debug(command, project=project)
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    try:
        retcode = check_call(command, shell=True)
        ok_(retcode >= 0)
        if test is not None:
            world.test_lines = file_number_of_lines(test)
            if options is None or \
                    options.find('--prediction-header') == -1:
                # test file has headers in it, so first line must be ignored
                world.test_lines -= 1
        elif test_rows is not None:
            world.test_lines = test_rows
            if options is not None and \
                    options.find('--prediction-header') > -1:
                world.test_lines += 1
        elif options is not None and \
                options.find('--prediction-header') > -1:
            world.test_lines += 1
        world.output = output
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)

#@step(r'I check that the batch prediction has been created')
def i_check_create_batch_prediction(step):
    batch_prediction_file = "%s%sbatch_prediction" % (world.directory, os.sep)
    try:
        batch_prediction_file = open(batch_prediction_file, "r")
        batch_prediction = check_resource(batch_prediction_file.readline().strip(),
                                          world.api.get_batch_prediction)
        world.batch_predictions.append(batch_prediction['resource'])
        world.batch_prediction = batch_prediction
        batch_prediction_file.close()
        assert True
    except Exception as exc:
        assert False, str(exc)


#@step(r'I check that the batch projection has been created')
def i_check_create_batch_projection(step):
    batch_projection_file = "%s%sbatch_projection" % (world.directory, os.sep)
    try:
        batch_projection_file = open(batch_projection_file, "r")
        batch_projection = check_resource(batch_projection_file.readline().strip(),
                                          world.api.get_batch_projection)
        world.batch_projections.append(batch_projection['resource'])
        world.batch_projection = batch_projection
        batch_projection_file.close()
        assert True
    except Exception as exc:
        assert False, str(exc)


#@step(r'I check that the source has been created from the test file')
def i_check_create_test_source(step):
    test_source_file = "%s%ssource_test" % (world.directory, os.sep)
    try:
        test_source_file = open(test_source_file, "r")
        test_source = check_resource(test_source_file.readline().strip(),
                                     world.api.get_source)
        world.sources.append(test_source['resource'])
        world.test_source = test_source
        test_source_file.close()
        assert True
    except Exception as exc:
        assert False, str(exc)


#@step(r'I check that the dataset has been created from the test file')
def i_check_create_test_dataset(step):
    test_dataset_file = "%s%sdataset_test" % (world.directory, os.sep)
    try:
        test_dataset_file = open(test_dataset_file, "r")
        test_dataset = check_resource(test_dataset_file.readline().strip(),
                                      world.api.get_dataset)
        world.datasets.append(test_dataset['resource'])
        world.test_lines = test_dataset['object']['rows']
        world.test_no_header = True
        world.test_dataset = test_dataset
        test_dataset_file.close()
        assert True
    except Exception as exc:
        assert False, str(exc)


#@step(r'I check that the batch centroid prediction has been created')
def i_check_create_batch_centroid(step):
    batch_prediction_file = "%s%sbatch_centroid" % (world.directory, os.sep)
    try:
        batch_prediction_file = open(batch_prediction_file, "r")
        batch_centroid = check_resource(batch_prediction_file.readline().strip(),
                                          world.api.get_batch_centroid)
        world.batch_centroids.append(batch_centroid['resource'])
        world.batch_centroid = batch_centroid
        batch_prediction_file.close()
        assert True
    except Exception as exc:
        assert False, str(exc)


#@step(r'I check that the batch anomaly scores prediction has been created')
def i_check_create_batch_anomaly_scores(step):
    batch_prediction_file = "%s%sbatch_anomaly_score" % (world.directory, os.sep)
    try:
        batch_prediction_file = open(batch_prediction_file, "r")
        batch_anomaly_score = check_resource(batch_prediction_file.readline().strip(),
                                          world.api.get_batch_anomaly_score)
        world.batch_anomaly_scores.append(batch_anomaly_score['resource'])
        world.batch_anomaly_score = batch_anomaly_score
        batch_prediction_file.close()
        assert True
    except Exception as exc:
        assert False, str(exc)


#@step(r'I check that the batch predictions dataset exists')
def i_check_create_batch_predictions_dataset(step):
    dataset_file = "%s%sbatch_prediction_dataset" % (world.directory, os.sep)
    try:
        dataset_file = open(dataset_file, "r")
        dataset = check_resource(dataset_file.readline().strip(),
                                 api=world.api)
        world.datasets.append(dataset['resource'])
        dataset_file.close()
        assert True
    except Exception as exc:
        assert False, str(exc)


#@step(r'I check that the batch centroids dataset exists')
def i_check_create_batch_centroids_dataset(step):
    dataset_file = "%s%sbatch_centroid_dataset" % (world.directory, os.sep)
    try:
        dataset_file = open(dataset_file, "r")
        dataset = check_resource(dataset_file.readline().strip(),
                                 api=world.api)
        world.datasets.append(dataset['resource'])
        dataset_file.close()
        assert True
    except Exception as exc:
        assert False, str(exc)

#@step(r'I create BigML resources using model with operating point "(.*)"
# to test "(.*)" and
# log predictions in "(.*)"')
def i_create_resources_from_model_with_op_remote(step, operating_point=None,
                                                 test=None, output=None):
    ok_(operating_point is not None and
        test is not None and output is not None)
    test = res_filename(test)
    operating_point = res_filename(operating_point)
    command = ("bigmler --model " + world.model['resource'] + " --test " +
               test + " --operating-point " + operating_point +
               " --store --remote --output " + output +
               " --max-batch-models 1")
    shell_execute(command, output, test=test)

#@step(r'I create BigML remote predictions one by one using model "
# to test "(.*)" and
# log predictions in "(.*)"')
def i_create_resources_from_model_remote_no_batch(step,
                                                  test=None, output=None):
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --model " + world.model['resource'] + " --test " +
               test + " --no-batch --store --remote --output " + output +
               " --max-batch-models 1")
    shell_execute(command, output, test=test)
