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
import csv

from bigml.api import check_resource

from bigmler.utils import storage_file_name
from bigmler.tests.common_steps import shell_execute
from bigmler.tests.world import world, res_filename, eq_, ok_, ok_error


def i_create_all_cluster_resources(step, data=None, test=None, output=None):
    """Step: I create BigML resources uploading train <data> file to create
    centroids for <test> and log predictions in <output>
    """
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler cluster --train " + res_filename(data) +
               " --test " + test +
               " --k 8" +
               " --store --output " + output)
    shell_execute(command, output, test=test)


def i_check_create_cluster(step):
    """Step: I check that the cluster has been created"""
    cluster_file = os.path.join(world.directory, "clusters")
    message = None
    try:
        with open(cluster_file) as handler:
            cluster = check_resource(handler.readline().strip(),
                                     world.api.get_cluster)
            world.clusters.append(cluster['resource'])
            world.cluster = cluster
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_create_centroids(step):
    """Step: I check that the centroids are ready"""
    predictions_file = world.output
    with open(predictions_file, "r") as handler:
        predictions_lines = 0
        for _ in handler:
            predictions_lines += 1
    eq_(predictions_lines, world.test_lines,
        msg="predictions lines: %s, test lines: %s" % (predictions_lines,
                                                       world.test_lines))


def i_check_centroids(step, check_file):
    """Step: the local centroids file is like <check_file>"""
    check_file = res_filename(check_file)
    predictions_file = world.output
    message = None
    try:
        with open(predictions_file) as p_handler:
            predictions_file = csv.reader(p_handler, lineterminator="\n")
            with open(check_file) as c_handler:
                check_file = csv.reader(c_handler, lineterminator="\n")
        for row in predictions_file:
            check_row = next(check_file)
            message = ok_error(len(check_row) == len(row),
                               msg="Different row lengths.")
            for index, row_value in enumerate(row):
                message = ok_error(
                    row_value == check_row[index],
                    msg="Different row values: Found %s, %s expected" %
                    (row_value, check_row[index]))
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_create_cluster_resources_from_dataset(step, test=None, output=None):
    """Step: I create BigML resources using dataset to find centroids for
    <test> and log predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler cluster --dataset " +
               world.dataset['resource'] + " --test " + test +  " --k 8" +
               " --store --output " + output)
    shell_execute(command, output, test=test)


def i_create_cluster_resources_from_source(step, test=None, output=None):
    """Step: I create BigML resources using source to find centroids for
    <test> and log predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler cluster --source " +
               world.source['resource'] + " --test " + test + " --k 8" +
               " --store --output " + output)
    shell_execute(command, output, test=test)


def i_create_cluster_resources_from_local_cluster(
    step, directory=None, test=None, output=None):
    """Step: I create BigML resources using local cluster in <directory> to
    find centroids for <test> and log predictions in <output>
    """
    ok_(test is not None and output is not None and directory is not None)
    test = res_filename(test)
    with open(os.path.join(directory, "clusters")) as handler:
        cluster_id = handler.readline().strip()
    command = ("bigmler cluster --cluster-file " +
               storage_file_name(directory, cluster_id) +
               " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


def i_create_cluster_resources_from_cluster(step, test=None, output=None):
    """Step: I create BigML resources using cluster to find centroids for
    <test> and log predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler cluster --cluster " +
               world.cluster['resource'] + " --test " + test + " --k 8" +
               " --store --output " + output)
    shell_execute(command, output, test=test)


def i_create_cluster_resources_from_clusters_file(
    step, clusters_file=None, test=None, output=None):
    """Step: I create BigML resources using clusters in file <cluster_file> to
    find centroids for <test> and log predictions in <output>
    """
    ok_(test is not None and output is not None and clusters_file is not None)
    test = res_filename(test)
    command = ("bigmler cluster --clusters " +
               clusters_file + " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


def i_create_all_cluster_resources_to_dataset(
    step, data=None, test=None, output_dir=None):
    """Step: I create BigML resources uploading train <data> file to find
    centroids for <test> remotely to dataset with no CSV and log resources in
    <output_dir>
    """
    ok_(data is not None and test is not None and output_dir is not None)
    test = res_filename(test)
    command = ("bigmler cluster --remote --train " + res_filename(data) +
               " --test " + test + " --k 8" +
               " --to-dataset --no-csv " +
               " --store --output-dir " + output_dir)
    shell_execute(command, "%s/x.csv" % output_dir, test=test)


def i_create_all_cluster_resources_with_mapping(
    step, data=None, test=None, fields_map=None, output=None):
    """Step: I create BigML resources uploading train <data> file to find
    centroids for <test> remotely with mapping file <fields_map> and log
    predictions in <output>
    """
    ok_(data is not None and test is not None and output is not None and
        fields_map is not None)
    test = res_filename(test)
    command = ("bigmler cluster --remote --train " + res_filename(data) +
               " --test " + test + " --k 8" +
               " --fields-map " + res_filename(fields_map) +
               " --store --output " + output)
    shell_execute(command, output, test=test, options="--no-header")


def i_create_all_cluster_resources_with_prediction_fields(
    step, data=None, test=None, prediction_fields=None, output=None):
    """Step: I create BigML resources uploading train <data> file to find
    centroids for <test> remotely with predictions fields <prediction_fields>
    and log predictions in <output>
    """
    ok_(data is not None and test is not None and output is not None and
        prediction_fields is not None)
    test = res_filename(test)
    command = ("bigmler cluster --remote --train " + res_filename(data) +
               " --test " + test + " --k 8" +
               " --prediction-fields \"" + prediction_fields +
               "\" --prediction-info full --prediction-header --store " +
               "--output " + output)
    shell_execute(command, output, test=test)


def i_create_cluster_from_dataset_with_summary_fields(
    step, summary_fields=None, output_dir=None):
    """Step: I create BigML cluster using dataset and summary_fields
    <summary_fields> and log resources in <output_dir>
    """
    ok_(summary_fields is not None and output_dir is not None)
    command = ("bigmler cluster --dataset " +
               world.dataset['resource'] + " --summary-fields " +
               summary_fields + " --k 8" +
               " --store --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "tmp.csv"))


def i_create_datasets_from_cluster(step, centroids=None, output=None):
    """#@step(r'I generate datasets for <centroids> centroids and log
    predictions in <output>
    """
    ok_(centroids is not None and output is not None)
    command = ("bigmler cluster --cluster " + world.cluster['resource'] +
               " --cluster-datasets \"" + centroids +
               "\" --store --output " + output)
    shell_execute(command, output, test=None)


def i_check_cluster_datasets(step, datasets_number=None):
    """Step: I check that the <datasets_number> cluster datasets are ready"""
    message = None
    try:
        datasets_file = os.path.join(world.directory, "dataset_cluster")
        with open(datasets_file) as handler:
            dataset_ids = handler.readlines()
            world.datasets.extend(dataset_ids)
            eq_(int(datasets_number), len(dataset_ids),
                msg="generated datasets %s, expected %s" % (
                    len(dataset_ids), datasets_number))
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_cluster_models(step, models_number=None):
    """Step: I check that the <models_number> cluster models are ready"""
    message = None
    try:
        models_file = os.path.join(world.directory, "models_cluster")
        with open(models_file) as handler:
            model_ids = handler.readlines()
            world.models.extend(model_ids)
            eq_(int(models_number), len(model_ids),
                msg="generated models %s, expected %s" % (
                    len(model_ids), models_number))
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_create_models_from_cluster(step, centroids=None, output=None):
    """Step: I generate models for <centroids> centroids and log results in
    <output>
    """
    ok_(centroids is not None and output is not None)
    command = ("bigmler cluster --dataset " + world.dataset['resource'] +
               " --cluster-models \"" + centroids +
               "\" --k 4 --store --output " + output)
    shell_execute(command, output, test=None)


def i_check_cluster_has_summary_fields(step, summary_fields=None):
    """Step: I check that the cluster has summary fields <summary_fields>"""
    eq_(world.cluster['object']['summary_fields'],
        summary_fields.split(","))
