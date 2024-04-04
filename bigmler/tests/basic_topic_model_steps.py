# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2016-2024 BigML
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

from bigmler.tests.common_steps import shell_execute, check_rows_equal
from bigmler.tests.world import world, res_filename, ok_, eq_


def i_create_all_td_resources_from_dataset(
    step, test=None, options=None, output=None):
    """Step: I create BigML topic model resources from dataset to test <test>
    with options <options> and log predictions in <output>
    """
    ok_(test is not None and options is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler topic-model " +
               "--minimum-name-terms 0 --dataset " +
               world.dataset['resource'] + " --test " + test +
               " --store --output " + output + " " + options)
    shell_execute(command, output, test=test, options=options)


def i_create_all_td_resources_from_source(
    step, test=None, options=None, output=None):
    """Step: I create BigML topic model resources from source to test <test>
    with options <options> and log predictions in <output>
    """
    ok_(test is not None and options is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler topic-model " +
               "--minimum-name-terms 0 --source " +
               world.source['resource'] + " --test " + test +
               " --store --output " + output + " " + options)
    shell_execute(command, output, test=test, options=options)


def i_create_all_td_resources_from_model(
    step, test=None, options=None, output=None):
    """Step: I create BigML topic model resources from model to test <test>
    with options <options> and log predictions in <output>
    """
    ok_(test is not None and options is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler topic-model " +
               "--minimum-name-terms 0 --topic-model " +
               world.topic_model['resource'] + " --test " + test +
               " --store --output " + output + " " + options)
    shell_execute(command, output, test=test, options=options)


def i_create_topic_distribution_from_model_remote(
    step, test=None, options=None, output=None):
    """Step: I create BigML batch topic distribution from model to test
    <test> with options <options> and log predictions in <output>
    """
    ok_(test is not None and options is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler topic-model --remote" +
               " --minimum-name-terms 0 --topic-model " +
               world.topic_model['resource'] + " --test " + test +
               " --store --output " + output + " " + options)
    shell_execute(command, output, test=test, options=options)


def i_check_create_topic_model(step):
    """Step: I check that the topic model has been created"""
    topic_model_file = os.path.join(world.directory, "topic_models")
    message = None
    try:
        with open(topic_model_file) as handler:
            topic_model = check_resource(handler.readline().strip(),
                                         world.api.get_topic_model)
            world.topic_models.append(topic_model['resource'])
            world.topic_model = topic_model
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_create_topic_distribution(step):
    """Step: I check that the topic distribution has been created"""
    batch_topic_distribution_file = os.path.join(world.directory,
                                                 "batch_topic_distribution")
    message = None
    try:
        with open(batch_topic_distribution_file) as handler:
            batch_topic_distribution = check_resource(
                handler.readline().strip(),
                world.api.get_batch_topic_distribution)
            world.batch_topic_distribution.append(
                batch_topic_distribution['resource'])
            world.batch_topic_distribution = batch_topic_distribution
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_create_topic_distributions(step):
    """Step: I check that the remote topic distributions is ready"""
    predictions_lines = 0
    message = None
    try:
        predictions_file = world.output
        with open(predictions_file) as handler:
            predictions_lines = 0
            for _ in handler:
                predictions_lines += 1
            eq_(predictions_lines, world.test_lines,
                msg=f"topic distribution lines: {predictions_lines},"
                    f" test lines: {world.test_lines}")
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_check_topic_distributions(step, check_file):
    """Step: the local topic distributions file is like <check_file>"""
    check_file = res_filename(check_file)
    predictions_file = world.output
    message = None
    #pylint: disable=locally-disabled,import-outside-toplevel
    try:
        message = check_rows_equal(predictions_file, check_file)
    except Exception:
        import traceback
        message = traceback.format_exc()
    ok_(message is None, msg=message)


def i_create_topic_model_from_dataset(step, output=None):
    """Step: I create BigML topic model from dataset"""
    ok_(output is not None)
    command = ("bigmler topic-model " +
               "--minimum-name-terms 0 --dataset " +
               world.dataset['resource'] +
               " --store --output " + output)
    shell_execute(command, output)
