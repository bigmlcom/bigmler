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
from nose.tools import assert_equal, assert_not_equal, ok_
from bigmler.tests.world import world, res_filename
from subprocess import check_call, CalledProcessError
from bigml.api import check_resource, HTTP_NOT_FOUND
from bigmler.checkpoint import file_number_of_lines
from bigmler.tests.common_steps import (check_debug, store_init_resources,
                          store_final_resources, check_init_equals_final)
from bigmler.tests.basic_tst_prediction_steps import shell_execute


#@step(r'I create a BigML source from file "(.*)" storing results in "(.*)"')
def i_create_source_from_file(step, data=None, output_dir=None):
    ok_(data is not None and output_dir is not None)
    command = ("bigmler --train " + res_filename(data) + " --store --output-dir " +
               output_dir +
               " --no-dataset --no-model --store")
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None,
                  project=False)


def i_check_source_exists_by_id(step, source_id):
    source = check_resource(source_id,
                            world.api.get_source)
    assert_not_equal(source['code'], HTTP_NOT_FOUND)
    world.source = source


#@step(r'I check that the source exists$')
def i_check_source_exists(step):
    source_file = "%s%ssource" % (world.directory, os.sep)
    source_file = open(source_file, "r")
    source_id = source_file.readline().strip()
    source_file.close()
    i_check_source_exists_by_id(step, source_id)


#@step(r'I check that the failed source exists$')
def i_check_faulty_source_exists(step):
    source_file = "%s%ssource" % (world.directory, os.sep)
    source_file = open(source_file, "r")
    source_id = source_file.readline().strip()
    source_file.close()
    source = world.api.get_source(source_id)
    assert_not_equal(source['code'], HTTP_NOT_FOUND)
    world.source = source


#@step(r'I check that the source doesn\'t exist$')
def i_check_source_does_not_exist(step, source_id=None):
    if source_id is None:
        source_id = world.source['resource']
    source = world.api.get_source(source_id)
    assert_equal(source['code'], HTTP_NOT_FOUND)


#@step(r'I delete the source by id using --ids storing results in "(.*)"$')
def i_delete_source_by_ids(step, output_dir=None):
    if output_dir is None:
        assert False
    command = ("bigmler delete --ids " + world.source['resource'] +
               " --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


#@step(r'I delete the source by id using --ids and --dry-run storing results in "(.*)"$')
def i_delete_source_by_ids_dry(step, output_dir=None):
    if output_dir is None:
        assert False
    command = ("bigmler delete --ids " + world.source['resource'] +
               " --dry-run --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


#@step(r'I delete the source by id using --ids and --resource-types "(.*)" storing results in "(.*)"$')
def i_delete_source_by_ids_filtered(step, resource_types=None, output_dir=None):
    if output_dir is None or resource_types is None:
        assert False
    command = ("bigmler delete --ids " + world.source['resource'] +
               " --dry-run --output-dir " + output_dir +
               " --resource-types " + resource_types)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


#@step(r'I delete the source by id using --from-file and the source file storing results in "(.*)"$')
def i_delete_source_by_file(step, output_dir=None):
    if output_dir is None:
        assert False
    command = ("bigmler delete --from-file %s%ssource " % (output_dir, os.sep) +
               " --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


#@step(r'I delete the source by id using --from-file and --status faulty and the source file storing results in "(.*)"$')
def i_delete_source_faulty_by_file(step, output_dir=None):
    ok_(output_dir is not None)
    command = ("bigmler delete --from-file %s%ssource " % (output_dir, os.sep) +
               " --status faulty --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


#@step(r'I delete the source by id using --from-file, the source file and --resource-types "(.*)" storing results in "(.*)"$')
def i_delete_source_by_file_filtered(step, resource_types=None, output_dir=None):
    ok_(output_dir is not None and resource_types is not None)
    command = ("bigmler delete --from-file %s%ssource " % (output_dir, os.sep) +
               " --output-dir " + output_dir +
               " --resource-types " + resource_types)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


#@step(r'I store the source id as (lower|upper|reference)$')
def i_store_source_id_as_bound(step, which=None):
    if which == 'lower':
        world.source_lower = world.source['resource']
    elif which == 'upper':
        world.source_upper = world.source['resource']
    elif which == 'reference':
        world.source_reference = world.source['resource']


#@step(r'I delete the source using --older-than and --newer-than storing results in "(.*)"$')
def i_delete_source_older_newer(step, output_dir=None):
    ok_(output_dir is not None)
    command = ("bigmler delete --older-than " + world.source_upper +
               " --newer-than " + world.source_lower +
               " --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


#@step(r'I check that the reference source doesn\'t exist$')
def i_check_reference_source_does_not_exist(step):
    i_check_source_does_not_exist(step, source_id=world.source_reference)


#@step(r'I delete the source using --older-than and --newer-than with resource_types "(.*)" storing results in "(.*)"$')
def i_delete_source_older_newer_with_resource_types(step, resource_types=None, output_dir=None):
    ok_(output_dir is not None and resource_types is not None)
    command = ("bigmler delete --older-than " + world.source_upper +
               " --newer-than " + world.source_lower +
               " --resource-types " + resource_types +
               " --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


#@step(r'I check that the reference source exists$')
def i_check_reference_source_exists(step):
    i_check_source_exists_by_id(step, source_id=world.source_reference)


#@step(r'I create a BigML source from file "(.*)" with tag "(.*)" storing results in "(.*)"')
def i_create_source_from_file_with_tag(step, data=None, tag=None, output_dir=None):
    ok_(data is not None and output_dir is not None and tag is not None)
    command = ("bigmler --train " + res_filename(data) + " --store --output-dir " +
               output_dir + " --tag " + tag +
               " --no-dataset --no-model --store")
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)

#@step(r'I create a BigML source from file "(.*)" with tag "(.*)" storing results in "(.*)"')
def i_create_faulty_source_from_file_with_tag(step, data=None, tag=None, output_dir=None):
    ok_(data is not None and output_dir is not None and tag is not None)
    command = ("bigmler --train " + res_filename(data) + " --store --output-dir " +
               output_dir + " --tag " + tag +
               " --no-dataset --no-model --store")
    try:
        shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)
    except:
        pass


#@step(r'I delete the source using --newer-than and --source-tag "(.*)" storing results in "(.*)"$')
def i_delete_source_newer_and_tag(step, tag=None, output_dir=None):
    ok_(output_dir is not None and tag is not None)
    command = ("bigmler delete --newer-than " + world.source_lower +
               " --source-tag " + tag +
               " --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)



#@step(r'I delete the source using --newer-than and --status faulty and --source-tag "(.*)" storing results in "(.*)"$')
def i_delete_source_newer_faulty_and_tag(step, tag=None, output_dir=None):
    ok_(output_dir is not None and tag is not None)
    command = ("bigmler delete --newer-than " + world.source_lower +
               " --source-tag " + tag +
               " --status faulty --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)

#@step(r'I check that the upper source exists$')
def i_check_upper_source_exists(step):
    i_check_source_exists_by_id(step, source_id=world.source_upper)


#@step(r'I create a BigML dataset from the source with tag "(.*)" storing results in "(.*)"')
def i_create_dataset_from_source_with_tag(step, tag=None, output_dir=None):
    ok_(tag is not None and output_dir is not None)
    command = ("bigmler --source " + world.source['resource'] +
               " --tag " + tag +
               " --store --output-dir " + output_dir +
               " --no-model --store")
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


def i_check_dataset_exists_by_id(step, dataset_id):
    dataset = check_resource(dataset_id,
                             world.api.get_dataset)
    assert_not_equal(dataset['code'], HTTP_NOT_FOUND)
    world.dataset = dataset


#@step(r'I check that the dataset exists$')
def i_check_dataset_exists(step):
    dataset_file = "%s%sdataset" % (world.directory, os.sep)
    dataset_file = open(dataset_file, "r")
    dataset_id = dataset_file.readline().strip()
    dataset_file.close()
    i_check_dataset_exists_by_id(step, dataset_id)


#@step(r'I check that the dataset doesn\'t exist$')
def i_check_dataset_does_not_exist(step, dataset_id=None):
    if dataset_id is None:
        dataset_id = world.dataset['resource']
    dataset = world.api.get_dataset(dataset_id)
    assert_equal(dataset['code'], HTTP_NOT_FOUND)


#@step(r'I delete the resources using --newer-than and --all-tag "(.*)" storing results in "(.*)"$')
def i_delete_resources_newer_and_tag(step, tag=None, output_dir=None):
    ok_(output_dir is not None and tag is not None)
    command = ("bigmler delete --newer-than " + world.source_lower +
               " --all-tag " + tag +
               " --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


#@step(r'I create BigML resources uploading train "(.*)" storing results in "(.*)"$')
def i_create_all_resources_in_output_dir(step, data=None, output_dir=None):
    ok_(output_dir is not None and data is not None)
    command = ("bigmler --train " + res_filename(data) +
               " --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


#@step(r'I check that the number of resources has changed$')
def i_check_changed_number_of_resources(step):
    store_final_resources()
    assert (world.counters['sources']['final'] != world.counters['sources']['init'] or
            world.counters['datasets']['final'] != world.counters['datasets']['init'] or
            world.counters['models']['final'] != world.counters['models']['init'] )


#@step(r'I delete the resources from the output directory$')
def i_delete_resources_from_dir(step):
    command = ("bigmler delete --from-dir " + world.directory +
               " --output-dir " + world.directory)
    shell_execute(command, os.path.join(world.directory, "p.csv"), test=None)


#@step(r'I store the number of existing resources$')
def i_store_the_number_of_resources(step):
    store_init_resources()


#@step(r'the number of resources has not changed$')
def i_check_equal_number_of_resources(step):
    store_final_resources()
    check_init_equals_final()
