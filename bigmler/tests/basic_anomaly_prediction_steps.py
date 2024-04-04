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
import json

from bigml.api import check_resource

from bigmler.utils import storage_file_name
from bigmler.tests.common_steps import shell_execute, check_rows_equal
from bigmler.tests.world import world, res_filename, ok_, eq_


def i_create_all_anomaly_resources_without_test_split(
    step, data=None, output_dir=None):
    """Step: I create BigML resources uploading train <data> file to find
    anomaly scores for the training set remotely saved to dataset with no
    CSV output and log resources in <output_dir>
    """
    ok_(data is not None and output_dir is not None)
    command = ("bigmler anomaly --remote --train " + res_filename(data) +
               " --store --score --no-csv --to-dataset --output-dir " +
               output_dir)
    shell_execute(command, "%s/x.csv" % output_dir, data=data, test_split=1)


def i_create_all_anomaly_resources_with_test_split_no_csv(
    step, data=None, test_split=None, output_dir=None):
    """Step: I create BigML resources uploading train <data> file to find
    anomaly scores with test split <test_split> remotely saved to dataset
    with no CSV output and log resources in <output_dir>
    """
    ok_(data is not None and output_dir is not None)
    command = ("bigmler anomaly --remote --train " + res_filename(data) +
               " --test-split " + test_split +
               " --store --no-csv --prediction-header  "
               "--to-dataset --output-dir " + output_dir)
    shell_execute(command, "%s/x.csv" % output_dir,
                  data=data, test_split=test_split)


def i_create_anomaly_with_id_fields(step, id_fields=None, output_dir=None):
    """Step: And I create anomaly detector with "<id_fields>" and log
    predictions in <output_dir>
    """
    ok_(output_dir is not None and id_fields is not None)
    command = ("bigmler anomaly --dataset " + world.dataset["resource"] +
               " --id-fields " + ",".join(json.loads(id_fields)) +
               " --store --output-dir " + output_dir)
    shell_execute(command, "%s/x.csv" % output_dir)


def i_create_anomaly_resources_with_options(
    step, data=None, options=None, output_dir=None):
    """Step: I create BigML anomaly detector from data <data> with options
    <options> and generate a new dataset of anomalies in <output_dir>
    """
    ok_(data is not None and output_dir is not None and options is not None)
    command = ("bigmler anomaly --train " + res_filename(data) + " " +
               options +
               " --anomalies-dataset in --store --output-dir " + output_dir)
    shell_execute(command, "%s/x.csv" % output_dir, data=data)


def i_create_all_anomaly_resources(step, data=None, test=None, output=None):
    """Step: I create BigML resources uploading train <data> file to create
    anomaly scores for <test> and log predictions in <output>
    """
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler anomaly --train " + res_filename(data) + " --test " +
               test + " --store --prediction-header --output " + output)
    shell_execute(command, output, test=test)


def i_create_anomaly_resources_from_source(step, test=None, output=None):
    """Step: I create BigML resources using source to find anomaly scores for
    <test> and log predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler anomaly --source " + world.source['resource'] +
               " --test " + test +
               " --store --prediction-header --output " + output)
    shell_execute(command, output, test=test)


def i_create_anomaly_resources_from_dataset(step, test=None, output=None):
    """Step: I create BigML resources using dataset to find anomaly scores
    for <test> and log predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler anomaly --dataset " + world.dataset['resource'] +
               " --test " + test +
               " --store --prediction-header --output " + output)
    shell_execute(command, output, test=test)


def i_create_anomaly_resources_from_local_anomaly_detector(
    step, directory=None, test=None, output=None):
    """Step: I create BigML resources using local anomaly detector in
    <directory> to find anomaly scores for <test> and log predictions in
    <output>
    """
    ok_(test is not None and output is not None and directory is not None)
    test = res_filename(test)
    with open(os.path.join(directory, "anomalies")) as handler:
        anomaly_id = handler.readline().strip()
    command = ("bigmler anomaly --anomaly-file " +
               storage_file_name(directory, anomaly_id) +
               " --test " + test +
               " --store --prediction-header --output " + output)
    shell_execute(command, output, test=test)


def i_create_anomaly_resources_from_anomaly_detector(
    step, test=None, output=None):
    """Step: I create BigML resources using anomaly detector to find anomaly
    scores for <test> and log predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler anomaly --anomaly " + world.anomaly['resource'] +
               " --test " + test +
               " --store --prediction-header --output " + output)
    shell_execute(command, output, test=test)


def i_create_anomaly_resources_from_anomaly_file(
    step, anomaly_file=None, test=None, output=None):
    """Step: I create BigML resources using anomaly detector in file
    <anomaly_file> to find anomaly scores for <test> and log predictions in
    <output>
    """
    ok_(anomaly_file is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler anomaly --anomalies " + anomaly_file +
               " --test " + test +
               " --store --prediction-header --output " + output)
    shell_execute(command, output, test=test)


def i_check_create_anomaly(step):
    """Step: I check that the anomaly detector has been created"""
    anomaly_file = "%s%sanomalies" % (world.directory, os.sep)
    message = None
    try:
        with open(anomaly_file) as handler:
            anomaly = check_resource(handler.readline().strip(),
                                     api=world.api)
        world.anomalies.append(anomaly['resource'])
        world.anomaly = anomaly
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_create_anomaly_scores(step):
    """Step: I check that the anomaly scores are ready"""
    predictions_lines = 0
    message = None
    try:
        predictions_file = world.output
        with open(predictions_file) as handler:
            predictions_lines = 0
            for _ in handler:
                predictions_lines += 1
            if predictions_lines != world.test_lines:
                message = "predictions lines: %s, test lines: %s" % (
                    predictions_lines, world.test_lines)
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_anomaly_scores(step, check_file):
    """Step: the local anomaly scores file is like <check_file>"""
    check_file = res_filename(check_file)
    predictions_file = world.output
    message = None
    try:
        message = check_rows_equal(predictions_file, check_file)
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_anomaly_has_id_fields(step, id_fields=None):
    """Checking that the anomaly detector has the correct id fields"""
    ok_(id_fields is not None)
    id_fields = json.loads(id_fields)
    id_fields.sort()
    anomaly_id_fields = world.anomaly.get("object", {}).get("id_fields")
    anomaly_id_fields.sort()
    eq_(len(anomaly_id_fields), len(id_fields))
    eq_(anomaly_id_fields, id_fields)


def i_create_all_anomaly_resources_with_mapping(
    step, data=None, test=None, fields_map=None, output=None):
    """Step: I create BigML resources uploading train <data> file to find
    anomaly scores for <test> remotely with mapping file <fields_map> and log
    predictions in <output>
    """
    ok_(data is not None and test is not None and output is not None
        and fields_map is not None)
    test = res_filename(test)
    command = ("bigmler anomaly --remote --train " + res_filename(data) +
               " --test " + test +
               " --fields-map " + res_filename(fields_map) +
               " --store --prediction-header --output " + output)
    shell_execute(command, output, test=test)


def i_create_all_anomaly_resources_with_test_split(
    step, data=None, test_split=None, output=None):
    """Step: I create BigML resources uploading train <data> file to find
    anomaly scores with test split <test_split> remotely and log predictions
    in <output>
    """
    ok_(data is not None and output is not None and test_split is not None)
    data = res_filename(data)
    command = ("bigmler anomaly --remote --train " + data +
               " --test-split " + test_split +
               " --store --output " + output)
    shell_execute(command, output, data=data, test_split=test_split)


def i_check_no_local_csv(step):
    """Step: no local CSV file is created"""
    files = [file_name for file_name in os.listdir(world.directory)
             if file_name.endswith('.csv')]
    eq_(len(files), 0, msg="Found unexpected files: %s" % ", ".join(files))


def i_check_create_batch_anomaly_score_dataset(step):
    """Step: I check that the batch anomaly scores dataset exists"""
    dataset_file = os.path.join(world.directory, "batch_anomaly_score_dataset")
    message = None
    try:
        with open(dataset_file) as handler:
            dataset = check_resource(handler.readline().strip(),
                                     api=world.api)
        world.datasets.append(dataset['resource'])
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_top_anomalies(step, top_anomalies):
    """Step: the top anomalies in the anomaly detector are <top_anomalies>"""
    eq_(int(top_anomalies),
        len(world.anomaly.get('object', []).get(
            'model', []).get('top_anomalies')))


def i_check_forest_size(step, forest_size):
    """Step: the forest size in the anomaly detector is <forest_size>"""
    eq_(int(forest_size),
        world.anomaly.get('object', []).get('forest_size'))


def i_check_dataset_lines_number(step, lines_number):
    """Step: the number of records in the top anomalies dataset is
    <top_anomalies>
    """
    eq_(int(lines_number),
        world.dataset.get('object', []).get('rows'))
