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

from bigmler.tests.common_steps import shell_execute
from bigmler.tests.world import world, res_filename, ok_


def i_create_all_lr_resources_with_no_headers(
    step, data=None, test=None, output=None):
    """Step: I create BigML resources uploading train <data> file with no
    headers to test <test> with no headers and log predictions in <output>
    """
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler linear-regression --train " + res_filename(data) +
               " --test " + test +
               " --store --no-bias --output " + output +
               " --no-train-header --default-numeric-value mean" +
               " --no-test-header")
    shell_execute(command, output, test=test, options='--prediction-header')


def i_create_all_lr_resources(step, data=None, test=None, output=None):
    """Step: I create BigML resources uploading train <data> file to test
    <test> and log predictions in <output>
    """
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler linear-regression --train " + res_filename(data) +
               " --test " + test +
               " --store --no-bias --default-numeric-value mean" +
               " --output " + output)
    shell_execute(command, output, test=test)


def i_create_lr_resources_from_source(
    step, multi_label=None, test=None, output=None):
    """Step: I create BigML <multi-label> resources using source to test
    <test> and log predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    multi_label = "" if multi_label is None else " --multi-label "
    command = ("bigmler linear-regression "+ multi_label +"--source " +
               world.source['resource'] + " --test " + test +
               " --store --no-bias --default-numeric-value mean" +
               " --output " + output)
    shell_execute(command, output, test=test)


def i_create_lr_resources_from_dataset(
    step, multi_label=None, test=None, output=None):
    """Step: I create BigML <multi-label> resources using dataset to test
    <test> and log predictions in <output>
    """
    ok_(test is not None and output is not None)
    multi_label = "" if multi_label is None else " --multi-label "
    test = res_filename(test)
    command = ("bigmler linear-regression "+ multi_label +"--dataset " +
               world.dataset['resource'] + " --test " + test +
               " --store --no-bias --default-numeric-value mean" +
               " --output " + output)
    shell_execute(command, output, test=test)


def i_create_lr_resources_from_model(step, test=None, output=None):
    """Step: I create BigML resources using model to test <test> and log
    predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler linear-regression --linear-regression " +
               world.linear_regression['resource'] + " --test " +
               test + " --store --no-bias --default-numeric-value mean" +
               " --output " + output)
    shell_execute(command, output, test=test)


def i_create_lr_resources_from_model_remote(step, test=None, output=None):
    """Step: I create BigML resources using model to test <test> as batch
    prediction and log predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler linear-regression --linear-regression " +
               world.linear_regression['resource'] + " --test " + test +
               " --store --no-bias --default-numeric-value mean" +
               " --remote --output " + output)
    shell_execute(command, output, test=test, options="--no-header")


def i_check_create_lr_model(step):
    """Step: I check that the linear regression model has been created"""
    lr_file = os.path.join(world.directory, "linear_regressions")
    message = None
    try:
        with open(lr_file) as handler:
            linr = check_resource(handler.readline().strip(),
                                  world.api.get_linear_regression)
            world.linear_regressions.append(linr['resource'])
            world.linear_regression = linr
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_create_all_lr_resources_to_evaluate(step, data=None, output=None):
    """Step: I create BigML linear regression resources uploading train
    <data> file to evaluate and log evaluation in <output>
    """
    ok_(data is not None and output is not None)
    command = ("bigmler linear-regression --train " + res_filename(data) +
               " --evaluate --default-numeric-value mean " +
               " --store --no-bias --output " + output)
    shell_execute(command, output)
