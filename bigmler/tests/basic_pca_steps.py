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

from bigmler.tests.common_steps import shell_execute
from bigmler.tests.world import world, res_filename, ok_


def i_create_all_pca_resources_with_no_headers(step, data=None, test=None, output=None):
    """Step: I create BigML PCA resources uploading train <data> file with no
    headers to test <test> with no headers and log projections in <output>
    """
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler pca --train " + res_filename(data) +
               " --test " + test +
               " --store --output " + output +
               " --no-train-header --no-test-header")
    shell_execute(command, output, test=test, options="--projection-header")


def i_create_all_pca_resources(step, data=None, test=None, output=None):
    """Step: I create BigML PCA resources uploading train <data> file to test
    <test> and log predictions in <output>
    """
    ok_(data is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler pca --train " + res_filename(data) +
               " --test " + test +
               " --store --output "
               + output)
    shell_execute(command, output, test=test)


def i_create_pca_resources_from_dataset(step, test=None, output=None):
    """Step: I create BigML PCA resources using dataset to test <test> and log
    predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler pca --dataset " +
               world.dataset['resource'] + " --test " + test +
               " --store --output " + output)
    shell_execute(command, output, test=test)


def i_create_pca_resources_from_source(
    step, test=None, output=None):
    """Step: I create BigML PCA resources using source to test <test>
    and log predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler pca --source " + world.source['resource']
               + " --test " + test + " --store --output " + output)
    shell_execute(command, output, test=test)


def i_create_pca_resources_from_model(step, test=None, output=None):
    """Step: I create BigML PCA resources using model to test <test> and log
    predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler pca --pca " +
               world.pca['resource'] + " --test " +
               test + " --store --output " +
               output)
    shell_execute(command, output, test=test)


def i_create_pca_resources_from_model_remote(step, test=None, output=None):
    """Step: I create BigML PCA resources using model to test <test> as batch
    prediction and log predictions in <output>
    """
    ok_(test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler pca --pca " +
               world.pca['resource'] + " --test " + test +
               " --store --remote --output " +
               output)
    shell_execute(command, output, test=test, options="--no-header")


def i_check_create_pca_model(step):
    """Step: I check that the pca model has been created"""
    pca_file = os.path.join(world.directory, "pcas")
    message = None
    try:
        with open(pca_file) as handler:
            pca = check_resource(handler.readline().strip(),
                                 world.api.get_pca)
            world.pcas.append(pca['resource'])
            world.pca = pca
    except Exception as exc:
        message = str(exc)
    ok_(message is None, msg=message)
