# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2014-2024 BigML
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

from bigml.api import check_resource, HTTP_NOT_FOUND

from bigmler.tests.common_steps import (
    store_init_resources, store_final_resources,
    check_init_equals_final, shell_execute)
from bigmler.tests.world import world, res_filename, ok_, eq_


def i_create_source_from_file(step, data=None, output_dir=None):
    """Step: I create a BigML source from file <data> storing results
    in <output_dir>
    """
    ok_(data is not None and output_dir is not None)
    command = ("bigmler --train " + res_filename(data) +
               " --store --output-dir " +
               output_dir + " --no-dataset --no-model --store")
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None,
                  project=False)


def i_create_project(step, name=None, output_dir=None):
    """Step: I create a BigML project with name <name> storing results in
    <output_dir>
    """
    ok_(name is not None and output_dir is not None)
    command = ("bigmler project --name " + name + " --store --output-dir " +
               output_dir)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None,
                  project=True)


def i_check_project_exists(step):
    """Step: I check that the project exists"""
    project_file = os.path.join(world.directory, "project")
    with open(project_file) as handler:
        project_id = handler.readline().strip()
    project = check_resource(project_id,
                             world.api.get_project)
    ok_(project['code'] != HTTP_NOT_FOUND)
    world.project = project


def i_check_source_exists_by_id(step, source_id):
    """Checking that source exists"""
    source = check_resource(source_id,
                            world.api.get_source)
    ok_(source['code'] != HTTP_NOT_FOUND)
    world.source = source


def i_check_source_exists(step):
    """Step: I check that the source exists"""
    source_file = os.path.join(world.directory, "source")
    with open(source_file) as handler:
        lines = handler.readlines()
        source_id = lines[-2].strip()
    i_check_source_exists_by_id(step, source_id)


def i_check_faulty_source_exists(step):
    """Step: I check that the failed source exists"""
    i_check_source_exists(step)


def i_check_source_does_not_exist(step, source_id=None):
    """Step: I check that the source doesn't exist"""
    if source_id is None:
        source_id = world.source['resource']
    source = world.api.get_source(source_id)
    eq_(source['code'], HTTP_NOT_FOUND)


def i_check_project_does_not_exist(step):
    """Step: I check that the project doesn't exist"""
    project = world.api.get_project(world.project["resource"])
    eq_(project['code'], HTTP_NOT_FOUND)


def i_delete_source_by_ids(step, output_dir=None):
    """Step: I delete the source by id using --ids storing results
    in <output_dir>
    """
    ok_(output_dir is not None)
    command = ("bigmler delete --ids " + world.source['resource'] +
               " --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


def i_delete_source_by_ids_dry(step, output_dir=None):
    """Step: I delete the source by id using --ids and --dry-run storing
    results in <output_dir>
    """
    ok_(output_dir is not None)
    command = ("bigmler delete --ids " + world.source['resource'] +
               " --dry-run --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


def i_delete_source_by_ids_filtered(
    step, resource_types=None, output_dir=None):
    """Step: I delete the source by id using --ids and --resource-types
    <resource_types> storing results in <output_dir>
    """
    ok_(output_dir is not None and resource_types is not None)
    command = ("bigmler delete --ids " + world.source['resource'] +
               " --dry-run --output-dir " + output_dir +
               " --resource-types " + resource_types)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


def i_delete_source_by_file(step, output_dir=None):
    """Step: I delete the source by id using --from-file and the source file
    storing results in <output_dir>
    """
    ok_(output_dir is not None)
    command = (
        "bigmler delete --from-file %s%ssource " % (output_dir, os.sep) +
        " --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


def i_delete_source_faulty_by_file(step, output_dir=None):
    """Step: I delete the source by id using --from-file and --status faulty
    and the source file storing results in <output_dir>
    """
    ok_(output_dir is not None)
    command = (
        "bigmler delete --from-file %s%ssource " % (output_dir, os.sep) +
        " --status faulty --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


def i_delete_source_by_file_filtered(
    step, resource_types=None, output_dir=None):
    """Step: I delete the source by id using --from-file, the source file and
    --resource-types <resource_types> storing results in <output_dir>
    """
    ok_(output_dir is not None and resource_types is not None)
    command = (
        "bigmler delete --from-file %s%ssource " % (output_dir, os.sep) +
        " --output-dir " + output_dir +
        " --resource-types " + resource_types)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


def i_delete_source_older_newer(step, output_dir=None):
    """Step: I delete the source using --older-than and --newer-than storing
    results in <output_dir>
    """
    ok_(output_dir is not None)
    command = ("bigmler delete --older-than " + step.bigml["source_upper"] +
               " --newer-than " + step.bigml["source_lower"] +
               " --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


def i_check_reference_source_does_not_exist(step):
    """Step: I check that the reference source doesn't exist"""
    i_check_source_does_not_exist(
        step, source_id=step.bigml["source_reference"])


def i_delete_source_older_newer_with_resource_types(
    step, resource_types=None, output_dir=None):
    """Step: I delete the source using --older-than and --newer-than with
    resource_types <resource_types> storing results in <output_dir>
    """
    ok_(output_dir is not None and resource_types is not None)
    command = ("bigmler delete --older-than " + step.bigml["source_upper"] +
               " --newer-than " + step.bigml["source_lower"] +
               " --resource-types " + resource_types +
               " --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


def i_check_reference_source_exists(step):
    """Step: I check that the reference source exists"""
    i_check_source_exists_by_id(step, source_id=step.bigml["source_reference"])


def i_create_source_from_file_with_tag(
    step, data=None, tag=None, output_dir=None):
    """Step: I create a BigML source from file <data> with tag <tag> storing
    results in <output_dir>
    """
    ok_(data is not None and output_dir is not None and tag is not None)
    command = (
        "bigmler --train " + res_filename(data) + " --store --output-dir " +
        output_dir + " --tag " + tag +
        " --no-dataset --no-model --store")
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)

def i_create_faulty_source_from_file_with_tag(
    step, data=None, tag=None, output_dir=None):
    """Step: I create a BigML source from file <data> with tag <tag> storing
    results in <output_dir>
    """
    ok_(data is not None and output_dir is not None and tag is not None)
    command = (
        "bigmler --train " + res_filename(data) + " --store --output-dir " +
        output_dir + " --tag " + tag +
        " --no-dataset --no-model --store")
    try:
        shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)
    except Exception:
        pass


def i_delete_source_newer_and_tag(step, tag=None, output_dir=None):
    """Step: I delete the source using --newer-than and --source-tag
    <tag> storing results in <output_dir>
    """
    ok_(output_dir is not None and tag is not None)
    command = ("bigmler delete --newer-than " + step.bigml["source_lower"] +
               " --source-tag " + tag +
               " --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


def i_delete_source_newer_faulty_and_tag(step, tag=None, output_dir=None):
    """Step: I delete the source using --newer-than and --status faulty and
    --source-tag <tag> storing results in <output_dir>
    """
    ok_(output_dir is not None and tag is not None)
    command = ("bigmler delete --newer-than " + step.bigml["source_lower"] +
               " --source-tag " + tag +
               " --status faulty --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


def i_check_upper_source_exists(step):
    """Step: I check that the upper source exists"""
    i_check_source_exists_by_id(step, source_id=step.bigml["source_upper"])


def i_create_dataset_from_source_with_tag(step, tag=None, output_dir=None):
    """Step: I create a BigML dataset from the source with tag <tag> storing
    results in <output_dir>
    """
    ok_(tag is not None and output_dir is not None)
    command = ("bigmler --source " + world.source['resource'] +
               " --tag " + tag +
               " --store --output-dir " + output_dir +
               " --no-model --store")
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


def i_check_dataset_exists_by_id(step, dataset_id):
    """Checking that dataset exists"""
    dataset = check_resource(dataset_id,
                             world.api.get_dataset)
    ok_(dataset['code'] != HTTP_NOT_FOUND)
    world.dataset = dataset


def i_check_dataset_exists(step):
    """Step: I check that the dataset exists"""
    dataset_file = os.path.join(world.directory, "dataset")
    with open(dataset_file) as handler:
        dataset_id = handler.readline().strip()
    i_check_dataset_exists_by_id(step, dataset_id)


def i_check_dataset_does_not_exist(step, dataset_id=None):
    """Step: I check that the dataset doesn't exist$"""
    if dataset_id is None:
        dataset_id = world.dataset['resource']
    dataset = world.api.get_dataset(dataset_id)
    eq_(dataset['code'], HTTP_NOT_FOUND)


def i_delete_resources_newer_and_tag(step, tag=None, output_dir=None):
    """Step: I delete the resources using --newer-than and --all-tag <tag>
    storing results in <output_dir>
    """
    ok_(output_dir is not None and tag is not None)
    command = ("bigmler delete --newer-than " + step.bigml["source_lower"] +
               " --all-tag " + tag +
               " --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


def i_create_all_resources_in_output_dir(step, data=None, output_dir=None):
    """Step: I create BigML resources uploading train <data> storing results
    in <output_dir>
    """
    ok_(output_dir is not None and data is not None)
    command = ("bigmler --train " + res_filename(data) +
               " --output-dir " + output_dir)
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)


def i_check_changed_number_of_resources(step):
    """Step: I check that the number of resources has changed"""
    store_final_resources()
    ok_(world.counters['sources']['final'] !=
        world.counters['sources']['init'] or
        world.counters['datasets']['final'] !=
        world.counters['datasets']['init'] or
        world.counters['models']['final'] !=
        world.counters['models']['init'] )


def i_delete_resources_from_dir(step):
    """Step: I delete the resources from the output directory"""
    command = ("bigmler delete --from-dir " + world.directory +
               " --output-dir " + world.directory)
    shell_execute(command, os.path.join(world.directory, "p.csv"), test=None)


def i_store_the_number_of_resources(step):
    """Step: I store the number of existing resources"""
    store_init_resources()


def i_check_equal_number_of_resources(step):
    """Step: the number of resources has not changed"""
    store_final_resources()
    check_init_equals_final()


def i_delete_project_by_name(step, name=None, output_dir=None):
    """Step: I delete the project by name <name>, storing results in
    <output_dir>
    """
    ok_(output_dir is not None and name is not None)
    command = ("bigmler delete --filter=\"name=%s\" "  % name +
               " --output-dir " + output_dir +
               " --resource-types project")
    shell_execute(command, os.path.join(output_dir, "p.csv"), test=None)
