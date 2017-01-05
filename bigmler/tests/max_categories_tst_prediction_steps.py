# -*- coding: utf-8 -*-
#
# Copyright 2014-2017 BigML
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
import csv
import json
from bigmler.tests.world import world, res_filename
from subprocess import check_call, CalledProcessError
from bigmler.checkpoint import file_number_of_lines
from bigml.api import check_resource
from bigmler.tests.common_steps import check_debug


#@step(r'I create BigML resources with (\d+) as categories limit and (.*) as objective field and model fields "(.*)" using dataset to test "(.*)" and log predictions in "(.*)"')
def i_create_all_mc_resources_from_dataset_with_model_fields(step, max_categories=None, objective=None, model_fields=None, test=None, output=None):
    if max_categories is None or test is None or output is None or model_fields is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    test = res_filename(test)
    try:
        command = ("bigmler --dataset " + world.dataset['resource'] +
                   " --max-categories " + max_categories + " --objective " +
                   objective + " --test " + test + " --store --output " +
                   output + " --model-fields \"" + model_fields + "\"")
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = file_number_of_lines(test)
            # test file has headers in it, so first line must be ignored
            world.test_lines -= 1
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create BigML resources from "(.*)" with (\d+) as categories limit and (.*) as objective field to test "(.*)" and log predictions in "(.*)"')
def i_create_all_mc_resources(step, data, max_categories=None, objective=None, test=None, output=None):
    if max_categories is None or test is None or output is None or objective is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    test = res_filename(test)
    try:
        command = ("bigmler --train " + res_filename(data) + " --max-categories " +
                   max_categories + " --objective " + objective + " --test " +
                   test + " --store --output " + output)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = file_number_of_lines(test)
            # test file has headers in it, so first line must be ignored
            world.test_lines -= 1
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create BigML resources with (\d+) as categories limit and (.*) as objective field using source to test "(.*)" and log predictions in "(.*)"')
def i_create_all_mc_resources_from_source(step, max_categories=None, objective=None, test=None, output=None):
    if max_categories is None or test is None or output is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    test = res_filename(test)
    try:
        command = ("bigmler --source " + world.source['resource'] +
                   " --max-categories " + max_categories +  " --objective " +
                   objective + " --test " + test + " --store --output " +
                   output)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = file_number_of_lines(test)
            # test file has headers in it, so first line must be ignored
            world.test_lines -= 1
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create BigML resources with (\d+) as categories limit and (.*) as objective field using dataset to test "(.*)" and log predictions in "(.*)"')
def i_create_all_mc_resources_from_dataset(step, max_categories=None, objective=None, test=None, output=None):
    if max_categories is None or test is None or output is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    test = res_filename(test)
    try:
        command = ("bigmler --dataset " + world.dataset['resource'] +
                   " --max-categories " + max_categories + " --objective " +
                   objective + " --test " + test + " --store --output " +
                   output)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = file_number_of_lines(test)
            # test file has headers in it, so first line must be ignored
            world.test_lines -= 1
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)


#@step(r'I create BigML resources using models in file "(.*)" to test "(.*)" and log predictions with combine method in "(.*)"')
def i_create_all_mc_resources_from_models(step, models_file=None, test=None, output=None):
    if models_file is None or test is None or output is None:
        assert False
    world.directory = os.path.dirname(output)
    world.folders.append(world.directory)
    test = res_filename(test)
    try:
        command = ("bigmler --models " + models_file +
                   " --method combined --test " + test + " --store --output "
                   + output)
        command = check_debug(command)
        retcode = check_call(command, shell=True)
        if retcode < 0:
            assert False
        else:
            world.test_lines = file_number_of_lines(test)
            # test file has headers in it, so first line must be ignored
            world.test_lines -= 1
            world.output = output
            assert True
    except (OSError, CalledProcessError, IOError) as exc:
        assert False, str(exc)

#@step(r'I check that the max_categories datasets have been created')
def i_check_create_max_categories_datasets(step):
    import traceback
    dataset_file = "%s%sdataset_parts" % (world.directory, os.sep)
    try:
        dataset_file = open(dataset_file, "r")
        number_of_datasets = 0
        for line in dataset_file:
            dataset_id = line.strip()
            dataset = check_resource(dataset_id,
                                     world.api.get_dataset)
            assert ('user_metadata' in dataset['object'] and 'max_categories'
                    in dataset['object']['user_metadata'])
            world.datasets.append(dataset['resource'])
            number_of_datasets += 1
        world.number_of_models = number_of_datasets
        dataset_file.close()
        assert True
    except Exception, exc:
        assert False, traceback.format_exc()
