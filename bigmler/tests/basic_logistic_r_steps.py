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
    command = ("bigmler logistic-regression --train " + res_filename(data) +
               " --test " + test +
               " --store --no-balance-fields --no-bias --output " + output +
               " --no-train-header --no-test-header")
    shell_execute(command, output, test=test)


def i_create_all_lr_resources(step, data=None, test=None, output=None):
    """Step: I create BigML resources uploading train <data> file to test
    <test> and log predictions in <output>
    """
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler logistic-regression --train " + res_filename(data) +
               " --test " + test +
               " --store --no-balance-fields --no-bias --output " + output)
    shell_execute(command, output, test=test)


def i_create_lr_resources_from_source(
    step, multi_label=None, test=None, output=None):
    """Step: I create BigML <multi-label> resources using source to test
    <test> and log predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    multi_label = "" if multi_label is None else " --multi-label "
    command = ("bigmler logistic-regression "+ multi_label +"--source " +
               world.source['resource'] + " --test " + test +
               " --store --no-bias --no-balance-fields --output " + output)
    shell_execute(command, output, test=test)


def i_create_lr_resources_from_dataset(
    step, multi_label=None, test=None, output=None):
    """Step: I create BigML <multi-label> resources using dataset to test
    <test> and log predictions in <output>
    """
    ok_(test is not None and output is not None)
    multi_label = "" if multi_label is None else " --multi-label "
    test = res_filename(test)
    command = ("bigmler logistic-regression "+ multi_label +"--dataset " +
               world.dataset['resource'] + " --test " + test +
               " --store --no-balance-fields --no-bias --output " + output)
    shell_execute(command, output, test=test)


def i_create_lr_resources_from_model(step, test=None, output=None):
    """Step: I create BigML resources using model to test <test> and log
    predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler logistic-regression --logistic-regression " +
               world.logistic_regression['resource'] + " --test " +
               test + " --store --no-balance-fields --no-bias --output " +
               output)
    shell_execute(command, output, test=test)


def i_create_lr_resources_from_model_remote(step, test=None, output=None):
    """Step: I create BigML resources using model to test <test> as batch
    prediction and log predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler logistic-regression --logistic-regression " +
               world.logistic_regression['resource'] + " --test " + test +
               " --store --no-balance-fields " +
               " --no-bias --remote --output " +
               output)
    shell_execute(command, output, test=test, options="--no-header")


def i_create_lr_resources_from_model_with_op(step, test=None, output=None,
                                             operating_point=None):
    """Step: I create BigML resources using model to test <test> as batch
    prediction and log predictions in <operating_point>
    """
    ok_(test is not None and output is not None and \
        operating_point is not None)
    test = res_filename(test)
    operating_point = res_filename(operating_point)
    command = ("bigmler logistic-regression --logistic-regression " +
               world.logistic_regression['resource'] + " --test " + test +
               " --operating-point " + operating_point +
               " --store --no-balance-fields --no-bias --output " +
               output)
    shell_execute(command, output, test=test)


def i_check_create_lr_model(step):
    """Step: I check that the logistic regression model has been created"""
    lr_file = os.path.join(world.directory, "logistic_regressions")
    message = None
    try:
        with open(lr_file) as handler:
            logr = check_resource(handler.readline().strip(),
                                  world.api.get_logistic_regression)
            world.logistic_regressions.append(logr['resource'])
            world.logistic_regression = logr
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_create_all_lr_resources_to_evaluate(step, data=None, output=None):
    """Step: I create BigML logistic regression resources uploading train
    <train> file to evaluate and log evaluation in <output>
    """
    ok_(data is not None and output is not None)
    command = ("bigmler logistic-regression --train " + res_filename(data) +
               " --evaluate" +
               " --store --no-balance-fields --no-bias --output " + output)
    shell_execute(command, output)
