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
                        options.find('--projection-header') == -1:
                    # test file has headers in it, so first line must be ignored
                    world.test_lines -= 1
            elif test_rows is not None:
                world.test_lines = test_rows
                if options is not None and \
                        options.find('--projection-header') > -1:
                    world.test_lines += 1
            elif options is not None and \
                    options.find('--projection-header') > -1:
                world.test_lines += 1
            world.output = output
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)

#@step(r'I create BigML PCA resources uploading train "(.*?)" file with no headers to test "(.*?)" with no headers and log projections in "([^"]*)"$')
def i_create_all_pca_resources_with_no_headers(step, data=None, test=None, output=None):
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler pca --train " + res_filename(data) +
               " --test " + test +
               " --store --output " + output +
               " --no-train-header --no-test-header")
    shell_execute(command, output, test=test, options="--projection-header")


#@step(r'I create BigML PCA resources uploading train "(.*?)" file to test "(.*?)" and log predictions in "([^"]*)"$')
def i_create_all_pca_resources(step, data=None, test=None, output=None):
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler pca --train " + res_filename(data) +
               " --test " + test +
               " --store --output "
               + output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML PCA resources using dataset to test "(.*)" and log predictions in "(.*)"')
def i_create_pca_resources_from_dataset(step, test=None, output=None):
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler pca --dataset " +
               world.dataset['resource'] + " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML PCA resources using source to test "(.*)"
# and log predictions in "(.*)"')
def i_create_pca_resources_from_source( \
    step, test=None, output=None):
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler pca --source " + world.source['resource']
               + " --test " + test + " --store --output " + output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML PCA resources using model to test "(.*)" and log predictions in "(.*)"')
def i_create_pca_resources_from_model(step, test=None, output=None):
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler pca --pca " +
               world.pca['resource'] + " --test " +
               test + " --store --output " +
               output)
    shell_execute(command, output, test=test)


#@step(r'I create BigML PCA resources using model to test "(.*)" as batch prediction and log predictions in "(.*)"')
def i_create_pca_resources_from_model_remote(step, test=None, output=None):
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler pca --pca " +
               world.pca['resource'] + " --test " + test +
               " --store --remote --output " +
               output)
    shell_execute(command, output, test=test)


#@step(r'I check that the pca model has been created')
def i_check_create_pca_model(step):
    pca_file = "%s%spcas" % (world.directory, os.sep)
    try:
        pca_file = open(pca_file, "r")
        pca = check_resource(pca_file.readline().strip(),
                             world.api.get_pca)
        world.pcas.append(pca['resource'])
        world.pca = pca
        pca_file.close()
    except Exception as exc:
        assert False, str(exc)
