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
import nose
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
                if options is None or options.find('--prediction-header') == -1:
                    # test file has headers in it, so first line must be ignored
                    world.test_lines -= 1
            if test_split is not None:
                data_lines = file_number_of_lines(data) - 1
                world.test_lines = int(data_lines * float(test_split))

            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create BigML resources uploading train "(.*?)" file to find anomaly scores for the training set remotely saved to dataset with no CSV output and log resources in "([^"]*)"$')
def i_create_all_anomaly_resources_without_test_split(step, data=None, output_dir=None):
    if data is None or output_dir is None:
        assert False
    command = ("bigmler anomaly --remote --train " + data +
               " --store --score --no-csv --to-dataset --output-dir " + output_dir)
    shell_execute(command, "%s/x.csv" % output_dir, data=data, test_split=1)

#@step(r'I create BigML resources uploading train "(.*?)" file to find anomaly scores for the training set remotely saved to dataset with no CSV output and log resources in "([^"]*)"$')
def i_create_all_anomaly_resources_without_test_split(step, data=None, output_dir=None):
    if data is None or output_dir is None:
        assert False
    command = ("bigmler anomaly --remote --train " + res_filename(data) +
               " --store --score --no-csv --to-dataset --output-dir " + output_dir)
    shell_execute(command, "%s/x.csv" % output_dir, data=data, test_split=1)

#@step(r'I create BigML resources uploading train "(.*?)" file to find anomaly scores with test split "(.*?)" remotely saved to dataset with no CSV output and log resources in "([^"]*)"$')
def i_create_all_anomaly_resources_with_test_split_no_CSV(step, data=None, test_split=None, output_dir=None):
    if data is None or output_dir is None or test_split is None:
        assert False
    command = ("bigmler anomaly --remote --train " + res_filename(data) + " --test-split " + test_split +
               " --store --no-csv --to-dataset --output-dir " + output_dir)
    shell_execute(command, "%s/x.csv" % output_dir, data=data, test_split=test_split)


#@step(r'I create BigML anomaly detector from data <data> with options <options> and generate a new dataset of anomalies in "<output_dir>"$')
def i_create_anomaly_resources_with_options(step, data=None, options=None, output_dir=None):
    if data is None or output_dir is None or options is None:
        assert False
    command = ("bigmler anomaly --train " + res_filename(data) + " " +
               options +
               " --anomalies-dataset in --store --output-dir " + output_dir)
    shell_execute(command, "%s/x.csv" % output_dir, data=data)


#@step(r'I create BigML resources uploading train "(.*?)" file to create anomaly scores for "(.*?)" and log predictions in "([^"]*)"$')
def i_create_all_anomaly_resources(step, data=None, test=None, output=None):
    if data is None or test is None or output is None:
        assert False
    test = res_filename(test)
    command = ("bigmler anomaly --train " + res_filename(data) + " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources using source to find anomaly scores for "(.*?)" and log predictions in "([^"]*)"$')
def i_create_anomaly_resources_from_source(step, test=None, output=None):
    if test is None or output is None:
        assert False
    test = res_filename(test)
    command = ("bigmler anomaly --source " + world.source['resource'] +
               " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources using dataset to find anomaly scores for "(.*?)" and log predictions in "([^"]*)"$')
def i_create_anomaly_resources_from_dataset(step, test=None, output=None):
    if test is None or output is None:
        assert False
    test = res_filename(test)
    command = ("bigmler anomaly --dataset " + world.dataset['resource'] +
               " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources using local anomaly detector in "(.*)" to find anomaly scores for "(.*?)" and log predictions in "([^"]*)"$')
def i_create_anomaly_resources_from_local_anomaly_detector(step, directory=None, test=None, output=None):
    if test is None or output is None or directory is None:
        assert False
    test = res_filename(test)
    with open(os.path.join(directory, "anomalies")) as handler:
        anomaly_id = handler.readline().strip()
    command = ("bigmler anomaly --anomaly-file " +
               storage_file_name(directory, anomaly_id) +
               " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources using anomaly detector to find anomaly scores for "(.*?)" and log predictions in "([^"]*)"$')
def i_create_anomaly_resources_from_anomaly_detector(step, test=None, output=None):
    if test is None or output is None:
        assert False
    test = res_filename(test)
    command = ("bigmler anomaly --anomaly " + world.anomaly['resource'] +
               " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources using anomaly detector in file "(.*?)" to find anomaly scores for "(.*?)" and log predictions in "([^"]*)"$')
def i_create_anomaly_resources_from_anomaly_file(step, anomaly_file=None, test=None, output=None):
    if anomaly_file is None or test is None or output is None:
        assert Falsee
    test = res_filename(test)
    command = ("bigmler anomaly --anomalies " + anomaly_file +
               " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I check that the anomaly detector has been created')
def i_check_create_anomaly(step):
    anomaly_file = "%s%sanomalies" % (world.directory, os.sep)
    try:
        anomaly_file = open(anomaly_file, "r")
        anomaly = check_resource(anomaly_file.readline().strip(),
                                 api=world.api)
        world.anomalies.append(anomaly['resource'])
        world.anomaly = anomaly
        anomaly_file.close()
        assert True
    except Exception, exc:
        assert False, str(exc)


#@step(r'I check that the anomaly scores are ready')
def i_check_create_anomaly_scores(step):

    previous_lines = -1
    predictions_lines = 0
    try:
        predictions_file = world.output
        predictions_file = open(predictions_file, "r")
        predictions_lines = 0
        for line in predictions_file:
            predictions_lines += 1
        if predictions_lines == world.test_lines:
            assert True
        else:
            assert False, "predictions lines: %s, test lines: %s" % (predictions_lines, world.test_lines)
        predictions_file.close()
    except Exception, exc:
        assert False, str(exc)


#@step(r'the local anomaly scores file is like "(.*)"')
def i_check_anomaly_scores(step, check_file):
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
                dot = row[index].find(".")
                if dot > 0 or (check_row[index].find(".") > 0
                               and check_row[index].endswith(".0")):
                    try:
                        decimal_places = min(len(row[index]), len(check_row[index])) - dot - 1
                        row[index] = round(float(row[index]), decimal_places)
                        check_row[index] = round(float(check_row[index]), decimal_places)
                    except ValueError:
                        pass
                if check_row[index] != row[index]:
                    print row, check_row
                    assert False
        assert True
    except Exception, exc:
        assert False, str(exc)


#@step(r'I create BigML resources uploading train "(.*?)" file to find anomaly scores for "(.*?)" remotely with mapping file "(.*)" and log predictions in "([^"]*)"$')
def i_create_all_anomaly_resources_with_mapping(step, data=None, test=None, fields_map=None, output=None):
    if data is None or test is None or output is None or fields_map is None:
        assert False
    test = res_filename(test)
    command = ("bigmler anomaly --remote --train " + res_filename(data) + " --test " + test +
               " --fields-map " + res_filename(fields_map) +
               " --store --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources uploading train "(.*?)" file to find anomaly scores with test split "(.*?)" remotely and log predictions in "([^"]*)"$')
def i_create_all_anomaly_resources_with_test_split(step, data=None, test_split=None, output=None):
    if data is None or output is None or test_split is None:
        assert False
    data = res_filename(data)
    command = ("bigmler anomaly --remote --train " + data + " --test-split " + test_split +
               " --store --output " + output)
    shell_execute(command, output, data=data, test_split=test_split)


#@step(r'no local CSV file is created')
def i_check_no_local_CSV(step):
    files = [file_name for file_name in os.listdir(world.directory)
             if file_name.endswith('.csv')]
    if len(files) == 0:
        assert True
    else:
        assert False, ", ".join(files)


#@step(r'I check that the batch anomaly scores dataset exists')
def i_check_create_batch_anomaly_score_dataset(step):
    dataset_file = "%s%sbatch_anomaly_score_dataset" % (world.directory, os.sep)
    try:
        dataset_file = open(dataset_file, "r")
        dataset = check_resource(dataset_file.readline().strip(),
                                 api=world.api)
        world.datasets.append(dataset['resource'])
        dataset_file.close()
        assert True
    except Exception, exc:
        assert False, str(exc)

#@step(r'the top anomalies in the anomaly detector are <top_anomalies>')
def i_check_top_anomalies(step, top_anomalies):
    nose.tools.assert_equal(
        int(top_anomalies),
        len(world.anomaly.get('object', []).get('model', []).get('top_anomalies')))

#@step(r'the forest size in the anomaly detector is <forest_size>')
def i_check_forest_size(step, forest_size):
    nose.tools.assert_equal(
        int(forest_size),
        world.anomaly.get('object', []).get('forest_size'))

#@step(r'the number of records in the top anomalies dataset is <top_anomalies>')
def i_check_dataset_lines_number(step, lines_number):
    nose.tools.assert_equal(
        int(lines_number),
        world.dataset.get('object', []).get('rows'))
