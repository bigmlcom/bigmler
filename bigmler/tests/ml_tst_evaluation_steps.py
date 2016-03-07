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
from bigmler.tests.world import world, res_filename
from subprocess import check_call, CalledProcessError
from bigmler.checkpoint import file_number_of_lines
from bigmler.tests.common_steps import check_debug

#@step(r'I create BigML multi-label resources tagged as "(.*)" with "(.*)" label separator and "(\d*)" labels uploading train "(.*)" file with "(.*)" field separator to evaluate and log evaluation in "(.*)"')
def i_create_all_ml_evaluations(step, tag=None, label_separator=None, number_of_labels=None, data=None, training_separator=None, output=None):
    if tag is None or label_separator is None or training_separator is None or number_of_labels is None or data is None or output is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    world.number_of_models = int(number_of_labels)
    try:
        command = "bigmler --multi-label --train " + res_filename(data) + " --label-separator \"" + label_separator + "\" --training-separator \"" + training_separator + "\" --evaluate --store --output " + output + " --tag " + tag + " --max-batch-models 1"
        retcode = check_call(check_debug(command), shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)

#@step(r'I create BigML multi-label resources tagged as "(.*)" with "(.*)" label separator and "(\d*)" labels uploading train "(.*)" file with "(.*)" field separator to evaluate and log in "(.*)"')
def i_create_all_ml_resources_for_evaluation(step, tag=None, label_separator=None, number_of_labels=None, data=None, training_separator=None, output=None):
    if tag is None or label_separator is None or training_separator is None or number_of_labels is None or data is None or output is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    world.number_of_models = int(number_of_labels)
    try:
        command = "bigmler --multi-label --train " + res_filename(data) + " --label-separator \"" + label_separator + "\" --training-separator \"" + training_separator + "\" --store --output " + output + " --tag " + tag + " --max-batch-models 1"
        retcode = check_call(check_debug(command), shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I check that the evaluation is ready')
def i_check_evaluation_ready(step):
    evaluation_file = "%s%sevaluation.json" % (world.directory, os.sep)
    try:
        evaluation_file = open(evaluation_file, "r")
        evaluation = json.loads(evaluation_file.readline().strip())
        evaluation_file.close()
        assert True
    except:
        assert False

#@step(r'I create BigML multi-label\sresources using source to evaluate and log evaluation in "(.*)"')
def i_create_ml_evaluations_from_source(step, output=None):
    if output is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    try:
        command = "bigmler --multi-label --source " + world.source['resource'] + " --evaluate --store --output " + output
        retcode = check_call(check_debug(command), shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create BigML multi-label\sresources using dataset to evaluate and log evaluation in "(.*)"')
def i_create_ml_evaluations_from_dataset(step, output=None):
    if output is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    try:
        command = ("bigmler --multi-label --dataset " +
                   world.dataset['resource'] + " --evaluate --store --output "
                   + output)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create BigML multi-label\sresources using models in file "(.*)" to evaluate and log evaluation in "(.*)"')
def i_create_ml_evaluations_from_models(step, models_file=None, output=None):
    if output is None or models_file is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    try:
        command = ("bigmler --multi-label --models " + models_file +
                   " --dataset " + world.dataset['resource'] +
                   " --evaluate --store --output " + output)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)

#@step(r'I create BigML multi-label\sresources using models tagged as "(.*)" to evaluate and log evaluation in "(.*)"')
def i_create_ml_evaluations_from_tagged_models(step, tag=None, output=None):
    if output is None or tag is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    try:
        command = ("bigmler --multi-label --model-tag " + tag + " --dataset " +
                   world.dataset['resource'] + " --evaluate --store --output "
                   + output)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)
