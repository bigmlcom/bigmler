# -*- coding: utf-8 -*-
#
# Copyright 2016 BigML
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
import json
from bigmler.tests.world import world, res_filename
from subprocess import check_call, CalledProcessError
from bigml.api import check_resource
from bigml.io import UnicodeReader
from bigmler.processing.models import MONTECARLO_FACTOR
from bigmler.checkpoint import file_number_of_lines
from bigmler.utils import storage_file_name, open_mode, decode2
from bigmler.utils import PYTHON3
from bigmler.tests.common_steps import check_debug
from nose.tools import ok_, assert_equal, assert_not_equal


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

#@step(r'I create BigML resources uploading train "(.*?)" file with no headers to test "(.*?)" with no headers and log predictions in "([^"]*)"$')
def i_create_all_lr_resources_with_no_headers(step, data=None, test=None, output=None):
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler logistic-regression --train " + res_filename(data) +
               " --test " + test +
               " --store --no-balance-fields --no-bias --output " + output +
               " --no-train-header --no-test-header")
    shell_execute(command, output, test=test, options='--prediction-header')


#@step(r'I create BigML resources uploading train "(.*?)" file to test "(.*?)" and log predictions in "([^"]*)"$')
def i_create_all_lr_resources(step, data=None, test=None, output=None):
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler logistic-regression --train " + res_filename(data) +
               " --test " + test +
               " --store --no-balance-fields --no-bias --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML (multi-label\s)?resources using source to test "(.*)" and log predictions in "(.*)"')
def i_create_lr_resources_from_source(step, multi_label=None, test=None, output=None):
    ok_(test is not None and output is not None)
    test = res_filename(test)
    multi_label = "" if multi_label is None else " --multi-label "
    command = ("bigmler logistic-regression "+ multi_label +"--source " +
               world.source['resource'] + " --test " + test +
               " --store --no-bias --no-balance-fields --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML (multi-label\s)?resources using dataset to test "(.*)" and log predictions in "(.*)"')
def i_create_lr_resources_from_dataset(step, multi_label=None, test=None, output=None):
    ok_(test is not None and output is not None)
    multi_label = "" if multi_label is None else " --multi-label "
    test = res_filename(test)
    command = ("bigmler logistic-regression "+ multi_label +"--dataset " +
               world.dataset['resource'] + " --test " + test +
               " --store --no-balance-fields --no-bias --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources using model to test "(.*)" and log predictions in "(.*)"')
def i_create_lr_resources_from_model(step, test=None, output=None):
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler logistic-regression --logistic-regression " +
               world.logistic_regression['resource'] + " --test " +
               test + " --store --no-balance-fields --no-bias --output " +
               output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources using model to test "(.*)" as batch prediction and log predictions in "(.*)"')
def i_create_lr_resources_from_model_remote(step, test=None, output=None):
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler logistic-regression --logistic-regression " +
               world.logistic_regression['resource'] + " --test " + test +
               " --store --no-balance-fields --no-bias --remote --output " +
               output)
    shell_execute(command, output, test=test)


#@step(r'I check that the logistic regression model has been created')
def i_check_create_lr_model(step):
    lr_file = "%s%slogistic_regressions" % (world.directory, os.sep)
    try:
        lr_file = open(lr_file, "r")
        lr = check_resource(lr_file.readline().strip(),
                            world.api.get_logistic_regression)
        world.logistic_regressions.append(lr['resource'])
        world.logistic_regression = lr
        lr_file.close()
        assert True
    except Exception, exc:
        assert False, str(exc)


#@step(r'I create BigML logistic regression resources uploading train "(.*)" file to evaluate and log evaluation in "([^"]*)"$')
def i_create_all_lr_resources_to_evaluate(step, data=None, output=None):
    ok_(data is not None and output is not None)
    command = ("bigmler logistic-regression --train " + res_filename(data) +
               " --evaluate" +
               " --store --no-balance-fields --no-bias --output " + output)
    shell_execute(command, output)
