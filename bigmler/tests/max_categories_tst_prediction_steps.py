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

from bigml.api import check_resource

from bigmler.tests.common_steps import shell_execute
from bigmler.tests.world import world, res_filename, ok_


def i_create_all_mc_resources_from_dataset_with_model_fields(
    step, max_categories=None, objective=None, model_fields=None,
    test=None, output=None):
    """Step: I create BigML resources with <max_categories> as categories limit
    and <objective> as objective field and model fields <model_fields> using
    dataset to test <test> and log predictions in <output>"""
    ok_(max_categories is not None and test is not None and output is not None
        and model_fields is not None)
    command = ("bigmler --dataset " + world.dataset['resource'] +
               " --max-categories " + max_categories + " --objective " +
               objective + " --test " + test + " --store --output " +
               output + " --model-fields \"" + model_fields + "\"")
    shell_execute(command, output, test=test)


def i_create_all_mc_resources(
    step, data, max_categories=None, objective=None, test=None, output=None):
    """Step: I create BigML resources from <data> with <max_categories> as
    categories limit and <objective> as objective field to test <test> and log
    predictions in <output>
    """
    ok_(max_categories is not None and test is not None and output is not None
        and objective is not None)
    test = res_filename(test)
    command = ("bigmler --train " + res_filename(data) + " --max-categories " +
               max_categories + " --objective " + objective + " --test " +
               test + " --store --output " + output)
    shell_execute(command, output, test=test)


def i_create_all_mc_resources_from_source(
    step, max_categories=None, objective=None, test=None, output=None):
    """Step: I create BigML resources with <max_categories> as categories
    limit and <objective> as objective field using source to test <test> and
    log predictions in <output>
    """
    ok_(max_categories is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --source " + world.source['resource'] +
               " --max-categories " + max_categories +  " --objective " +
               objective + " --test " + test + " --store --output " +
               output)
    shell_execute(command, output, test=test)


def i_create_all_mc_resources_from_dataset(
    step, max_categories=None, objective=None, test=None, output=None):
    """Step: I create BigML resources with <max_categories> as categories limit
    and <objective> as objective field using dataset to test <test> and
    log predictions in <output>
    """
    ok_(max_categories is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --dataset " + world.dataset['resource'] +
               " --max-categories " + max_categories + " --objective " +
               objective + " --test " + test + " --store --output " +
               output)
    shell_execute(command, output, test=test)


def i_create_all_mc_resources_from_models(
    step, models_file=None, test=None, output=None):
    """Step: I create BigML resources using models in file <models_file> to
    test <test> and log predictions with combine method in <output>
    """
    ok_(models_file is not None and test is not None and output is not None)
    test = res_filename(test)
    command = ("bigmler --models " + models_file +
               " --method combined --test " + test + " --store --output "
               + output)
    shell_execute(command, output, test=test)


def i_check_create_max_categories_datasets(step):
    """Step: I check that the max_categories datasets have been created"""
    dataset_file = os.path.join(world.directory, "dataset_parts")
    message = None
    #pylint: disable=locally-disabled,import-outside-toplevel
    try:
        with open(dataset_file) as handler:
            number_of_datasets = 0
            for line in handler:
                dataset_id = line.strip()
                dataset = check_resource(dataset_id,
                                         world.api.get_dataset)
                ok_('user_metadata' in dataset['object'] and 'max_categories'
                    in dataset['object']['user_metadata'])
                world.datasets.append(dataset['resource'])
                number_of_datasets += 1
        world.number_of_models = number_of_datasets
    except Exception:
        import traceback
        message = traceback.format_exc()
    ok_(message is None, msg=message)
