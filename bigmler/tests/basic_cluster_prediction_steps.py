# -*- coding: utf-8 -*-
#
# Copyright 2014-2016 BigML
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
from __future__ import absolute_import


import os
import time
import csv
import json

from nose.tools import assert_equal, assert_not_equal, ok_
from bigmler.tests.world import world, res_filename
from subprocess import check_call, CalledProcessError
from bigml.api import check_resource
from bigmler.utils import storage_file_name
from bigmler.checkpoint import file_number_of_lines
from bigmler.tests.common_steps import check_debug


def shell_execute(command, output, test=None, options=None,
                  data=None, test_split=None):
    """Excute bigmler command in shell

    """
    command = check_debug(command)
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    try:
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            if test is not None:
                world.test_lines = file_number_of_lines(test)
                world.test_lines -= 1
                # prediction file has headers in it,
                # so first line must be ignored
                world.prediction_header = options is not None and \
                    options.find('--prediction-header') > -1
            if test_split is not None:
                data_lines = file_number_of_lines(data) - 1
                world.test_lines = int(data_lines * float(test_split))
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create BigML resources uploading train "(.*?)" file to create centroids for "(.*?)" and log predictions in "([^"]*)"$')
def i_create_all_cluster_resources(step, data=None, test=None, output=None):
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler cluster --train " + res_filename(data) + " --test " + test +
               " --k 8" +
               " --store --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I check that the cluster has been created')
def i_check_create_cluster(step):
    cluster_file = "%s%sclusters" % (world.directory, os.sep)
    try:
        cluster_file = open(cluster_file, "r")
        cluster = check_resource(cluster_file.readline().strip(),
                                 world.api.get_cluster)
        world.clusters.append(cluster['resource'])
        world.cluster = cluster
        cluster_file.close()
        assert True
    except Exception, exc:
        assert False, str(exc)


#@step(r'I check that the centroids are ready')
def i_check_create_centroids(step):
    predictions_file = world.output
    predictions_file = open(predictions_file, "r")
    predictions_lines = 0
    for line in predictions_file:
        predictions_lines += 1
    predictions_file.close()
    if world.prediction_header:
        predictions_lines -= 1
    assert_equal(predictions_lines, world.test_lines,
                 msg="predictions lines: %s, test lines: %s" % \
                 (predictions_lines, world.test_lines))


#@step(r'the local centroids file is like "(.*)"')
def i_check_centroids(step, check_file):
    check_file = res_filename(check_file)
    predictions_file = world.output
    try:
        predictions_file = csv.reader(open(predictions_file, "U"), lineterminator="\n")
        check_file = csv.reader(open(check_file, "U"), lineterminator="\n")
        for row in predictions_file:
            check_row = check_file.next()
            if len(check_row) != len(row):
                assert False
            for index in range(len(row)):
                if check_row[index] != row[index]:
                    print row, check_row
                    assert False
        assert True
    except Exception, exc:
        assert False, str(exc)


#@step(r'I create BigML resources using dataset to find centroids for "(.*)" and log predictions in "(.*)"')
def i_create_cluster_resources_from_dataset(step, test=None, output=None):
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler cluster --dataset " +
               world.dataset['resource'] + " --test " + test +  " --k 8" +
               " --store --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources using source to find centroids for "(.*)" and log predictions in "(.*)"')
def i_create_cluster_resources_from_source(step, test=None, output=None):
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler cluster --source " +
               world.source['resource'] + " --test " + test + " --k 8" +
               " --store --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources using local cluster in "(.*)" to find centroids for "(.*)" and log predictions in "(.*)"')
def i_create_cluster_resources_from_local_cluster(step, directory=None, test=None, output=None):
    ok_(test is not None and output is not None and directory is not None)
    test = res_filename(test)
    with open(os.path.join(directory, "clusters")) as handler:
        cluster_id = handler.readline().strip()
    command = ("bigmler cluster --cluster-file " +
               storage_file_name(directory, cluster_id) +
               " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources using cluster to find centroids for "(.*)" and log predictions in "(.*)"')
def i_create_cluster_resources_from_cluster(step, test=None, output=None):
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler cluster --cluster " +
               world.cluster['resource'] + " --test " + test + " --k 8" +
               " --store --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources using clusters in file "(.*)" to find centroids for "(.*)" and log predictions in "(.*)"')
def i_create_cluster_resources_from_clusters_file(step, clusters_file=None, test=None, output=None):
    ok_(test is not None and output is not None and clusters_file is not None)
    test = res_filename(test)
    command = ("bigmler cluster --clusters " +
               clusters_file + " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources uploading train "(.*?)" file to find centroids for "(.*?)" remotely to dataset with no CSV and log resources in "([^"]*)"$')
def i_create_all_cluster_resources_to_dataset(step, data=None, test=None, output_dir=None):
    ok_(data is not None and test is not None and output_dir is not None)
    test = res_filename(test)
    command = ("bigmler cluster --remote --train " + res_filename(data) +
               " --test " + test + " --k 8" +
               " --to-dataset --no-csv " +
               " --store --output-dir " + output_dir)
    shell_execute(command, "%s/x.csv" % output_dir, test=test)


#@step(r'I create BigML resources uploading train "(.*?)" file to find centroids for "(.*?)" remotely with mapping file "(.*)" and log predictions in "([^"]*)"$')
def i_create_all_cluster_resources_with_mapping(step, data=None, test=None, fields_map=None, output=None):
    ok_(data is not None and test is not None and output is not None and fields_map is not None)
    test = res_filename(test)
    command = ("bigmler cluster --remote --train " + res_filename(data) +
               " --test " + test + " --k 8" +
               " --fields-map " + res_filename(fields_map) +
               " --store --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources uploading train "(.*?)" file to find centroids for "(.*?)" remotely with predictions fields "(.*)" and log predictions in "([^"]*)"$')
def i_create_all_cluster_resources_with_prediction_fields(step, data=None, test=None, prediction_fields=None, output=None):
    ok_(data is not None and test is not None and output is not None and prediction_fields is not None)
    test = res_filename(test)
    command = ("bigmler cluster --remote --train " + res_filename(data) +
               " --test " + test + " --k 8" +
               " --prediction-fields \"" + prediction_fields +
               "\" --prediction-info full --prediction-header --store " +
               "--output " + output)
    shell_execute(command, output, test=test, options='--prediction-header')



#@step(r'I create BigML cluster using dataset and summary_fields "(.*)" and log resources in "(.*)"')
def i_create_cluster_from_dataset_with_summary_fields(step, summary_fields=None, output_dir=None):
    ok_(summary_fields is not None and output_dir is not None)
    command = ("bigmler cluster --dataset " +
               world.dataset['resource'] + " --summary-fields " +
               summary_fields + " --k 8" +
               " --store --output-dir " + output_dir)
    shell_execute(command, "%s/x.csv" % output_dir)

#@step(r'I generate datasets for "(.*?)" centroids and log predictions in "(.*?)"$')
def i_create_datasets_from_cluster(step, centroids=None, output=None):
    ok_(centroids is not None and output is not None)
    command = ("bigmler cluster --cluster " + world.cluster['resource'] +
               " --cluster-datasets \"" + centroids +
               "\" --store --output " + output)
    shell_execute(command, output, test=None)


#@step(r'I check that the (\d+) cluster datasets are ready$')
def i_check_cluster_datasets(step, datasets_number=None):

    try:
        datasets_file = os.path.join(world.directory, "dataset_cluster")
        datasets_file = open(datasets_file, "r")
        dataset_ids = datasets_file.readlines()
        world.datasets.extend(dataset_ids)
        if int(datasets_number) == len(dataset_ids):
            assert True
        else:
            assert False, "generated datasets %s, expected %s" % (
                len(dataset_ids), datasets_number)
    except Exception, exc:
        assert False, str(exc)


#@step(r'I check that the (\d+) cluster models are ready$')
def i_check_cluster_models(step, models_number=None):

    try:
        models_file = os.path.join(world.directory, "models_cluster")
        models_file = open(models_file, "r")
        model_ids = models_file.readlines()
        world.models.extend(model_ids)
        if int(models_number) == len(model_ids):
            assert True
        else:
            assert False, "generated models %s, expected %s" % (
                len(model_ids), models_number)
    except Exception, exc:
        assert False, str(exc)


#@step(r'I generate models for "(.*?)" centroids and log results in "(.*?)"$')
def i_create_models_from_cluster(step, centroids=None, output=None):
    ok_(centroids is not None and output is not None)
    command = ("bigmler cluster --dataset " + world.dataset['resource'] +
               " --cluster-models \"" + centroids +
               "\" --k 4 --store --output " + output)
    shell_execute(command, output, test=None)


#@step(r'I check that the cluster has summary fields "(.*)"$')
def i_check_cluster_has_summary_fields(step, summary_fields=None):

    assert_equal(world.cluster['object']['summary_fields'],
                 summary_fields.split(","))
