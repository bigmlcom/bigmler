# -*- coding: utf-8 -*-
#
# Copyright 2016-2020 BigML
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
import json
from bigmler.tests.world import world, res_filename
from subprocess import check_call, CalledProcessError
from bigml.api import check_resource
from bigml.io import UnicodeReader
from bigmler.processing.models import MONTECARLO_FACTOR
from bigmler.checkpoint import file_number_of_lines
from bigmler.utils import storage_file_name, open_mode
from bigmler.tests.common_steps import check_debug
from nose.tools import ok_, assert_equal, assert_not_equal, assert_almost_equal


def shell_execute(command, output, test=None, options=None,
                  test_rows=None, project=True):
    """Excute bigmler command in shell

    """
    command = check_debug(command, project=project)
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    try:
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
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
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create BigML topic model resources from dataset to test "(.*)" with options "(.*)" and log predictions in "(.*)"')
def i_create_all_td_resources_from_dataset( \
    step, test=None, options=None, output=None):
    ok_(test is not None and options is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler topic-model " +
               "--minimum-name-terms 0 --dataset " +
               world.dataset['resource'] + " --test " + test +
               " --store --output " + output + " " + options)
    shell_execute(command, output, test=test, options=options)


#@step(r'I create BigML topic model resources from source to test "(.*)" with options "(.*)" and log predictions in "(.*)"')
def i_create_all_td_resources_from_source( \
    step, test=None, options=None, output=None):
    ok_(test is not None and options is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler topic-model " +
               "--minimum-name-terms 0 --source " +
               world.source['resource'] + " --test " + test +
               " --store --output " + output + " " + options)
    shell_execute(command, output, test=test, options=options)


#@step(r'I create BigML topic model resources from model to test "(.*)" with options "(.*)" and log predictions in "(.*)"')
def i_create_all_td_resources_from_model( \
    step, test=None, options=None, output=None):
    ok_(test is not None and options is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler topic-model " +
               "--minimum-name-terms 0 --topic-model " +
               world.topic_model['resource'] + " --test " + test +
               " --store --output " + output + " " + options)
    shell_execute(command, output, test=test, options=options)


#@step(r'I create BigML batch topic distribution from model to test "(.*)" with options "(.*)" and log predictions in "(.*)"')
def i_create_topic_distribution_from_model_remote( \
    step, test=None, options=None, output=None):
    ok_(test is not None and options is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler topic-model --remote" +
               " --minimum-name-terms 0 --topic-model " +
               world.topic_model['resource'] + " --test " + test +
               " --store --output " + output + " " + options)
    shell_execute(command, output, test=test, options=options)


#@step(r'I check that the topic model has been created')
def i_check_create_topic_model(step):
    topic_model_file = "%s%stopic_models" % (world.directory, os.sep)
    try:
        topic_model_file = open(topic_model_file, "r")
        topic_model = check_resource(topic_model_file.readline().strip(),
                                     world.api.get_topic_model)
        world.topic_models.append(topic_model['resource'])
        world.topic_model = topic_model
        topic_model_file.close()
        assert True
    except Exception as exc:
        assert False, str(exc)


#@step(r'I check that the topic distribution has been created')
def i_check_create_topic_distribution(step):
    batch_topic_distribution_file = "%s%sbatch_topic_distribution" % (
        world.directory, os.sep)
    try:
        batch_topic_distribution_file = open(
            batch_topic_distribution_file, "r")
        batch_topic_distribution = check_resource(
            batch_topic_distribution_file.readline().strip(),
            world.api.get_batch_topic_distribution)
        world.batch_topic_distribution.append(
            batch_topic_distribution['resource'])
        world.batch_topic_distribution = batch_topic_distribution
        batch_topic_distribution_file.close()
        assert True
    except Exception as exc:
        assert False, str(exc)


#@step(r'I check that the remote topic distributions is ready')
def i_check_create_topic_distributions(step):
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
            assert False, "topic distribution lines: %s, test lines: %s" % (
                predictions_lines, world.test_lines)
        predictions_file.close()
    except Exception as exc:
        assert False, str(exc)


#@step(r'the local topic distributions file is like "(.*)"')
def i_check_topic_distributions(step, check_file):
    check_file = res_filename(check_file)
    predictions_file = world.output
    import traceback
    try:
        with UnicodeReader(predictions_file) as predictions_file:
            with UnicodeReader(check_file) as check_file:
                for row in predictions_file:
                    check_row = next(check_file)
                    assert len(check_row) == len(row)
                    for index in range(len(row)):
                        dot = row[index].find(".")
                        decimal_places = 1
                        if dot > 0 or (check_row[index].find(".") > 0
                                       and check_row[index].endswith(".0")):
                            try:
                                decimal_places = min( \
                                    len(row[index]),
                                    len(check_row[index])) - dot - 1
                                row[index] = round(float(row[index]),
                                                   decimal_places)
                                check_row[index] = round(
                                    float(check_row[index]), decimal_places)
                            except ValueError:
                                decimal_places = 1
                            assert_almost_equal(check_row[index], row[index],
                                                places=(decimal_places - 1))
                        else:
                            assert_equal(check_row[index], row[index])
    except Exception as exc:
        assert False, traceback.format_exc()


#@step(r'I create BigML topic model from dataset"')
def i_create_topic_model_from_dataset( \
    step, output=None):
    ok_(output is not None)
    command = ("bigmler topic-model " +
               "--minimum-name-terms 0 --dataset " +
               world.dataset['resource'] +
               " --store --output " + output)
    shell_execute(command, output)
