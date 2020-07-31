# -*- coding: utf-8 -*-
#
# Copyright 2019-2020 BigML
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
from bigmler.checkpoint import file_number_of_lines
from bigmler.utils import storage_file_name, open_mode
from bigmler.tests.common_steps import check_debug
from nose.tools import ok_, assert_equal, assert_not_equal
import bigmler.tests.basic_tst_prediction_steps as test_pred
import bigmler.tests.basic_deepnet_steps as test_dn


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


#@step(r'I create BigML resources using model to test "(.*)" and log predictions in "(.*)"')
def i_create_fs_resources_from_model(step, test=None, output=None):
    ok_(test is not None and output is not None)
    test = res_filename(test)

    models = [world.model["resource"], world.deepnet["resource"]]
    command = ("bigmler fusion --fusion-models " +
               ",".join(models) + " --test \"" +
               test + "\" --store --output " +
               output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML resources using model to test "(.*)" as batch prediction and log predictions in "(.*)"')
def i_create_fs_resources_from_model_remote(step, test=None, output=None):
    ok_(test is not None and output is not None)
    test = res_filename(test)

    models = [world.model["resource"], world.deepnet["resource"]]
    command = ("bigmler fusion --fusion-models " +
               ",".join(models) + " --test \"" + test +
               "\" --store --remote --output " +
               output)
    shell_execute(command, output, test=test)

#@step(r'I create BigML resources using model to test "(.*)" as batch prediction with output format "(.*)" and log predictions in "(.*)"')
def i_create_fs_resources_from_model_remote_with_options(step, test=None, output=None, options_file=None):
    ok_(test is not None and output is not None and options_file is not None)
    test = res_filename(test)
    options_file = res_filename(options_file)

    models = [world.model["resource"], world.deepnet["resource"]]
    command = ("bigmler fusion --fusion-models " +
               ",".join(models) + " --test \"" + test +
               "\" --batch-prediction-attributes " + options_file +
               " --store --remote --output " +
               output)
    shell_execute(command, output, test=test)

#@step(r'I create BigML resources using model to test "(.*)" and an evaluation and log predictions in "(.*)"')
def i_create_fs_resources_from_mode_and_evaluate(step, output=None):
    ok_(output is not None)
    models = [world.model["resource"], world.deepnet["resource"]]
    command = ("bigmler fusion --fusion-models " +
               ",".join(models) + " --test-dataset \"" +
               world.dataset["resource"] +
               "\" --evaluate --store --remote --output " +
               output)
    shell_execute(command, output)

#@step(r'I check that the fusion model has been created')
def i_check_create_fusion(step):
    fs_file = "%s%sfusions" % (world.directory, os.sep)
    try:
        fs_file = open(fs_file, "r")
        fs = check_resource(fs_file.readline().strip(),
                            world.api.get_fusion)
        world.fusions.append(fs['resource'])
        world.fusion = fs
        fs_file.close()
    except Exception as exc:
        assert False, str(exc)

def setup_for_fusion(step, train=None, output_dir=None):
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

#@step(r'I create BigML fusion resources uploading train "(.*)" file to evaluate and log evaluation in "([^"]*)"$')
def i_create_all_fs_resources_to_evaluate(step, train=None, test=None, output=None):
    models = [world.model["resource"], world.deepnet["resource"]]
    command = ("bigmler fusion --fusion-models " + ",".join(models) +
               " --test \"" +
               test +
               "\" --evaluate" +
               " --store --output " + output)
    shell_execute(command, output)
