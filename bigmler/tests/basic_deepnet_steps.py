# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2017-2024 BigML
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


def i_create_all_dn_resources_with_no_headers(
    step, data=None, test=None, output=None):
    """Step: I create BigML resources uploading train <data> file with no
    headers to test <test> with no headers and log predictions in <output>
    """
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler deepnet --train " + res_filename(data) +
               " --test " + test +
               " --store --output " + output +
               " --no-train-header --no-test-header")
    shell_execute(command, output, test=test, options='--no-header')


def i_create_all_dn_resources(step, data=None, test=None, output=None):
    """Step: I create BigML resources uploading train <data> file to test
    <test> and log predictions in <output>
    """
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler deepnet --train " + res_filename(data) +
               " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)

def i_create_all_dn_resources_headers(step, data=None, test=None, output=None):
    """Step: I create BigML resources uploading train <data> file to test
    <test> with headers and log predictions in <output>
    """
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler deepnet --train " + res_filename(data) +
               " --test " + test +
               " --store --prediction-header --prediction-info full" +
               " --output " + output)
    shell_execute(command, output, test=test)


def i_create_dn_resources_from_source(
    step, multi_label=None, test=None, output=None):
    """Step: I create BigML <multi-label> resources using source to test
    <test> and log predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    multi_label = "" if multi_label is None else " --multi-label "
    command = ("bigmler deepnet "+ multi_label +"--source " +
               world.source['resource'] + " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


def i_create_dn_resources_from_dataset(step, multi_label=None, test=None, output=None):
    """Step: I create BigML <multi-label> resources using dataset to test
    <test> and log predictions in <output>
    """
    ok_(test is not None and output is not None)
    multi_label = "" if multi_label is None else " --multi-label "
    test = res_filename(test)
    command = ("bigmler deepnet "+ multi_label +"--dataset " +
               world.dataset['resource'] + " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


def i_create_dn_resources_from_model(step, test=None, output=None):
    """Step: I create BigML resources using model to test <test> and log
    predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler deepnet --deepnet " +
               world.deepnet['resource'] + " --test " +
               test + " --store --output " +
               output)
    shell_execute(command, output, test=test)


def i_create_dn_resources_from_model_remote(step, test=None, output=None):
    """Step: I create BigML resources using model to test <test> as batch
    prediction and log predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler deepnet --deepnet " +
               world.deepnet['resource'] + " --test " + test +
               " --store --prediction-header --remote --output " +
               output)
    shell_execute(command, output, test=test)


def i_create_dn_resources_from_model_remote_with_options(
    step, test=None, options_file=None, output=None):
    """Step: I create BigML resources using model to test <test> as batch
    prediction with output format <options_file> and log predictions in
    <output>
    """
    ok_(test is not None and output is not None and options_file is not None)
    test = res_filename(test)
    options_file = res_filename(options_file)
    command = ("bigmler deepnet --deepnet " +
               world.deepnet['resource'] + " --test " + test +
               " --batch-prediction-attributes " + options_file +
               " --store --remote --output " +
               output)
    shell_execute(command, output, test=test, options="--no-header")


def i_check_create_dn_model(step):
    """Step: I check that the deepnet model has been created"""
    dn_file = os.path.join(world.directory, "deepnets")
    message = None
    try:
        with open(dn_file) as handler:
            dn_ = check_resource(handler.readline().strip(),
                                world.api.get_deepnet)
        world.deepnets.append(dn_['resource'])
        world.deepnet = dn_
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def i_create_all_dn_resources_to_evaluate(step, data=None, output=None):
    """Step: I create BigML deepnet resources uploading train <data> file to
    evaluate and log evaluation in <output>
    """
    ok_(data is not None and output is not None)
    command = ("bigmler deepnet --train " + res_filename(data) +
               " --evaluate" +
               " --store --output " + output)
    shell_execute(command, output)
