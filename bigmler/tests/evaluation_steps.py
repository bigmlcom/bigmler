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

try:
    import simplejson as json
except ImportError:
    import json

from bigml.api import check_resource

from bigmler.tests.common_steps import shell_execute
from bigmler.tests.world import world, res_filename, ok_, eq_


def given_i_create_bigml_resources_using_source_to_evaluate(
    step, output=None):
    """Step: I create BigML resources using source to evaluate and log
    evaluation in <output>
    """
    ok_(output is not None)
    command = ("bigmler --evaluate --source " + world.source['resource'] +
               " --output " + output)
    shell_execute(command, output)


def read_id_from_file(path):
    """Reading the id in first line in a file

    """
    with open(path) as id_file:
        return id_file.readline().strip()


def given_i_create_bigml_resources_using_dataset_to_evaluate(
    step, output=None):
    """Creating a default evaluation from dataset"""
    ok_(output is not None)
    command = ("bigmler --evaluate --dataset " + world.dataset['resource'] +
               " --output " + output)
    shell_execute(command, output)


def i_create_all_resources_to_evaluate_with_model_and_map(
    step, data=None, fields_map=None, output=None):
    """Step: I create BigML resources using test file <data> and a fields
    map <fields_map> to evaluate a model and log evaluation in <output>
    """
    ok_(data is not None and fields_map is not None and output is not None)
    command = ("bigmler --evaluate --test " + res_filename(data) +
               " --model " +
               world.model['resource'] + " --output " + output +
               " --fields-map " + res_filename(fields_map))
    shell_execute(command, output)


def i_create_all_resources_to_evaluate_with_model(
    step, data=None, output=None):
    """Step: I create BigML resources using test file <data> to evaluate
    a model and log evaluation in <output>
    """
    ok_(data is not None and output is not None)
    command = ("bigmler --evaluate --test " + res_filename(data) +
               " --model " +
               world.model['resource'] + " --output " + output)
    shell_execute(command, output)


def given_i_create_bigml_resources_using_dataset_to_evaluate_with_model(
    step, output=None):
    """Step: I create BigML resources using a dataset to evaluate a
    model and log evaluation in <output>
    """
    ok_(output is not None)
    command = ("bigmler --evaluate --dataset " +
               world.dataset['resource']  + " --model " +
               world.model['resource'] + " --output " + output)
    shell_execute(command, output)


def i_create_with_split_to_evaluate(step, data=None, split=None, output=None):
    """Step: I create BigML resources uploading train <data> file to evaluate
    with test-split <split> and log evaluation in <output>
    """
    ok_(data is not None and split is not None and output is not None)
    command = ("bigmler --evaluate --train " + res_filename(data) +
               " --test-split " + split +  " --output " + output)
    shell_execute(command, output)


def i_create_proportional_to_evaluate(step, test=None):
    """Step: I evaluate <test> with proportional missing strategy"""
    ok_(test is not None)
    test = res_filename(test)
    output_dir = world.directory + "_eval/"
    output = output_dir + os.path.basename(world.output)
    command = ("bigmler --evaluate --model " +
               world.model['resource'] +
               " --test " + test +
               " --missing-strategy proportional --output " +
               output)
    shell_execute(command, output)


def then_the_evaluation_file_is_like(step, check_file_json):
    """Step: the evaluation file is like <check_file_json>"""
    check_file_path = res_filename(check_file_json)
    evaluation_file_json = world.output + ".json"
    try:
        with open(evaluation_file_json) as eval_handler:
            with open(check_file_path) as check_handler:
                check = check_handler.readline()
                evaluation = eval_handler.readline()
                check = json.loads(check)
                evaluation = json.loads(evaluation)
        if 'model' in check:
            for metric, value in check['model'].items():
                if not isinstance(value, list) and not isinstance(value, dict):
                    eq_(check['model'][metric], evaluation['model'][metric],
                        msg=f"model {metric}")
                    eq_(check['mode'][metric], evaluation['mode'][metric],
                        msg=f"mode {metric}")
        else:
            del check["datasets"]
            del evaluation["datasets"]
            eq_(check, evaluation)
    except Exception as exc:
        with open("%s.new" % check_file_path, "w") as eval_handler:
            json.dump(evaluation, eval_handler)
        ok_(False, msg=str(exc))


def i_check_create_dataset(step, dataset_type=None):
    """Step: I check that the <dataset_type> dataset has been created"""
    dataset_file = os.path.join(world.directory, "dataset_%s" % dataset_type)
    try:
        with open(dataset_file) as handler:
            dataset = check_resource(handler.readline().strip(),
                                     world.api.get_dataset)
        world.datasets.append(dataset['resource'])
        world.dataset = dataset
    except Exception as exc:
        ok_(False, msg=str(exc))


def i_check_evaluation_key(step, key=None, value=None):
    """Step: the evaluation key <key> value for the model is greater than
    <value>
    """
    evaluation_file_json = world.output + ".json"
    try:
        with open(evaluation_file_json) as handler:
            evaluation = handler.readline()
            evaluation = json.loads(evaluation)
            model_evaluation = evaluation['model']
            ok_(model_evaluation[key] > float(value),
                "model key: %s, expected >: %s" % ( \
                model_evaluation[key], float(value)))
    except Exception as exc:
        ok_(False, msg=str(exc))


def i_create_with_split_to_evaluate_ensemble(
    step, data=None, number_of_models=None, split=None, output=None):
    """Step: I create BigML resources uploading train <data> file to evaluate
    an ensemble of <number_of_models> models with test-split <split> and log
    evaluation in <output>
    """
    ok_(data is not None and split is not None and output is not None)
    command = ("bigmler --evaluate --train " + res_filename(data) +
               " --test-split " + split +
               " --number-of-models " + number_of_models +
               " --output " + output)
    shell_execute(command, output)


def i_evaluate_ensemble_with_dataset(
    step, ensemble_dir=None, dataset_dir=None, output=None):
    """Step: I evaluate the ensemble in directory <ensemble_dir> with the
    dataset in directory <dataset_dir> and log evaluation in <output>
    """
    ok_(ensemble_dir is not None and dataset_dir is not None and
        output is not None)
    ensemble_id = read_id_from_file(os.path.join(ensemble_dir, "ensembles"))
    dataset_id = read_id_from_file(os.path.join(dataset_dir, "dataset_test"))
    command = ("bigmler --dataset " + dataset_id +
               " --ensemble " + ensemble_id + " --store" +
               " --output " + output + " --evaluate")
    shell_execute(command, output)


def i_evaluate_ensemble_with_dataset_and_options( \
    step, ensemble_dir=None, dataset_dir=None, output=None, options=None):
    """Step: I evaluate the ensemble in directory <ensemble_dir> with the
    dataset in directory <dataset_dir> and log evaluation in <output>
    """
    ok_(ensemble_dir is not None and dataset_dir is not None and
        output is not None and options is not None)
    ensemble_id = read_id_from_file(os.path.join(ensemble_dir, "ensembles"))
    dataset_id = read_id_from_file(os.path.join(dataset_dir, "dataset_test"))
    command = ("bigmler --dataset " + dataset_id +
               " --ensemble " + ensemble_id + " --store" +
               " --output " + output + " --evaluate " + options)
    shell_execute(command, output)
