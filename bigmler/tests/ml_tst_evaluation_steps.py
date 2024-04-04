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

from bigmler.tests.common_steps import shell_execute
from bigmler.tests.world import world, res_filename, ok_


def i_create_all_ml_evaluations(
    step, tag=None, label_separator=None, number_of_labels=None, data=None,
    training_separator=None, output=None):
    """Step: I create BigML multi-label resources tagged as <tag> with
    <label_separator> label separator and <number_of_labels> labels uploading
    train <data> file with <training_separator> field separator to evaluate
    and log evaluation in <output>
    """
    ok_(tag is not None and label_separator is not None and
        training_separator is not None and number_of_labels is not None
        and data is not None and output is not None)
    world.number_of_models = int(number_of_labels)
    command = ("bigmler --multi-label --train " + res_filename(data) +
        " --label-separator \"" + label_separator +
        "\" --training-separator \"" + training_separator +
        "\" --evaluate --store --output " + output +
        " --tag " + tag + " --max-batch-models 1")
    shell_execute(command, output)


def i_create_all_ml_resources_for_evaluation(
    step, tag=None, label_separator=None, number_of_labels=None, data=None,
    training_separator=None, output=None):
    """Step: I create BigML multi-label resources tagged as <tag> with
    <label_separator> label separator and <number_of_labels> labels uploading
    train <data> file with <training_separator> field separator to evaluate
    and log in <output>
    """
    ok_(tag is not None and label_separator is not None and
        training_separator is not None and number_of_labels is not None
        and data is not None and output is not None)
    world.number_of_models = int(number_of_labels)
    command = ("bigmler --multi-label --train " + res_filename(data) +
        " --label-separator \"" + label_separator +
        "\" --training-separator \"" + training_separator +
        "\" --store --output " + output +
        " --tag " + tag + " --max-batch-models 1")
    shell_execute(command, output)


def i_check_evaluation_ready(step):
    """Step: I check that the evaluation is ready"""
    evaluation_file = os.path.join(world.directory, "evaluation.json")
    message = None
    try:
        with open(evaluation_file) as handler:
            json.loads(handler.readline().strip())
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_create_ml_evaluations_from_source(step, output=None):
    """Step: I create BigML <multi-label> resources using source to evaluate
    and log evaluation in <output>
    """
    ok_(output is not None)
    command = ("bigmler --multi-label --source " + world.source['resource'] +
        " --evaluate --store --output " + output)
    shell_execute(command, output)


def i_create_ml_evaluations_from_dataset(step, output=None):
    """Step: I create BigML <multi-label> resources using dataset to evaluate
    and log evaluation in <output>
    """
    ok_(output is not None)
    command = ("bigmler --multi-label --dataset " +
               world.dataset['resource'] + " --evaluate --store --output "
               + output)
    shell_execute(command, output)


def i_create_ml_evaluations_from_models(step, models_file=None, output=None):
    """Step: I create BigML <multi-label> resources using models in file
    <models_file> to evaluate and log evaluation in <output>
    """
    ok_(output is not None and models_file is not None)
    command = ("bigmler --multi-label --models " + models_file +
               " --dataset " + world.dataset['resource'] +
               " --evaluate --store --output " + output)
    shell_execute(command, output)


def i_create_ml_evaluations_from_tagged_models(step, tag=None, output=None):
    """Step: I create BigML <multi-label> resources using models tagged as
    <tag> to evaluate and log evaluation in <output>
    """
    ok_(output is not None and tag is not None)
    command = ("bigmler --multi-label --model-tag " + tag + " --dataset " +
               world.dataset['resource'] + " --evaluate --store --output "
               + output)
    shell_execute(command, output)
