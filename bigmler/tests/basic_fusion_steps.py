# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2019-2024 BigML
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

import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.basic_deepnet_steps as test_dn

from bigmler.tests.common_steps import shell_execute
from bigmler.tests.world import world, res_filename, ok_


def i_create_fs_resources_from_model(step, test=None, output=None):
    """Step: I create BigML resources using model to test <test> and log
    predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)

    models = [world.model["resource"], world.deepnet["resource"]]
    command = ("bigmler fusion --fusion-models " +
               ",".join(models) + " --test \"" +
               test + "\" --store --output " +
               output)
    shell_execute(command, output, test=test)


def i_create_fs_resources_from_model_remote(step, test=None, output=None):
    """Step: I create BigML resources using model to test <test> as batch
    prediction and log predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)

    models = [world.model["resource"], world.deepnet["resource"]]
    command = ("bigmler fusion --fusion-models " +
               ",".join(models) + " --test \"" + test +
               "\" --store --remote --output " +
               output)
    shell_execute(command, output, test=test, options="--no-header")


def i_create_fs_resources_from_model_remote_with_options(
    step, test=None, output=None, options_file=None):
    """Step: I create BigML resources using model to test <test> as batch
    prediction with output format <options_file> and log predictions in
    <output>
    """
    ok_(test is not None and output is not None and options_file is not None)
    test = res_filename(test)
    options_file = res_filename(options_file)

    models = [world.model["resource"], world.deepnet["resource"]]
    command = ("bigmler fusion --fusion-models " +
               ",".join(models) + " --test \"" + test +
               "\" --batch-prediction-attributes " + options_file +
               " --store --remote --output " +
               output)
    shell_execute(command, output, test=test, options="--no-header")


def i_create_fs_resources_from_mode_and_evaluate(step, output=None):
    """Step: I create BigML resources using model to test <test> and an
    evaluation and log predictions in <output>
    """
    ok_(output is not None)
    models = [world.model["resource"], world.deepnet["resource"]]
    command = ("bigmler fusion --fusion-models " +
               ",".join(models) + " --test-dataset \"" +
               world.dataset["resource"] +
               "\" --evaluate --store --remote --output " +
               output)
    shell_execute(command, output, options="--no-header")


def i_check_create_fusion(step):
    """Step: I check that the fusion model has been created"""
    fs_file = os.path.join(world.directory, "fusions")
    message = None
    try:
        with open(fs_file) as handler:
            fusion = check_resource(handler.readline().strip(),
                                    world.api.get_fusion)
            world.fusions.append(fusion['resource'])
            world.fusion = fusion
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)


def setup_for_fusion(step, train=None, output_dir=None):
    """Creating models needed for a fusion"""
    train = res_filename(train)
    command = ("bigmler --train \"" +
               train + "\" --store --output-dir " +
               output_dir)
    shell_execute(command, "%s/predictions" % output_dir)
    test_pred.i_check_create_source(step)
    test_pred.i_check_create_dataset(step)
    test_pred.i_check_create_model(step)

    command = ("bigmler deepnet --dataset \"" +
               world.dataset["resource"] + "\" --store --output-dir " +
               output_dir)
    shell_execute(command, "%s/predictions" % output_dir)
    test_dn.i_check_create_dn_model(step)


def i_create_all_fs_resources_to_evaluate(step, train=None, test=None, output=None):
    """Step: I create BigML fusion resources uploading train <train> file to
    evaluate and log evaluation in <output>
    """
    models = [world.model["resource"], world.deepnet["resource"]]
    command = ("bigmler fusion --fusion-models " + ",".join(models) +
               " --test \"" +
               test +
               "\" --evaluate" +
               " --store --output " + output)
    shell_execute(command, output)
