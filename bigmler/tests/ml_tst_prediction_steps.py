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
from bigmler.checkpoint import file_number_of_lines
from bigmler.tests.common_steps import check_debug

#@step(r'I create BigML multi-label resources tagged as "(.*)" with "(.*)" label separator and (\d*) labels uploading train "(.*)" file with "(.*)" field separator and "(.*)" as multi-label fields using model_fields "(.*)" and objective "(.*)" to test "(.*)" and log predictions in "(.*)"')
def i_create_all_mlm_resources(step, tag=None, label_separator=None, number_of_labels=None, data=None, training_separator=None, ml_fields=None, model_fields=None, objective=None, test=None, output=None):
    if tag is None or label_separator is None or training_separator is None or number_of_labels is None or data is None or test is None or output is None or model_fields is None or objective is None or ml_fields is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    world.number_of_models = int(number_of_labels)
    test = res_filename(test)
    try:
        command = ("bigmler --multi-label --train " + res_filename(data) +
                   " --multi-label-fields " + ml_fields +
                   " --label-separator \"" + label_separator +
                   "\" --training-separator \"" + training_separator +
                   "\" --model-fields \" " + model_fields +
                   "\" --test " + test + " --store --output " + output +
                   " --objective " + objective +
                   " --tag " + tag + " --max-batch-models 1")
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = file_number_of_lines(test)
            # test file has headers in it, so first line must be ignored
            world.test_lines -= 1
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create BigML multi-label resources tagged as "(.*)" with "(.*)" label separator and (\d*) labels uploading train "(.*)" file with "(.*)" field separator to test "(.*)" and log predictions in "(.*)"')
def i_create_all_ml_resources(step, tag=None, label_separator=None, number_of_labels=None, data=None, training_separator=None, test=None, output=None):
    if tag is None or label_separator is None or training_separator is None or number_of_labels is None or data is None or test is None or output is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    world.number_of_models = int(number_of_labels)
    test = res_filename(test)
    try:
        command = ("bigmler --multi-label --train " + res_filename(data) +
                   " --label-separator \"" + label_separator +
                   "\" --training-separator \"" + training_separator +
                   "\" --test " + test + " --store --output " + output +
                   " --tag " + tag + " --max-batch-models 1")
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = file_number_of_lines(test)
            # test file has headers in it, so first line must be ignored
            world.test_lines -= 1
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)



#@step(r'I create BigML multi-label resources using models tagged as "(.*)" to test "(.*)" and log predictions in "(.*)"')
def i_predict_ml_from_model_tag(step, tag=None, test=None, output=None):
    if tag is None or test is None or output is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    test = res_filename(test)
    try:
        command = ("bigmler --multi-label --model-tag " + tag + " --test " +
                   test + " --store --output " + output +
                   " --max-batch-models 1")
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = file_number_of_lines(test)
            # test file has headers in it, so first line must be ignored
            world.test_lines -= 1
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)

#@step(r'I create BigML multi-label resources with labels "(.*)" and objective "(.*)" using models tagged as "(.*)" to test "(.*)" and log predictions in "(.*)"')
def i_predict_ml_from_model_tag_with_labels_with_objective(step, labels=None, objective=None, tag=None, test=None, output=None):
    if (tag is None or labels is None or test is None or output is None
            or objective is None):
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    test = res_filename(test)
    try:
        command = ("bigmler --multi-label --model-tag " + tag + " --labels " +
                   labels + " --test " + test + " --store --output " + output +
                   " --objective " + objective + " --max-batch-models 1")
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = file_number_of_lines(test)
            # test file has headers in it, so first line must be ignored
            world.test_lines -= 1
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create BigML multi-label resources with labels "([^"]*)" using models tagged as "(.*)" to test "(.*)" and log predictions in "(.*)"')
def i_predict_ml_from_model_tag_with_labels(step, labels=None, tag=None, test=None, output=None):
    if tag is None or labels is None or test is None or output is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    test = res_filename(test)
    try:
        command = ("bigmler --multi-label --model-tag " + tag + " --labels " +
                   labels + " --test " + test + " --store --output " + output +
                   " --max-batch-models 1")
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = file_number_of_lines(test)
            # test file has headers in it, so first line must be ignored
            world.test_lines -= 1
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'Then I check the extended file "(.*)" has been created')
def i_check_local_file(step, path=None):
    if path is None:
        assert False
    try:
        handler = open(path, "r")
        world.headers = handler.readline().strip()
        world.first_row = handler.readline().strip()
    except IOError:
        assert False

#@step(r'the headers of the local extended file are "(.*)"')
def i_check_headers_file(step, headers=None):
    if headers is None:
        assert False
    if headers==world.headers:
        assert True
    else:
        assert False, ("The expected headers are:\n%s\nand the"
                       " ones found are:\n%s" % (headers, world.headers))

#@step(r'the first row of the local extended file is "(.*)"')
def i_check_first_row_file(step, first_row=None):
    if first_row is None:
        assert False
    if first_row==world.first_row:
        assert True
    else:
        assert False, ("The expected first row is:\n%s\n"
                       "and the one found is:\n%s" % (first_row,
                                                      world.first_row))

#@step(r'I create BigML a multi-label source with "(.*)" label separator and (\d+) labels from train "(.*)" file with "(.*)" field separator and "(.*)" as multi-label fields and objective "(.*)" and output in "(.*)"')
def i_create_ml_source(step, label_separator=None, number_of_labels=None, data=None, training_separator=None, multi_label_fields=None, objective=None, output_dir=None):
    if label_separator is None or training_separator is None or number_of_labels is None or data is None or multi_label_fields is None or output_dir is None or objective is None:
        assert False
    world.directory = output_dir
    world.folders.append(world.directory)
    try:
        command = ("bigmler --multi-label --train " + res_filename(data) +
                   " --label-separator \"" + label_separator +
                   "\" --training-separator \"" + training_separator +
                   "\" --multi-label-fields " + multi_label_fields +
                   " --objective " + objective + " --store --output-dir " +
                   output_dir +
                   "  --no-dataset --no-model --max-batch-models 1")
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = output_dir
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create BigML multi-label resources tagged as "(.*)" with "(.*)" label separator and (\d*) labels uploading train "(.*)" file with "(.*)" field separator and (\d+) models ensembles to test "(.*)" and log predictions in "(.*)"')
def i_create_all_ml_resources_and_ensembles(step, tag=None, label_separator=None, number_of_labels=None, data=None, training_separator=None, number_of_models=None, test=None, output=None):
    if tag is None or label_separator is None or training_separator is None or number_of_labels is None or data is None or test is None or output is None or number_of_models is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    world.number_of_models = int(number_of_labels) * int(number_of_models)
    test = res_filename(test)
    try:
        command = ("bigmler --multi-label --train " + res_filename(data) +
                   " --label-separator \"" + label_separator +
                   "\" --training-separator \"" + training_separator +
                   "\" --test " + test + " --number-of-models " +
                   str(number_of_models) + " --store --output " + output +
                   " --tag " + tag + " --max-batch-models 1")
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = file_number_of_lines(test)
            # test file has headers in it, so first line must be ignored
            world.test_lines -= 1
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create BigML (multi-label\s)?resources using source and (\d+) models ensembles to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_and_ensembles_from_source(step, multi_label=None, number_of_models=None, test=None, output=None):
    if test is None or output is None or number_of_models is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    multi_label = "" if multi_label is None else " --multi-label "
    test = res_filename(test)
    try:
        command = ("bigmler "+ multi_label +"--source " +
                   world.source['resource'] + " --number-of-models " +
                   str(number_of_models) + " --test " + test +
                    " --store --output " + output)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = file_number_of_lines(test)
            # test file has headers in it, so first line must be ignored
            world.test_lines -= 1
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)

#@step(r'I create BigML (multi-label\s)?resources using dataset and (\d+) models ensembles to test "(.*)" and log predictions in "(.*)"')
def i_create_resources_and_ensembles_from_dataset(step, multi_label=None, number_of_models=None, test=None, output=None):
    if test is None or output is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    multi_label = "" if multi_label is None else " --multi-label "
    test = res_filename(test)
    try:
        command = ("bigmler "+ multi_label +"--dataset " +
                   world.dataset['resource'] + " --number-of-models " +
                   str(number_of_models) + " --test " + test +
                   " --store --output " + output)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = file_number_of_lines(test)
            # test file has headers in it, so first line must be ignored
            world.test_lines -= 1
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)
